import graphene
from django.utils.http import urlencode
from graphene import relay, ObjectType, String
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id

from .models import *
from payir.models import Transaction, Gateway


class ProductNode(DjangoObjectType):
    class Meta:
        model = Product
        filter_fields = ['id', 'title']
        interfaces = (relay.Node,)


class TransactionNode(DjangoObjectType):
    class Meta:
        model = Transaction
        filter_fields = ['id']
        interfaces = (relay.Node,)


class CouponNode(DjangoObjectType):
    class Meta:
        model = Coupon
        filter_fields = ['id', 'title']
        interfaces = (relay.Node,)


class BasketNode(DjangoObjectType):
    class Meta:
        model = Basket
        filter_fields = ['id', 'profile']
        interfaces = (relay.Node,)


class OrderNode(DjangoObjectType):
    class Meta:
        model = Order
        filter_fields = ['id', 'profile', 'transaction']
        interfaces = (relay.Node,)


class OrderNoteNode(DjangoObjectType):
    class Meta:
        model = OrderNote
        filter_fields = ['id', 'order', 'message']
        interfaces = (relay.Node,)


class ShopQuery(graphene.ObjectType):
    product = relay.Node.Field(ProductNode)
    all_products = DjangoFilterConnectionField(ProductNode)

    transaction = relay.Node.Field(TransactionNode)
    all_transactions = DjangoFilterConnectionField(TransactionNode)

    coupon = relay.Node.Field(CouponNode)
    all_coupons = DjangoFilterConnectionField(CouponNode)

    basket = relay.Node.Field(BasketNode)
    all_baskets = DjangoFilterConnectionField(BasketNode)
    current_basket = graphene.Field(BasketNode)

    def resolve_current_basket(root, info):
        try:
            return Basket.objects.filter(profile=info.context.user.profile, is_paid=False).last()
        except Basket.DoesNotExist:
            return None

    order = relay.Node.Field(OrderNode)
    all_orders = DjangoFilterConnectionField(OrderNode)

    order_note = relay.Node.Field(OrderNoteNode)
    all_order_notes = DjangoFilterConnectionField(OrderNoteNode)


# ----- Mutations ----
class TransactionMutation(graphene.Mutation):
    # class Arguments:
    #     # The input arguments for this mutation
    #     # text = graphene.String(required=True)
    #     # id = graphene.ID()
    # pass

    # The class attributes define the response of the mutation
    transaction = graphene.Field(TransactionNode)

    @classmethod
    def mutate(cls, root, info):
        if info.context.user.is_authenticated:
            user = info.context.user
            profile = Profile.objects.get(user=user)
            basket = Basket.objects.filter(profile=profile, is_paid=False).last()
            gateway = Gateway.objects.filter(api_key='test').first()
            transaction = Transaction(account=user, amount=basket.total_amount * 10, gateway=gateway)
            transaction.save()
            order = Order(basket=basket, profile=profile, transaction=transaction)
            order.save()
            gateway.submit(info.context, transaction, mobile=None, valid_card_number=None, callback=None)
        # Notice we return an instance of this mutation
        return TransactionMutation(transaction=transaction)


class VerifyTransactionMutation(graphene.Mutation):
    class Arguments:
        token = graphene.String(required=True)
        status = graphene.String(required=True)

    transaction = graphene.Field(TransactionNode)
    status = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, token, status):
        transaction = Transaction.objects.filter(token=token).first()
        gateway = Gateway.objects.filter(api_key='test').first()
        transaction, gateway_verification = gateway.find_and_verify(token)
        if transaction.verified == gateway_verification:
            return_status = True
        else:
            return_status = False
        return VerifyTransactionMutation(transaction=transaction, status=return_status)


class ProductToBasketMutation(graphene.Mutation):
    class Arguments:
        product_id = graphene.ID(required=True)
        action = graphene.String(required=True)

    status = graphene.Boolean()
    product = graphene.Field(ProductNode)
    basket = graphene.Field(BasketNode)

    @classmethod
    def mutate(cls, root, info, product_id, action):
        basket = Basket.objects.filter(profile=info.context.user.profile, is_paid=False).last()
        if not basket:
            basket = Basket(profile=info.context.user.profile)
            basket.save()
        node_type, _product_id = from_global_id(product_id)
        product = Product.objects.get(pk=_product_id)
        if action == 'add':
            basket.products.add(product)
            status = True
        else:
            basket.products.remove(product)
            status = False
        return ProductToBasketMutation(status=status, product=product, basket=basket)


class CouponToBasketMutation(graphene.Mutation):
    class Arguments:
        coupon_title = graphene.String(required=True)
        action = graphene.String(required=True)

    status = graphene.Boolean()
    coupon = graphene.Field(CouponNode)
    basket = graphene.Field(BasketNode)

    @classmethod
    def mutate(cls, root, info, coupon_title, action):
        basket = Basket.objects.filter(profile=info.context.user.profile, is_paid=False).last()
        if not basket:
            basket = Basket(profile=info.context.user.profile)
            basket.save()
        coupon = Coupon.objects.filter(title=coupon_title).first()
        if action == 'add':
            basket.coupons.add(coupon)
            status = True
        else:
            basket.coupons.remove(coupon)
            status = False
        return CouponToBasketMutation(status=status, coupon=coupon, basket=basket)


class ShopMutation(graphene.ObjectType):
    pay = TransactionMutation.Field()
    verify_payment = VerifyTransactionMutation.Field()
    product_to_basket = ProductToBasketMutation.Field()
    coupon_to_basket = CouponToBasketMutation.Field()
