from datetime import datetime
from urllib.parse import urlencode

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from payir.models import Gateway, Transaction

from shop.models import Basket


def current_datetime(request):
    token = request.GET.get('token')
    status = request.GET.get('status')
    gateway = Gateway.objects.filter(api_key='test').first()
    if status == '1' and token:
        transaction, gateway_verification = gateway.find_and_verify(token)
        if transaction.verified == gateway_verification:
            return_status = True
            done_before = False
            basket = transaction.order.basket
            basket.is_paid = True
            basket.save()
            Basket.objects.filter(updated_at__lt=basket.updated_at, is_paid=False).delete()
            for product in transaction.order.basket.products.all():
                product.podcast.subscribers.add(basket.profile)
        elif transaction.verified:
            return_status = True
            done_before = True
        else:
            return_status = False
            done_before = False
    else:
        return_status = False
        done_before = False
    base_url = gateway.default_redirect_url
    query_string = urlencode({'status': return_status, 'doneBefore': done_before})  # 2 category=42
    url = '{}?{}'.format(base_url, query_string)  # 3 /products/?category=42
    return redirect(url)  # 4
