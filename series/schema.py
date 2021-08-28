import graphene
from django_filters import OrderingFilter
from graphene import relay, ObjectType, String
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .models import *


class EpisodeNode(DjangoObjectType):
    has_access = graphene.Boolean()

    def resolve_has_access(self, info):
        is_registered = Serial.objects.filter(pk=self.serial.id, subscribers__in=[info.context.user.profile]).exists()
        if self.is_freemium:
            return True
        elif is_registered:
            return True
        else:
            return False

    class Meta:
        model = Episode
        filter_fields = ['id', 'title', 'is_active', 'categories']
        interfaces = (relay.Node,)


class SerialNode(DjangoObjectType):
    has_bought = graphene.Boolean()

    def resolve_has_bought(self, info):
        is_registered = Serial.objects.filter(pk=self.id, subscribers__in=[info.context.user.profile]).exists()
        if self.is_freemium:
            return True
        elif is_registered:
            return True
        else:
            return False

    class Meta:
        model = Serial
        filter_fields = ['id', 'title', 'is_active', 'categories']
        interfaces = (relay.Node,)


class SerialImageNode(DjangoObjectType):
    class Meta:
        model = SerialImage
        filter_fields = ['id', 'is_featured']
        order_by = OrderingFilter(
            fields=(
                'order',
            )
        )
        interfaces = (relay.Node,)


class SerialQuery(ObjectType):
    serial = relay.Node.Field(SerialNode)
    all_serials = DjangoFilterConnectionField(SerialNode)

    episode = relay.Node.Field(EpisodeNode)
    all_episodes = DjangoFilterConnectionField(EpisodeNode)

    serial_image = relay.Node.Field(SerialImageNode)
    all_serial_images = DjangoFilterConnectionField(SerialImageNode)
