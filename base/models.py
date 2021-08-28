from random import randint

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from djrichtextfield.models import RichTextField
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from base.smshelper import otp_send


def random_with_N_digits():
    n = settings.OTP_NUMBER_OF_DIGITS
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    return str(randint(range_start, range_end))


# Create your models hec
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=settings.ACTIVE_ROLES, default=settings.ACTIVE_ROLES[0])
    status = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.phone_number


class OTP(models.Model):
    message = models.CharField(max_length=7, default=random_with_N_digits, blank=True, null=True)
    is_valid = models.BooleanField(default=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
        profile.phone_number = instance.username
        profile.save()


@receiver(post_save, sender=Profile)
def create_profile_otp(sender, instance, created, **kwargs):
    if created:
        otp_s = OTP.objects.create(profile=instance)
        otp_s.save()
        # wallet = Wallet.objects.create(related_profile=instance, amount=0)
        # wallet.save()
        instance.save()


@receiver(post_save, sender=OTP)
def send_otp(sender, instance, created, **kwargs):
    if created:
        phone_number = instance.profile.user.username
        otp_send(phone_number, instance.message)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class BaseModel(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(max_length=10000, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(Profile, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        abstract = True

    # def __str__(self):
    #     return self.title


class Image(BaseModel):
    image = models.ImageField()
    alt_text = models.TextField(max_length=1000, blank=True, null=True)


class File(BaseModel):
    file = models.FileField()


class Category(BaseModel, MPTTModel):
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    image = models.ForeignKey(Image, blank=True, null=True, on_delete=models.CASCADE)


class Post(BaseModel):
    categories = models.ManyToManyField(Category)
    images = models.ManyToManyField(Image)
    Files = models.ManyToManyField(File)
    content = RichTextField()
