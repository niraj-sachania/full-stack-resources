from django.shortcuts import render, get_object_or_404, reverse
from django.views import generic
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import Resource
from .forms import ResourceForm

# Create your views here.


class ResourceList(generic.ListView):
    queryset = Resource.objects.filter(approved=1).order_by("created_at")
    template_name = "index.html"
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["resource_form"] = ResourceForm()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.add_message(
                request, messages.ERROR,
                "You must be logged in to submit a resource."
            )
            return HttpResponseRedirect(reverse("home"))

        resource_form = ResourceForm(data=request.POST)
        if resource_form.is_valid():
            resource = resource_form.save(commit=False)
            resource.username = request.user
            resource.save()
            messages.add_message(
                request, messages.SUCCESS,
                "Resource submitted and awaiting approval."
            )
            return HttpResponseRedirect(reverse("home"))

        context = self.get_context_data()
        context["resource_form"] = resource_form
        return self.render_to_response(context)
