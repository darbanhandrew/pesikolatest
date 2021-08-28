from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from subscription.models import Subscription, PodcastSubscription


class SubscriptionNode(DjangoObjectType):
    class Meta:
        model = Subscription
        filter_fields = ['id', 'starts_at', 'expires_at', 'profile']
        interfaces = (relay.Node,)


class PodcastSubscriptionNode(DjangoObjectType):
    class Meta:
        model = PodcastSubscription
        filter_fields = ['id', 'subscription', 'podcast']
        interfaces = (relay.Node,)


class SubscriptionQuery(ObjectType):
    subscription = relay.Node.Field(SubscriptionNode)
    all_subscriptions = DjangoFilterConnectionField(SubscriptionNode)

    podcast_subscription = relay.Node.Field(PodcastSubscriptionNode)
    all_podcast_subscriptions = DjangoFilterConnectionField(PodcastSubscriptionNode)