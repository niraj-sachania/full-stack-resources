from django.db import models
from django.contrib.auth.models import User


class Resource(models.Model):
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    link = models.CharField(max_length=2000, unique=True)
    username = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="resources")
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} | by {self.username}"
