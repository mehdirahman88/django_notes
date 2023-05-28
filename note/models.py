from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User


class Note(models.Model):
    title = models.CharField(max_length=150)
    content = models.TextField(null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='note')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(default=timezone.now)

    def get_absolute_url(self):
        return reverse('note:single', args=[self.pk])

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.title
