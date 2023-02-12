from django.db import models
from django.urls import reverse

class Feedback(models.Model):
    Title = models.CharField(max_length=10000)
    Content = models.TextField()

    def __str__(self):
        return self.Title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)