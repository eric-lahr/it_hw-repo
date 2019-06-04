from django.shortcuts import render, redirect
from assets.models import Category, Location, Department, Equipment, Action, Zone, Status
#from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.views import generic
from django.urls import reverse
from django.urls import reverse_lazy
from assets.forms import ServiceForm, LocationCheckForm, EditForm
from django.shortcuts import get_object_or_404
from datetime import datetime
import socket


# Create your views here.

def index(request):
    cat_dict = {}
    zone_dict = {}
    dept_dict = {}
    search_term = ''
    searching = ''
    eq_tot = Equipment.objects.all().count()
    cats = Category.objects.all()
    for cat in cats:
        val = Equipment.objects.filter(asset_cat__asset_cat=cat).count()
        cat_dict[cat] = val

    zones = Zone.objects.all()
    for z in zones:
        tot_count = 0
        if str(z) == 'storage':
            continue
        locs_in_z = Location.objects.filter(zone_loc__zone_loc=z)
        for l in locs_in_z:
            eq_in_loc = Equipment.objects.filter(asset_loc__asset_loc=l).count()
            tot_count += eq_in_loc
        zone_dict[z] = tot_count

    depts = Department.objects.all()
    for d in depts:
        tot_count = 0
        if str(d) == 'none':
            continue
        locs_in_dept = Location.objects.filter(dept__dept=d)
        for lct in locs_in_dept:
            if str(lct) == 'storage':
                continue
            eq_at_loc = Equipment.objects.filter(asset_loc__asset_loc=lct).count()
            tot_count += eq_at_loc
        dept_dict[d] = tot_count
    store_locs = Location.objects.filter(zone_loc__zone_loc='storage')
    store = Equipment.objects.filter(asset_loc__in=store_locs)
    store_count = len(store)
    cat_list = []
    store_dict = {}
    for eq in store:
        cat_list.append(str(eq.asset_cat))
    cats_in_store = set((cat_list))
    for c in cats_in_store:
        cat_count = Equipment.objects.filter(asset_loc__asset_loc='storage',
                                 asset_cat__asset_cat=c).count()
        store_dict[c] = cat_count
    loc_tot = Location.objects.all().count()

    dhcp = Equipment.objects.filter(ip_config='DHCP').exclude(asset_loc__in=store_locs)

    for eq in dhcp:
        ip_name = str(eq) + '.vitacost.com'
        ipaddr = socket.gethostbyname(ip_name)
        t = Equipment.objects.get(name=eq)
        t.ip_address = ipaddr
        t.save()

    if 'search' in request.GET:
        search_term = request.GET['search']
        searching = Equipment.objects.filter(name__icontains=search_term)

    context = {
            'cat_dict': cat_dict,
            'zone_dict': zone_dict,
            'dept_dict': dept_dict,
            'eq_tot': eq_tot,
            'store_dict': store_dict,
            'store_count': store_count,
            'loc_tot': loc_tot,
            'search_term': search_term,
            'searching': searching,
}

    return render(request, 'index.html', context=context)

# class ZoneListView(generic.ListView):
#    context_object_name = 'zone_list'
#    queryset = Zone.objects.all().exclude(zone_loc='storage')
#    template_name = 'zone_list.html'

class ZoneListView(generic.TemplateView):
    template_name = 'zone_list.html'

    def get_context_data(self, *args, **kwargs):
        zone_info = {}
        search_term = ''
        searching = ''
        context = super(ZoneListView, self).get_context_data(*args, **kwargs)
        zones = Zone.objects.all().exclude(zone_loc='storage')
        for z in zones:
            #print(z)
            e_tot = 0
            loc_tot = Location.objects.filter(zone_loc__zone_loc=z)
            #print(loc_tot)
            for l in loc_tot:
                #print(l)
                e = Equipment.objects.filter(asset_loc=l).count()
                #print(e)
                e_tot += e
            loc_tot = loc_tot.count()
            zone_info[z] = [loc_tot, e_tot]

        if 'search' in self.request.GET:
            search_term = self.request.GET['search']
            searching = Equipment.objects.filter(name__icontains=search_term)

        context['zones'] = zones.count()
        context['zone_info'] = zone_info
        context['search_term'] = search_term
        context['searching'] = searching
        return context

