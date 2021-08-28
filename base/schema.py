import graphene
import graphql_jwt
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.forms import ModelForm
from graphene import relay, ObjectType, String
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql_jwt.refresh_token.shortcuts import create_refresh_token
from graphql_jwt.shortcuts import get_token
from .models import *


# Graphene will automatically map the Category model's fields onto the CategoryNode.
# This is configured in the CategoryNode's Meta class (as you can see below)
class UserNode(DjangoObjectType):
    class Meta:
        model = get_user_model()
        filter_fields = ['id']
        interfaces = (relay.Node,)


class ProfileNode(DjangoObjectType):
    class Meta:
        model = Profile
        filter_fields = ['id', 'phone_number', 'user']
        interfaces = (relay.Node,)


class OtpNode(DjangoObjectType):
    class Meta:
        model = OTP
        filter_fields = ['id', 'profile']
        interfaces = (relay.Node,)


class CategoryNode(DjangoObjectType):
    class Meta:
        model = Category
        filter_fields = ['id', 'title']
        interfaces = (relay.Node,)


class ImageNode(DjangoObjectType):

    def resolve_image(self, info):
        if self.image:
            self.image = info.context.build_absolute_uri(self.image.url)
        return self.image

    class Meta:
        model = Image
        filter_fields = ['id', 'title', 'description', 'slug']
        interfaces = (relay.Node,)


class FileNode(DjangoObjectType):

    def resolve_file(self, info):
        if self.file:
            self.file = info.context.build_absolute_uri(self.file.url)
        return self.file

    class Meta:
        model = File
        filter_fields = ['id', 'title', 'description', 'slug']
        interfaces = (relay.Node,)


class PostNode(DjangoObjectType):
    class Meta:
        model = Post
        filter_fields = ['id', 'title', 'description', 'categories']
        interfaces = (relay.Node,)


class BaseQuery(graphene.ObjectType):
    user = relay.Node.Field(UserNode)
    all_users = DjangoFilterConnectionField(UserNode)

    profile = relay.Node.Field(ProfileNode)
    all_profiles = DjangoFilterConnectionField(ProfileNode)

    otp = relay.Node.Field(OtpNode)
    all_otps = DjangoFilterConnectionField(OtpNode)

    category = relay.Node.Field(CategoryNode)
    all_categories = DjangoFilterConnectionField(CategoryNode)

    image = relay.Node.Field(ImageNode)
    all_images = DjangoFilterConnectionField(ImageNode)

    file = relay.Node.Field(FileNode)
    all_files = DjangoFilterConnectionField(FileNode)

    post = relay.Node.Field(PostNode)
    all_posts = DjangoFilterConnectionField(PostNode)


# Mutations --------------------
# -------------------------------
class RequestOTP(graphene.Mutation):
    status = graphene.Field(String)

    class Arguments:
        username = graphene.String(required=True)

    def mutate(self, info, username):
        user_obj = User.objects.get(username=username)
        profile_obj = Profile.objects.get(user=user_obj.id)
        otp = OTP(profile=profile_obj)
        otp.save()
        return RequestOTP(status="success")


class VerifyUser(graphene.Mutation):
    status = graphene.Field(String)

    class Arguments:
        username = graphene.String(required=True)
        otp_message = graphene.String(required=True)

    def mutate(self, info, username, otp_message):
        user_obj = User.objects.get(username=username)
        profile_obj = Profile.objects.get(user=user_obj.id)
        related_otp = OTP.objects.filter(profile=profile_obj.id)
        for otp in related_otp:
            if otp.message == otp_message and otp.is_valid == True:
                otp.valid = False
                profile_obj.status = True
                otp.save()
                profile_obj.save()
                return VerifyUser(status="success")
        return VerifyUser(status="failed")


# CreateUser
class CreateUser(graphene.Mutation):
    user = graphene.Field(UserNode)
    profile = graphene.Field(ProfileNode)
    token = graphene.String()
    refresh_token = graphene.String()

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, username, password):
        user = get_user_model()(
            username=username,
            email="",
        )
        user.set_password(password)
        user.save()

        profile_obj = Profile.objects.get(user=user.id)
        token = get_token(user)
        refresh_token = create_refresh_token(user)
        # phone_number = profile_obj.phone_number
        # otp = OTP.objects.get(profile=profile_obj.id)
        # otp_send(phone_number, otp.message)
        return CreateUser(user=user, profile=profile_obj, token=token, refresh_token=refresh_token)


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'


class profileMutation(DjangoModelFormMutation):
    profile = graphene.Field(ProfileNode)

    class Meta:
        form_class = ProfileForm


class ObtainJSONWebToken(graphql_jwt.JSONWebTokenMutation):
    user = graphene.Field(UserNode)

    # ip = graphene.String()
    # session = graphene.String()

    # @classmethod
    # def Field(cls, *args, **kwargs):
    #     cls._meta.arguments.update({
    #         'session': graphene.String()
    #     })
    #     return super().Field(*args, **kwargs)

    @classmethod
    def resolve(cls, root, info, **kwargs):
        # request = info.context.request
        # client_ip, is_routable = get_client_ip(request)
        # session = kwargs['session']
        return cls(user=info.context.user)


class BaseMutation(graphene.ObjectType):
    token_auth = ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    create_user = CreateUser.Field()
    verify_user = VerifyUser.Field()
    request_otp = RequestOTP.Field()
    profile_edit = profileMutation.Field()
