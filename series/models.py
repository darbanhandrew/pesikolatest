from django.db import models

# Create your models here.
from djrichtextfield.models import RichTextField

from base.models import BaseModel, File, Category, Image, Profile
from shop.models import Product
from sort_order_field import SortOrderField


class Serial(BaseModel):
    categories = models.ManyToManyField(Category, blank=True, null=True)
    is_freemium = models.BooleanField(default=False)
    product = models.OneToOneField(Product, models.CASCADE, blank=True, null=True)
    images = models.ManyToManyField(Image, through='SerialImage')
    is_active = models.BooleanField(default=True)
    content = RichTextField()
    subscribers = models.ManyToManyField(Profile, related_name='serial_subscribers', blank=True, null=True)


class Episode(BaseModel):
    is_freemium = models.BooleanField(default=False)
    video_file = models.OneToOneField(File, on_delete=models.CASCADE, blank=True, null=True)
    duration_seconds = models.IntegerField(blank=True, null=True)
    categories = models.ManyToManyField(Category, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    serial = models.ForeignKey(Serial, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        ordering = ('order',)

    order = SortOrderField("Sort")


class SerialImage(models.Model):
    class Meta:
        ordering = ('order',)

    serial = models.ForeignKey(Serial, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    is_featured = models.BooleanField(default=False)
    order = SortOrderField("Sort")
