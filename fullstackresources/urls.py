from . import views
from django.urls import path

urlpatterns = [
    path('', views.ResourceList.as_view(), name='home'),
]
