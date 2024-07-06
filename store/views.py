from django.shortcuts import render
from django.http import JsonResponse
from .models import *
import json
import datetime

def store(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        order = {'get_cart_total': 0, 'get_cart_items':0, 'shipping':False}
        items = []
        cartItems = order['get_cart_items']

    products = Product.objects.all()
    context = {'products': products, 'cartItems':cartItems}
    return render(request, 'store/index.html', context)

def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items':0, 'shipping':False}
        cartItems = order['get_cart_items']

    context = {'items': items, 'order': order, 'cartItems':cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items

        # Kargo gerekli mi değil mi kontrol et
        shipping = True
    else:
        order = {'get_cart_total': 0, 'get_cart_items': 0,'shipping':False}
        items = []
        shipping = False

    context = {'items': items, 'order': order, 'cartItems': cartItems, 'shipping': shipping}

    return render(request, 'store/checkout.html', context)

def updateItem(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body.decode('utf-8'))
            productId = data.get('productId')
            action = data.get('action')

            if not productId or not action:
                return JsonResponse({'error': 'Eksik veri: productId veya action'}, status=400)

            print('Action:', action)
            print('productId:', productId)

            customer = request.user.customer
            product = Product.objects.get(id=productId)
            order, created = Order.objects.get_or_create(customer=customer, complete=False)

            orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

            if action == 'add':
                orderItem.quantity = (orderItem.quantity + 1)
            elif action == 'remove':
                orderItem.quantity = (orderItem.quantity - 1)

            orderItem.save()

            if orderItem.quantity <= 0:
                orderItem.delete()

            return JsonResponse('Ürün sepete eklendi', safe=False)
        else:
            return JsonResponse({'error': 'Geçersiz istek yöntemi'}, status=400)
    except Exception as e:
        print('Error:', e)
        return JsonResponse({'error': str(e)}, status=500)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer  # Düzeltilmiş
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        if total == order.get_cart_total:  # Doğru metod çağrıldığından emin olun
            order.complete = True
        order.save()

        if order.shipping:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode'],
            )

    else:
        print('print is not logged in..')

    return JsonResponse('Payment complete', safe=False)