from . import views
from django.urls import path

urlpatterns = [
    path('', views.ResourceList.as_view(), name='home'),
    path('resource/<slug:slug>/edit/',
         views.resource_edit, name='resource_edit'),
    path('resource/<slug:slug>/delete/',
         views.resource_delete, name='resource_delete'),
]
