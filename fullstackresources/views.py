from django.shortcuts import render, get_object_or_404, reverse
from django.views import generic
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Resource
from .forms import ResourceForm

# Create your views here.


class ResourceList(generic.ListView):
    queryset = Resource.objects.filter(approved=1).order_by("-created_at")
    template_name = "index.html"
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        approved_resources = Resource.objects.filter(approved=1)
        context["resource_count"] = approved_resources.count()
        context["contributor_count"] = approved_resources.values(
            "username").distinct().count()
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

        self.object_list = self.get_queryset()
        context = self.get_context_data()
        context["resource_form"] = resource_form
        return self.render_to_response(context)


@login_required
def resource_edit(request, slug):
    resource = get_object_or_404(Resource, slug=slug)

    if resource.username != request.user:
        messages.add_message(
            request, messages.ERROR,
            "You can only edit your own resources."
        )
        return HttpResponseRedirect(reverse("home"))

    if request.method == "POST":
        resource_form = ResourceForm(data=request.POST, instance=resource)
        if resource_form.is_valid():
            resource = resource_form.save(commit=False)
            resource.username = request.user
            resource.save()
            messages.add_message(
                request, messages.SUCCESS, "Resource updated!"
            )
            return HttpResponseRedirect(reverse("home"))
    else:
        resource_form = ResourceForm(instance=resource)

    return render(
        request,
        "resource_edit.html",
        {"resource_form": resource_form, "resource": resource},
    )


@login_required
@require_POST
def resource_delete(request, slug):
    resource = get_object_or_404(Resource, slug=slug)

    if resource.username != request.user:
        messages.add_message(
            request, messages.ERROR,
            "You can only delete your own resources."
        )
        return HttpResponseRedirect(reverse("home"))

    resource.delete()
    messages.add_message(request, messages.SUCCESS, "Resource deleted!")
    return HttpResponseRedirect(reverse("home"))
