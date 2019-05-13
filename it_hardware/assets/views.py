from django.shortcuts import render, redirect
from assets.models import Category, Location, Department, Equipment, Action, Zone
from django.contrib.messages.views import SuccessMessageMixin
from django.views import generic
from django.urls import reverse
from django.urls import reverse_lazy
from assets.forms import ServiceForm, LocationCheckForm


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

        return context

class EquipmentEditView(generic.UpdateView):
    model = Equipment
    fields = ['asset_loc', 'i_date', 'state', 'ip_config','ip_address','os',
              'ram', 'hd', 'bios','firm', 'ext']
    template_name = 'equipment_edit.html'

    def get_success_url(self, *args, **kwargs):
        return reverse('equipment-detail', kwargs={'pk': self.kwargs.get('pk')})

class EquipmentServiceView(generic.CreateView):
    template_name = 'equipment_service.html'
    form_class = ServiceForm
    queryset = Action.objects.all()


class LocationCheckView(generic.FormView):
    form_class = LocationCheckForm
    template_name = 'location_check.html'
    success_url = '/quickcheck/'

    def form_valid(self, form):
        return super().form_valid(form)

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

