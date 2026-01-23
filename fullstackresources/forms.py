from .models import Resource
from django import forms


class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ('title', 'link', 'description')
