from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from djrichtextfield.models import RichTextField
from payir.models import Transaction

from base.models import BaseModel, Profile


# Create your models here.
class Product(BaseModel):
    price = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    in_stock = models.BooleanField(default=True)
    content = RichTextField()


# class Transaction(models.Model):
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     amount = models.IntegerField()
#     status = models.CharField(max_length=20, choices=settings.TRANSACTION_STATUSES,
#                               default=settings.TRANSACTION_STATUSES[0])
#     transaction_id = models.CharField(max_length=1000, blank=True, null=True)
#     transaction_token = models.CharField(max_length=1000, blank=True, null=True)
#     profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, blank=True, null=True)


class Coupon(models.Model):
    title = models.CharField(max_length=100, default="Coupon")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    amount = models.IntegerField()


class Basket(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_amount = models.IntegerField(default=0)
    products = models.ManyToManyField(Product, blank=True, null=True)
    coupons = models.ManyToManyField(Coupon, blank=True, null=True)
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, blank=True, null=True)
    is_paid = models.BooleanField(default=False)


@receiver(m2m_changed, sender=Basket.products.through)
def update_basket_products(sender, **kwargs):
    action = kwargs.get('action')
    instance = kwargs.get('instance')
    pk_set = kwargs.get('pk_set')
    if pk_set:
        for pk in pk_set:
            if action == 'post_add':
                instance.total_amount += Product.objects.get(pk=pk).price
                # print(Product(pk).price)
            elif action == 'post_remove':
                instance.total_amount -= Product.objects.get(pk=pk).price
                # print(Product(pk).price)
    instance.save()


@receiver(m2m_changed, sender=Basket.coupons.through)
def update_basket_coupons(sender, **kwargs):
    action = kwargs.get('action')
    instance = kwargs.get('instance')
    pk_set = kwargs.get('pk_set')
    if pk_set:
        for pk in pk_set:
            if action == 'post_add':
                instance.total_amount -= Coupon.objects.get(pk=pk).amount
                # print(Product(pk).price)
            elif action == 'post_remove':
                instance.total_amount += Coupon.objects.get(pk=pk).amount
                # print(Product(pk).price)
    instance.save()


class Order(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.SET_NULL, blank=True, null=True)
    transaction = models.OneToOneField(Transaction, on_delete=models.SET_NULL, blank=True, null=True)
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class OrderNote(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    message = models.TextField(max_length=1000, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
