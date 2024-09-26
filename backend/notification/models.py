from django.db import models
from django.utils import timezone

# Create your models here.
class Notification(models.Model):
    # Fields
    date = models.DateField()
    time = models.TimeField()
    image = models.ImageField(upload_to='notifications/')
    created_at = models.DateTimeField(default=timezone.now, editable=False) 

    def __str__(self):
        return f"Notification on {self.date} at {self.time}"


class NotificationSetting(models.Model):
    # A number field for the interval
    interval = models.IntegerField(help_text="Interval in minutes")

    def __str__(self):
        return f"Notification Interval: {self.interval} minutes"