from django.db import models
from django.urls import reverse

class Feedback(models.Model):
    Name = models.CharField(null=True, blank=True, max_length=1000)
    Email = models.EmailField(null=True, blank=True)
    Title = models.CharField(max_length=10000)
    Content = models.TextField()


    def __str__(self):
        return self.Title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)