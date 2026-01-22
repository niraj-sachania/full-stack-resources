from django.shortcuts import render
from django.views import generic
from .models import Resource

# Create your views here.


class ResourceList(generic.ListView):
    queryset = Resource.objects.filter(approved=1).order_by("created_at")
    template_name = "index.html"
    paginate_by = 6
