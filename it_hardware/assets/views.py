from django.shortcuts import render, redirect
from assets.models import Category, Location, Department, Equipment, Action, Zone, Status
#from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.views import generic
from django.urls import reverse
from django.urls import reverse_lazy
from assets.forms import ServiceForm, LocationCheckForm, EditForm
from django.shortcuts import get_object_or_404


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
    queryset = Zone.objects.all()
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
        print(changes)
        for key, value in changes.items():
            print(key)
            k = str(key)
            v = str(value)
            n = str(self.object.name)
            if k == 'ip_address':
                y = str(self.object.ip_address)

                if y == '' and v == 'None':
                    print('no ip address change')
                else:
                    print('{} ip address changed from {} to {}.'.format(
                        n, v, y
                    ))
            if k == 'asset_loc_id':
                new_loc = self.object.asset_loc
                old_loc = Location.objects.get(pk=v)
                print('{} location changed from {} to {}.'.format(
                    n, str(old_loc), str(new_loc)
                    ))
            if k == 'state_id':
                new_state = self.object.state
                old_state = Status.objects.get(pk=v)
                print('{} status changed from {} to {}.'.format(
                    n, str(old_state), str(new_state)
                    ))
            if k == 'ip_config':
                new_config = self.object.ip_config
                print('{} IP configuration changed from {} to {}.'.format(
                    n, v, str(new_config)
                    ))
            if k == 'os':
                new_os = self.object.os
                print('{} operating system changed from {} to {}.'.format(
                    n, v, str(new_os)
                    ))
            if k == 'ram':
                new_ram = self.object.ram
                print('{} amount of RAM changed from {} to {}.'.format(
                    n, v, str(new_ram)
                    ))
            if k == 'hd':
                new_hd = self.object.hd
                print('The hard drive on {} changed from {} to {}.'.format(
                    n, v, str(new_hd)
                    ))
            if k == 'bios':
                new_bios = self.object.bios
                print('The BIOS version on {} has changed from {} to {}'.format(
                    n, v, str(new_bios)
                    ))
            if k == 'firm':
                new_firm = self.object.firm
                print('The firmware version for {} changed from {} to {}.'.format(
                    n, v, str(new_firm)
                    ))
            if k == 'ext':
                new_ext = self.object.ext
                print('The extension for {} changed from {} to {}.'.format(
                    n, v, str(new_ext)
                    ))



        return super().form_valid(form)


    def get_success_url(self, *args, **kwargs):
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