class ZoneDetailView(generic.DetailView):
    model = Zone
    template_name = 'zone_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ZoneDetailView,self).get_context_data(**kwargs)
        loc_list = Location.objects.filter(zone_loc=self.object)
        eq_tot = 0
        loc_dict = {}
        for lo in loc_list:
            at_loc = Equipment.objects.filter(asset_loc__asset_loc=lo)
            loc_dict[lo] = at_loc
        print(loc_dict)
        context['loc_num'] = Location.objects.filter(zone_loc=self.object).count()
        context['loc_dict'] = loc_dict
        return context

class LocationDetailView(generic.DetailView):
    model = Location
    template_name = 'location_detail.html'

    def get_context_data(self, **kwargs):
        context = super(LocationDetailView,self).get_context_data(**kwargs)
        context['loc_tot'] = Equipment.objects.filter(asset_loc=self.object).count()
        context['loc_eq'] = Equipment.objects.filter(asset_loc=self.object)
        return context

class CategoryListView(generic.TemplateView):
    template_name = 'category_list.html'

    def get_context_data(self, *args, **kwargs):
        cat_info = {}
        context = super(CategoryListView, self).get_context_data(*args, **kwargs)
        categories = Category.objects.all()
        for c in categories:
            e_tot = Equipment.objects.filter(asset_cat__asset_cat=c).count()
            cat_info[c] = e_tot
        context['cat_info'] = cat_info
        return context

class CategoryDetailView(generic.DetailView):
    model = Category
    template_name = 'category_detail.html'

    def get_context_data(self, **kwargs):
        context = super(CategoryDetailView,self).get_context_data(**kwargs)
        context['cat_tot'] = Equipment.objects.filter(asset_cat=self.object).count()
        context['cat_eq'] = Equipment.objects.filter(asset_cat=self.object)
        context['cat'] = self.object
        return context

class StorageListView(generic.ListView):
    context_object_name = 'storage_list'
    store_zone = Location.objects.filter(zone_loc__zone_loc='storage')
    queryset = Equipment.objects.filter(asset_loc__in=store_zone).order_by('asset_cat')
    template_name = 'storage_list.html'


class EquipmentDetailView(generic.DetailView):
    model = Equipment
    template_name = 'equipment_detail.html'

    def get_context_data(self, **kwargs):
        context = super(EquipmentDetailView, self).get_context_data(**kwargs)
        field_values = {}
        no_value = ['None', 'none', '', ' ']
        remove = []
        if str(self.object.ip_config) == 'DHCP':
            ip_name = str(self.object) + '.vitacost.com'
            context['ip_addr'] = socket.gethostbyname(ip_name)
        loc = Location.objects.get(asset_loc=self.object.asset_loc)
        context['eq_dept'] = loc.dept
        context['equipment_history'] = Action.objects.filter(name=self.object).order_by('dt').reverse()
        context['asset_cat'] = self.object.asset_cat
#        eq_fields = [f.get_attname() for f in Equipment._meta.fields]
        obj_dict = Equipment.objects.filter(pk=self.object.pk).values()[0]
        del obj_dict['asset_cat_id'], obj_dict['id'], obj_dict['asset_loc_id'], obj_dict['state_id'], obj_dict['name']

        for key, value in obj_dict.items():
            if str(value) in no_value:
                remove.append(key)
        for i in remove:
            del obj_dict[i]
        for key, value in obj_dict.items():

            if str(key) == 'ip_config':
                old = str(value)
                del obj_dict['ip_config']
                obj_dict['ip configuration'] = old
            if str(key) == 'ip_address':
                old = str(value)
                del obj_dict['ip_address']
                obj_dict['ip address'] = old
            if str(key) == 'serial':
                old = str(value)
                del obj_dict['serial']
                obj_dict['serial number'] = old
            if str(key) == 'pro':
                old = str(value)
                del obj_dict['pro']
                obj_dict['processor'] = old
            if str(key) == 'firm':
                old = str(value)
                del obj_dict['firm']
                obj_dict['firmware'] = old
            if str(key) == 'ext':
                old = str(value)
                del obj_dict['ext']
                obj_dict['extension'] = old
            if str(key) == 'p_date':
                old = str(value)
                del obj_dict['p_date']
                obj_dict['purchase date'] = old
            if str(key) == 'd_date':
                old = str(value)
                del obj_dict['d_date']
                obj_dict['deployment date'] = old
            if str(key) == 'i_date':
                old = str(value)
                del obj_dict['i_date']
                obj_dict['image date'] = old


        context['obj_dict'] = obj_dict
