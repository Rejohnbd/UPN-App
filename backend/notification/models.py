from django.db import models

# Create your models here.
class Notification(models.Model):
    # Fields
    date = models.DateField()
    time = models.TimeField()
    image = models.ImageField(upload_to='notifications/')

    def __str__(self):
        return f"Notification on {self.date} at {self.time}"


class NotificationSetting(models.Model):
    # A number field for the interval
    interval = models.IntegerField(help_text="Interval in minutes")

    def __str__(self):
        return f"Notification Interval: {self.interval} minutes"