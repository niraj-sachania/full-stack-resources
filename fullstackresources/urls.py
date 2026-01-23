from . import views
from django.urls import path

urlpatterns = [
    path('', views.ResourceList.as_view(), name='home'),
    # path('<slug:slug>/', views.resource_detail, name='resource_detail'),
    #     path('<slug:slug>/edit_resource/<int:resource_id>',
    #          views.resource_edit, name='resource_edit'),
    #     path('<slug:slug>/delete_resource/<int:resource_id>',
    #          views.resource_delete, name='resource_delete'),
]