#        print(obj_dict)
#        print(field_values)
        return context


class EquipmentEditView(generic.UpdateView):
    form_class = EditForm
    template_name = 'equipment_edit.html'
    queryset = Equipment.objects.all()


    def form_valid(self, form):
        self.object = form.save(commit=False)
        img = (self.request.POST['i_date'])
        changes = self.object.tracker.changed()
        #store_zone = Location.objects.filter(zone_loc__zone_loc='storage')
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
                        act_detail='IP address changed from {} to {}.'.format(
                            v, y
                        ), incident = '')

            if k == 'i_date':
                print(v)
                if img != '':
                    new_image = Action.objects.create(name=self.object, act='CHANGE',
                                                      incident = '',
                                                      act_detail='Imaged. Fresh operating system instance applied.')
                    just_created = Action.objects.get(pk=new_image.pk)
                    just_created.dt = self.request.POST['i_date']
                    just_created.save(update_fields=["dt"])


            if k == 'state_id':
                new_state = self.object.state
                old_state = Status.objects.get(pk=v)

                current_loc = self.object.asset_loc
                if str(old_state) == 'deployed':
                    if current_loc not in Location.objects.filter(zone_loc__zone_loc='storage'):
                    #if str(current_loc) != 'storage':
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

                    if current_loc in Location.objects.filter(zone_loc__zone_loc='storage'):
                    #if str(current_loc) =='storage':
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

                    if current_loc not in Location.objects.filter(zone_loc__zone_loc='storage'):
                    #if str(current_loc) != 'storage':
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
                    ), incident = '')

            if k == 'asset_loc_id':
                new_loc = self.object.asset_loc
                old_loc = Location.objects.get(pk=v)
                conflict = Equipment.objects.filter(asset_loc=new_loc,
                    asset_cat=self.object.asset_cat)
                conflict_count = Equipment.objects.filter(asset_loc=new_loc,
                    asset_cat=self.object.asset_cat).count()
                maximum = Category.objects.get(asset_cat=self.object.asset_cat)

                if new_loc in Location.objects.filter(zone_loc__zone_loc='storage'):
                    Status_id = Status.objects.get(state='stored')
                    self.object.state = Status_id
                    self.object.save()
                    if old_loc not in Location.objects.filter(zone_loc__zone_loc='storage'):
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
                        Equipment_id = Equipment.objects.get(name=to_storage.name)

                        Action.objects.create(name=Equipment_id, act='CHANGE',
                                              act_detail='Location changed from {} to storage.'.format(
                                                  str(new_loc)
                                                  ), incident = '')
                        Action.objects.create(name=Equipment_id, act='CHANGE',
                                              act_detail='Status changed from deployed to stored.',
                                              incident = '')
                        loc_message="""{} was already at {}. Your move was successful
                        but be aware, {} has been moved to storage.""".format(
                                to_storage.name, new_loc, to_storage.name)
                        messages.add_message(self.request, messages.WARNING, loc_message)


                Action.objects.create(name=self.object, act='CHANGE',
                                      act_detail='Location changed from {} to {}.'.format(
                                          str(old_loc), str(new_loc)), incident = '')

                #if current_loc in Location.objects.filter(zone_loc__zone_loc='storage'):
                if (
                   str(self.object.state) != 'deployed' and
                   self.object.asset_loc not in Location.objects.filter(zone_loc__zone_loc='storage')
                   ):
                    Status_id = Status.objects.get(state='deployed')
                    self.object.state = Status_id
                    self.object.d_date = datetime.now()
                    self.object.save()
                    Action.objects.create(name=self.object, act='CHANGE',
                                          act_detail='Status changed to deployed.',
                                          incident = '')

                elif (
                    str(self.object.state) == 'deployed' and
                    self.object.asset_loc in Location.objects.filter(zone_loc__zone_loc='storage')
                    ):
                    Status_id = Status.objects.get(state='stored')
                    self.object.state = Status_id
                    self.object.save()
                    Action.objects.create(name=self.object, act='CHANGE',
                                          act_detail='Status changed from deployed to stored.',
                                          incident = '')


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

    def get_success_url(self, *args, **kwargs):
        return reverse('equipment-detail', kwargs={'pk': self.kwargs['equipment_pk']})

