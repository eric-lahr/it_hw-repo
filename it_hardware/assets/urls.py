from django.urls import path
from . import views

urlpatterns = [
        path('', views.index, name='index'),
        path('zones/', views.ZoneListView.as_view(), name='zones'),
        path('zone/<int:pk>',views.ZoneDetailView.as_view(), name='zone-detail'),
        path('location/<int:pk>',views.LocationDetailView.as_view(), name='location-detail'),
        path('quickcheck/', views.LocationCheckView.as_view(), name='location-check'),
        path('quickmove/', views.QuickMoveView.as_view(), name='quick-move'),
        path('categories/', views.CategoryListView.as_view(), name='categories'),
        path('category/<int:pk>',views.CategoryDetailView.as_view(), name='category-detail'),
        path('incident/<int:pk>', views.IncidentDetailView.as_view(), name='incident-detail'),
        path('equipment/<int:pk>', views.EquipmentDetailView.as_view(), name='equipment-detail'),
        path('equipment/<int:equipment_pk>/service/', views.EquipmentServiceView.as_view(), name='service-create'),
        path('equipment/<int:pk>/edit/', views.EquipmentEditView.as_view(), name='equipment-edit'),
        path('storage/', views.StorageListView.as_view(), name='storage'),
]





#        path('equipment/<int:pk>/service/', views.EquipmentServiceView.as_view(), name='equipment-service'),




#        path('create/', views.EquipmentCreateView.as_view(), name='equipment-create'),
#        path('', views.EquipmentInfoView, name='base_equipment'),
