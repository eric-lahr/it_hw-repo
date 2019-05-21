from django.shortcuts import render, redirect
from assets.models import Category, Location, Department, Equipment, Action, Zone, Status
#from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.views import generic
from django.urls import reverse
from django.urls import reverse_lazy
from assets.forms import ServiceForm, LocationCheckForm, EditForm
from django.shortcuts import get_object_or_404
import socket


# Create your views here.

def index(request):
    tot_pcs = Equipment.objects.filter(asset_cat__asset_cat='PC').count()
    tot_prn = Equipment.objects.filter(asset_cat__asset_cat='Printer').count()
    tot_phn = Equipment.objects.filter(asset_cat__asset_cat='Phone').count()
    tot_mon = Equipment.objects.filter(asset_cat__asset_cat='Monitor').count()
    context = {
            'tot_pcs': tot_pcs,
            'tot_prn': tot_prn,
            'tot_phn': tot_phn,
            'tot_mon': tot_mon,
}

    return render(request, 'index.html', context=context)

class ZoneListView(generic.ListView):
    context_object_name = 'zone_list'
    queryset = Zone.objects.all().exclude(zone_loc='storage')
    template_name = 'zone_list.html'

class ZoneDetailView(generic.DetailView):
    model = Zone
    template_name = 'zone_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ZoneDetailView,self).get_context_data(**kwargs)
        context['loc_num'] = Location.objects.filter(zone_loc=self.object).count()
        context['loc_list'] = Location.objects.filter(zone_loc=self.object)
        return context

class LocationDetailView(generic.DetailView):
    model = Location
    template_name = 'location_detail.html'

    def get_context_data(self, **kwargs):
        context = super(LocationDetailView,self).get_context_data(**kwargs)
        context['loc_tot'] = Equipment.objects.filter(asset_loc=self.object).count()
        context['loc_eq'] = Equipment.objects.filter(asset_loc=self.object)
        return context

class CategoryListView(generic.ListView):
    context_object_name = 'category_list'
    queryset = Category.objects.all()
    template_name = 'category_list.html'

class CategoryDetailView(generic.DetailView):
    model = Category
    template_name = 'category_detail.html'

    def get_context_data(self, **kwargs):
        context = super(CategoryDetailView,self).get_context_data(**kwargs)
        context['cat_tot'] = Equipment.objects.filter(asset_cat=self.object).count()
        context['cat_eq'] = Equipment.objects.filter(asset_cat=self.object)
        return context

class EquipmentDetailView(generic.DetailView):
    model = Equipment
    template_name = 'equipment_detail.html'

    def get_context_data(self, **kwargs):
        context = super(EquipmentDetailView, self).get_context_data(**kwargs)
        context['equipment_history'] = Action.objects.filter(name=self.object).order_by('dt').reverse()
        return context


