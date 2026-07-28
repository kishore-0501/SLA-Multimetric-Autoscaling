from django.db import models
from django.contrib.auth.models import User

# UserProfile for role
ROLE_CHOICES = (
    ('buyer', 'Buyer'),
    ('seller', 'Seller'),
)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    
    # ✅ Added saved/favorite crops for buyers
    saved_crops = models.ManyToManyField('Crop', blank=True, related_name='saved_by')

    def __str__(self):
        return f"{self.user.first_name} ({self.role})"


# Crop Model
class Crop(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    crop_name = models.CharField(max_length=100)
    crop_type = models.CharField(max_length=100)
    quantity = models.IntegerField()
    price_per_unit = models.FloatField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sold = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.crop_name} ({self.owner.first_name})"


# Order Model
class Order(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.crop.crop_name}"
 
        
class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}"


