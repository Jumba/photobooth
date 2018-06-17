from django.db import models


class Event(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateField()


class Photo(models.Model):
    event = models.ForeignKey(Event, related_name='photos')

    filename = models.CharField(max_length=255, db_index=True)

    path_raw = models.CharField(max_length=255)
    path_scaled = models.CharField(max_length=255)
    path_thumb = models.CharField(max_length=155)

    uploaded_at = models.DateTimeField(auto_now_add=True)


