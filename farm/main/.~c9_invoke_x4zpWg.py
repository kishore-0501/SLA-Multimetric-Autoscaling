from django.db import models
from django.contrib.auth.models import User

class Crop(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)  # link crop to seller
    crop_name = models.CharField(max_length=100)
    crop_type = models.CharField(max_length=100)
    quantity = models.IntegerField()
    price_per_unit = models.FloatField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.crop_name} ({self.owner.first_name})"
