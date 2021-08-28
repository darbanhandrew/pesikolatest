from django.db import models

# Create your models here.
from base.models import Profile
from podcast.models import Podcast
from shop.models import Order


class Subscription(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    starts_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True)


class PodcastSubscription(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE)
