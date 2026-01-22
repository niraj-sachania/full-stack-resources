from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import Resource


@admin.register(Resource)
class PostAdmin(SummernoteModelAdmin):

    list_display = ('title', 'slug', 'approved', 'created_at', 'username')
    search_fields = ['title', 'description']
    list_filter = ('approved', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    summernote_fields = ('description',)


# Register your models here.
