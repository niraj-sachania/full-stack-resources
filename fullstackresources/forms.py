from django import forms
from django.core.exceptions import ValidationError
from django_summernote.widgets import SummernoteWidget
from .models import Resource


class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ('title', 'link', 'description')
        widgets = {
            "description": SummernoteWidget(),
        }

    def clean_title(self):
        title = self.cleaned_data.get("title", "").strip()
        if not title:
            return title

        qs = Resource.objects.filter(title__iexact=title)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("A resource with this title already exists.")
        return title