class EquipmentEditView(generic.UpdateView):
    form_class = EditForm
    template_name = 'equipment_edit.html'
    queryset = Equipment.objects.all()

    def form_valid(self, form):
        self.object = form.save(commit=False)
        changes = self.object.tracker.changed()
        for key, value in changes.items():
            k = str(key)
            v = str(value)
            n = str(self.object.name)
            if k == 'ip_address':
                y = str(self.object.ip_address)

                if y == '' and v == 'None':
                    pass
                else:
                    Action.objects.create(name=self.object, act='CHANGE',
                        act_detail='{} ip address changed from {} to {}.'.format(
                            n, v, y
                        ), incident = '')

            if k == 'state_id':
                new_state = self.object.state
                old_state = Status.objects.get(pk=v)
                current_loc = self.object.asset_loc
                if str(old_state) == 'deployed':

                    if str(current_loc) != 'storage':
                        self.object.state = old_state
                        self.object.save()
                        loc_message = """{} is not in storage. You must change
                        the location of {} to storage if you want to change it's
                        status from 'deployed'.""".format(n, n)
                        messages.add_message(self.request, messages.ERROR, loc_message)
                    else:
                        Action.objects.create(name=self.object, act='CHANGE',
                        act_detail='Status changed from {} to {}.'.format(
                            str(old_state), str(new_state)
                            ), incident = '')
                    
                elif str(new_state) == 'deployed':

                    if str(current_loc) =='storage':
                        self.object.state = old_state
                        self.object.save()
                        loc_message = """{} is in storage. To change it's status to
                        'deployed', move it out of the storage location.""".format(n)
                        messages.add_message(self.request, messages.ERROR, loc_message)
                    else:
                        Action.objects.create(name=self.object, act='CHANGE',
                        act_detail='Status changed from {} to {}.'.format(
                            str(old_state), str(new_state)
                            ), incident = '')

                elif str(new_state) == 'stored':

                    if str(current_loc) != 'storage':
                        self.object.state = old_state
                        self.object.save()
                        loc_message = """{} is not in the storage location. Move {} to
                        the storage location to change it's status to
                        'stored'.""".format(n, n)
                        messages.add_message(self.request, messages.ERROR, loc_message)
                    else:
                        Action.objects.create(name=self.object, act='CHANGE',
                        act_detail='Status changed from {} to {}.'.format(
                            str(old_state), str(new_state)
                            ), incident = '')

                else:

                    Action.objects.create(name=self.object, act='CHANGE',
                        act_detail='Status changed from {} to {}.'.format(
                            str(old_state), str(new_state)
                            ), incident = '')


            if k == 'ip_config':
                new_config = self.object.ip_config
                Action.objects.create(name=self.object, act='CHANGE',
                    act_detail='IP configuration changed from {} to {}.'.format(
                        v, str(new_config)
                    ), incident = '')

            if k == 'os':
                new_os = self.object.os
                Action.objects.create(name=self.object, act='CHANGE',
                    act_detail='Operating system changed from {} to {}.'.format(
                        v, str(new_os)
                    ), incident = '')

            if k == 'ram':
                new_ram = self.object.ram
                Action.objects.create(name=self.object, act='CHANGE',
                    act_detail='Amount of system RAM changed from {} to {}.'.format(
                        v, str(new_ram)
                    ), incident = '')

            if k == 'hd':
                new_hd = self.object.hd
                Action.objects.create(name=self.object, act='CHANGE',
                    act_detail='Hard drive changed from {} to {}.'.format(
                        v, str(new_hd)
                    ), incident = '')

            if k == 'bios':
                new_bios = self.object.bios
                Action.objects.create(name=self.object, act='CHANGE',
                    act_detail='System BIOS version changed from {} to {}.'.format(
                        v, str(new_bios)
                    ), incident = '')

            if k == 'firm':
                new_firm = self.object.firm
                Action.objects.create(name=self.object, act='CHANGE',
                    act_detail='Firmware version changed from {} to {}.'.format(
                        v, str(new_firm)
                    ), incident = '')

            if k == 'ext':
                new_ext = self.object.ext
                Action.objects.create(name=self.object, act='CHANGE',
                    act_detail='Extension changed from {} to {}.'.format(
                        v, str(new_ext)
                    ))

            if k == 'asset_loc_id':
                new_loc = self.object.asset_loc
                old_loc = Location.objects.get(pk=v)
                conflict = Equipment.objects.filter(asset_loc=new_loc,
                    asset_cat=self.object.asset_cat)
                conflict_count = Equipment.objects.filter(asset_loc=new_loc,
                    asset_cat=self.object.asset_cat).count()
                maximum = Category.objects.get(asset_cat=self.object.asset_cat)

                if str(new_loc) == 'storage':
                    self.object.state = 'stored'
                    self.object.save()
                    Action.objects.create(name=self.object, act='CHANGE',
                        act_detail='Status changed from deployed to stored.',
                                          incident = '')

                elif conflict_count == maximum.max_allowed:
                    
                    if conflict_count > 1:
                        self.object.asset_loc = old_loc
                        self.object.save()
                        loc_message="""There are already too many {}s at {}. 
                        Move one of these to storage before you try this move
                        again.""".format(maximum, new_loc)
                        messages.add_message(self.request, messages.ERROR, loc_message)
                        
                    else:
                        x = str(conflict)
                        Location_id = Location.objects.get(asset_loc='storage')
                        Status_id = Status.objects.get(state='stored')
                        to_storage = Equipment.objects.get(asset_loc=new_loc,
                                asset_cat=self.object.asset_cat)
                        to_storage.asset_loc = Location_id
                        to_storage.state = Status_id
                        to_storage.save()

                        Action.objects.create(name=to_storage.name, act='CHANGE',
                                              act_detail='Location changed from {} to storage.'.format(
                                                  str(new_loc)
                                                  ), incident = '')
                        Action.objects.create(name=to_storage.name, act='CHANGE',
                                              act_detail='Status changed from deployed to stored.',
                                              incident = '')
                        loc_message="""{} was already at {}. Your move was successful
                        but be aware, {} has been moved to storage.""".format(
                                to_storage.name, new_loc, to_storage.name)
                        messages.add_message(self.request, messages.WARNING, loc_message)
        

                Action.objects.create(name=self.object, act='CHANGE',
                                      act_detail='Location changed from {} to {}.'.format(
                                          str(old_loc), str(new_loc)), incident = '')
                

        return super().form_valid(form)


    def get_success_url(self, *args, **kwargs):
