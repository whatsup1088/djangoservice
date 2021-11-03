from django.db import models

# Create your models here.
class Channel(models.Model):

    channel_id = models.CharField(max_length=50)
    channel_type = models.CharField(max_length=10)
    channel_name = models.CharField(max_length=20)

    def __str__(self):
        return self.name