class QuickMoveView(generic.FormView):
    form_class = LocationCheckForm
    template_name = 'quick_move.html'
    success_url = '/assets/quickmove/'

    def form_valid(self, form):
        new_loc = form.cleaned_data['location']
        move_eq = (form.cleaned_data['assets'].split('\r\n'))
        valid_loc = Location.objects.filter(asset_loc=new_loc).first()

        if not valid_loc:
            messages.error(self.request, "{} is not a valid location.".format(new_loc))
            return super(QuickMoveView, self).form_valid(form)
        else:
            remove = []
            new_loc_rec = Location.objects.get(asset_loc=new_loc)
            for eq_mv in move_eq:
                valid_eq = Equipment.objects.filter(name=eq_mv).first()
                if not valid_eq:
                    move_message = "{} is not a valid equipment name.".format(eq_mv)
                    messages.add_message(self.request, messages.ERROR, move_message)
                    remove.append(eq_mv)

            for move_try in move_eq:
                if move_try in remove:
                    continue
                move_try_rec = Equipment.objects.get(name=move_try)

                old_loc = str(move_try_rec.asset_loc)
                if old_loc == new_loc:
                    move_message = "{} is already at {}.".format(move_try, new_loc)
                    messages.add_message(self.request, messages.ERROR, move_message)
                    remove.append(move_try)
                else:
                    #Category_id = Category.objects.get(asset_cat=move_try_rec.asset_cat)
                    #Location_id = Location.objects.get(asset_loc=move_try_rec.asset_loc)

                    conflict = Equipment.objects.filter(asset_loc_id=new_loc_rec.id,
                                                        asset_cat_id=move_try_rec.asset_cat_id)
                    conflict_count = conflict.count()
                    #conflict_count = Equipment.objects.filter(asset_loc_id=new_loc_rec.id,
                   #                                          asset_cat_id=move_try_rec.asset_cat_id).count()
                    maximum = Category.objects.get(id=move_try_rec.asset_cat_id)
                    Status_id = Status.objects.get(state='stored')
                    Location_id = Location.objects.get(asset_loc='storage')
                    #Equipment_id = Equipment.objects.get(name=move_try_rec.name)
                    if new_loc in Location.objects.filter(zone_loc__zone_loc='storage'):
                        move_try_rec.state = Status_id
                        move_try_rec.asset_loc = Location_id
                        move_try_rec.save()
                        move_message = "Location changed from {} to {}.".format(
                            old_loc, new_loc)
                        Action.objects.create(name_id=move_try_rec.id, act='CHANGE',
                                              act_detail=move_message, incident = '')
                        display_message = "{} successfully moved from {} to {}.".format(
                            move_try_rec.name, old_loc, new_loc)
                        messages.add_message(self.request, messages.SUCCESS, display_message)

                    elif conflict_count == maximum.max_allowed:

                        if conflict_count > 1:
                            move_message="""There are already too many {}s at {}.
                            Move one of these to storage before you try this move
                            again.""".format(maximum, new_loc)
                            messages.add_message(self.request, messages.ERROR, move_message)

                        else:
                            x = str(conflict)
                            new_loc_rec = Location.objects.get(asset_loc=new_loc)
                            to_storage = Equipment.objects.get(asset_loc_id=new_loc_rec.id,
                                                               asset_cat_id=move_try_rec.asset_cat_id)
                            to_storage.asset_loc = Location_id
                            to_storage.state = Status_id
                            to_storage.save()
                            #Equipment_id = Equipment.objects.get(name=to_storage.name)
                            Action.objects.create(name_id=to_storage.id, act='CHANGE',
                                                  act_detail='Location changed from {} to storage.'.format(
                                                      str(new_loc)),
                                                  incident = '')
                            Action.objects.create(name_id=to_storage.id, act='CHANGE',
                                                  act_detail='Status changed from deployed to stored.',
                                                  incident = '')
                            move_message="""{} was already at {}. Your move was successful
                            but be aware, {} has been moved to storage.""".format(
                                to_storage.name, new_loc, to_storage.name)
                            messages.add_message(self.request, messages.WARNING, move_message)

                            Action.objects.create(name_id=move_try_rec.id,
                                                  act='CHANGE',
                                                  act_detail='Location changed from {} to {}.'.format(
                                                      str(old_loc), str(new_loc)),
                                                  incident = '')
                            move_message = """{} successfully moved from {} to {}.""".format(
                                move_try,str(old_loc),str(new_loc))
                            messages.add_message(self.request, messages.SUCCESS, move_message)
                            if move_try_rec.asset_loc in Location.objects.filter(zone_loc__zone_loc='storage'):
                                move_try_rec.d_date = datetime.now()
                                move_try_rec.save(update_fields=['d_date'])
                            new = Location.objects.get(asset_loc=new_loc)
                            move_try_rec.asset_loc_id = new.id
                            move_try_rec.save(update_fields=["asset_loc"])

                    else:

                        Action.objects.create(name_id=move_try_rec.id,
                                              act='CHANGE',
                                              act_detail='Location changed from {} to {}.'.format(
                                                  str(old_loc), str(new_loc)),
                                              incident = '')
                        move_message = """{} successfully moved from {} to {}.""".format(
                            move_try,str(old_loc),str(new_loc))
                        messages.add_message(self.request, messages.SUCCESS, move_message)
                        new = Location.objects.get(asset_loc=new_loc)
                        move_try_rec.asset_loc_id = new.id
                        move_try_rec.save(update_fields=["asset_loc"])

                    #in Location.objects.filter(zone_loc__zone_loc='storage'):
                    if (
                        str(move_try_rec.state) != 'deployed' and
                        move_try_rec.asset_loc not in Location.objects.filter(zone_loc__zone_loc='storage')
                        ):
                        Status_id = Status.objects.get(state='deployed')
                        move_try_rec.state_id = Status_id
                        move_try_rec.d_date = datetime.now()
                        move_try_rec.save()
                        Action.objects.create(name_id=move_try_rec.id,
                                              act='CHANGE',
                                              act_detail='Status changed to deployed.',
                                              incident = '')

                    elif (
                        str(move_try_rec.state) == 'deployed' and
                        move_try_rec.asset_loc in Location.objects.filter(zone_loc__zone_loc='storage')
                        ):
                        Status_id = Status.objects.get(state='stored')
                        move_try_rec.state_id = Status_id
                        move_try_rec.save()
                        Action.objects.create(name_id=move_try_rec.id,
                                              act='CHANGE',
                                              act_detail='Status changed from deployed to stored.',
                                              incident = '')

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

class IncidentDetailView(generic.DetailView):
    model = Action
    template_name = 'incident_detail.html'

    def get_context_data(self, **kwargs):
        context = super(IncidentDetailView, self).get_context_data(**kwargs)
        context['incident_record'] = Action.objects.filter(id=self.object.id).first()
        return context