#        messages.add_message(request, messages.WARNING, loc_message)
        return reverse('equipment-detail', kwargs={'pk': self.kwargs.get('pk')})


class EquipmentServiceView(generic.CreateView):
    template_name = 'equipment_service.html'
    form_class = ServiceForm
    queryset = Action.objects.all()

    def form_valid(self, form):
        equipment_pk = self.kwargs['equipment_pk']
        equipment = get_object_or_404(Equipment, pk=equipment_pk)
        self.object = form.save(commit=False)
        self.object.name = equipment
        self.object.act = 'SERVICE'
        self.object.save()
        return super().form_valid(form)


class LocationCheckView(generic.FormView):
    form_class = LocationCheckForm
    template_name = 'location_check.html'
    success_url = '/assets/quickcheck/'

    def form_valid(self, form):
        at_location = []
        test = "pass"
        missing = []
        in_system = []
        loc_chk = form.cleaned_data['location']
        eq_chk = (form.cleaned_data['assets'].split('\r\n'))
        all_loc = Location.objects.filter(asset_loc=loc_chk).first()
        eq_at_loc = Equipment.objects.filter(asset_loc=all_loc)

        for i in eq_at_loc:
            in_system.append(str(i))

        for p in eq_chk:
            check = Equipment.objects.filter(name=p).first()

            if not check:
                messages.error(self.request, "{} is not a valid equipment name.".format(p))
            else:
                at_location.append(str(p))

        if not all_loc:
            messages.error(self.request, "{} is not valid location.".format(loc_chk))
            return super(LocationCheckView, self).form_valid(form)
        else:
            for item in at_location:
                if item in in_system:
                    messages.success(self.request, "{} belongs at this location.".format(item))
                else:
                    should_be = Equipment.objects.get(name=item)
                    print(should_be.asset_loc)
                    messages.error(self.request,
                            "{} does not belong here. It should be at {}.".format(item, should_be.asset_loc))

            for item in in_system:
                if item not in at_location:
                    messages.error(self.request,
                        "{} should be at this location but was not in your list.".format(item))
                    missing.append(item)
                    test = "fail"
                else:
                    continue
        if test == "pass":
            messages.success(self.request, "All items that should be at this location are present.")
        else:
            messages.error(self.request, "Items are missing from this location!")

        return super(LocationCheckView, self).form_valid(form)


#def LocationCheckView(request):
#    form = LocationCheckForm
#    template
#    if request.method == 'POST':
#        form = LocationCheckForm(request.POST)


#        if form.is_valid():
#            print(form.cleaned_data)
#            loc_chk = form.cleaned_data['loc_to_check']
#            eq_chk = form.cleaned_data['eq_to_check']
#            locations = Location.objects.filter(asset_loc=loc_chk).first()
#            if not locations:
#                messages.error(request, "{} is not a known location.".format(loc_chk))
#            else:
#                pass
#    return redirect('index')
