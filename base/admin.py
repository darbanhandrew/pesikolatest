from django.contrib import admin
from django.apps import apps
from mptt.admin import MPTTModelAdmin
from graphql_jwt.refresh_token.models import RefreshToken
from payir.models import Transaction, Gateway

from podcast.models import Podcast, Track
from .models import Category

admin.site.register(Category)


class PodcastTrackInine(admin.TabularInline):
    model = Track


@admin.register(Podcast)
class PodcastAdmin(admin.ModelAdmin):
    inlines = (PodcastTrackInine,)
    pass


models = apps.get_models()

for model in models:
    if model == RefreshToken:
        continue
    if model == Category or model == Transaction or model == Gateway:
        continue
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
