from django.db import models

# Create your models here.
from djrichtextfield.models import RichTextField

from base.models import BaseModel, File, Category, Image, Profile
from shop.models import Product
from sort_order_field import SortOrderField


class Podcast(BaseModel):
    categories = models.ManyToManyField(Category, blank=True, null=True)
    is_freemium = models.BooleanField(default=False)
    product = models.OneToOneField(Product, models.CASCADE, blank=True, null=True)
    images = models.ManyToManyField(Image, through='PodcastImage')
    is_active = models.BooleanField(default=True)
    content = RichTextField()
    subscribers = models.ManyToManyField(Profile, related_name='subscribers', blank=True, null=True)


class Track(BaseModel):
    is_freemium = models.BooleanField(default=False)
    audio_file = models.OneToOneField(File, on_delete=models.CASCADE, blank=True, null=True)
    duration_seconds = models.IntegerField(blank=True, null=True)
    categories = models.ManyToManyField(Category, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        ordering = ('order',)

    order = SortOrderField("Sort")


class PodcastImage(models.Model):
    class Meta:
        ordering = ('order',)

    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    is_featured = models.BooleanField(default=False)
    order = SortOrderField("Sort")
