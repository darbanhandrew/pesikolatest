import graphene
from django_filters import OrderingFilter
from graphene import relay, ObjectType, String
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .models import *


class TrackNode(DjangoObjectType):
    has_access = graphene.Boolean()

    def resolve_has_access(self, info):
        is_registered = Podcast.objects.filter(pk=self.podcast.id, subscribers__in=[info.context.user.profile]).exists()
        if self.is_freemium:
            return True
        elif is_registered:
            return True
        else:
            return False

    class Meta:
        model = Track
        filter_fields = ['id', 'title', 'is_active', 'categories']
        interfaces = (relay.Node,)


class PodcastNode(DjangoObjectType):
    has_bought = graphene.Boolean()

    def resolve_has_bought(self, info):
        is_registered = Podcast.objects.filter(pk=self.id, subscribers__in=[info.context.user.profile]).exists()
        if self.is_freemium:
            return True
        elif is_registered:
            return True
        else:
            return False

    class Meta:
        model = Podcast
        filter_fields = ['id', 'title', 'is_active', 'categories']
        interfaces = (relay.Node,)


class PodcastImageNode(DjangoObjectType):
    class Meta:
        model = PodcastImage
        filter_fields = ['id', 'is_featured']
        order_by = OrderingFilter(
            fields=(
                'order',
            )
        )
        interfaces = (relay.Node,)


class PodcastQuery(ObjectType):
    podcast = relay.Node.Field(PodcastNode)
    all_podcasts = DjangoFilterConnectionField(PodcastNode)

    track = relay.Node.Field(TrackNode)
    all_tracks = DjangoFilterConnectionField(TrackNode)

    podcast_image = relay.Node.Field(PodcastImageNode)
    all_podcast_images = DjangoFilterConnectionField(PodcastImageNode)
