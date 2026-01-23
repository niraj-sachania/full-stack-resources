from django.db import models
from django.contrib.auth.models import User
from django.db.models.functions import Lower
from django.utils.text import slugify


class Resource(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, db_index=True)
    link = models.URLField(max_length=2000, unique=True)
    username = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="resources")
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                Lower("title"),
                name="resource_title_ci_unique",
            )
        ]

    def __str__(self):
        return f"{self.title} | by {self.username}"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)
