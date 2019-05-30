from django.contrib import admin
from assets.models import Category, Zone, Location, Department, Status, Equipment, Action

# Register your models here.

class EquipmentAdmin(admin.ModelAdmin):
    fields = ['name', 'asset_cat', ('brand', 'model'), ('service_tag', 'serial'),
              ('ip_config', 'ip_address'), 'os', 'ram', 'hd', 'pro', ('bios',
              'firm'), 'ports', ('ext', 'phone_num'), ('p_date', 'cost')]

admin.site.register(Category)
admin.site.register(Zone)
admin.site.register(Location)
admin.site.register(Department)
admin.site.register(Status)
admin.site.register(Equipment, EquipmentAdmin)
