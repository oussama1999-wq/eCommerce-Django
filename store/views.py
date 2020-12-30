from django.shortcuts import render,redirect
from .models import *
from django.http import JsonResponse
import json
import datetime
from . utils import cookieCart,cartData, guestOrder
from django.contrib.auth.forms import  UserCreationForm
from .forms import OrderForm,CreateUserForm,ContactForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect

# Create your views here.
def registerPage(request):
	form=CreateUserForm()

	if request.method=='POST':
		form=CreateUserForm(request.POST)
		if form.is_valid():
			form.save()
			user=form.cleaned_data.get('username')
			messages.success(request,'Your Account was created for '+user)
			return redirect('store')

	context={'form':form}
	return render(request,'store/register.html',context)
def loginPage(request):
	if request.method=='POST':
		username=request.POST.get('username')
		password=request.POST.get('password')
		user=authenticate(request,username=username,password=password)
		if user is not None:
			return redirect('store')
		else:
			messages.info(request,'username or password is incorrect')
	context={}
	return render(request,'store/login.html',context)
def home(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	products = Product.objects.all()
	context = {'products':products, 'cartItems':cartItems}
	return render(request, 'store/Home.html', context)

def contact(request):
	data = cartData(request)
	if request.method == 'GET':
		form = ContactForm()
	else:
		form = ContactForm(request.POST)
		if form.is_valid():
			subject = form.cleaned_data['subject']
			from_email = form.cleaned_data['from_email']
			message = form.cleaned_data['message']
			try:
				send_mail(subject, message, from_email, ['elmalki.abdennour98@gmail.com'])
			except BadHeaderError:
				return HttpResponse('Invalid header found.')
			return redirect('success')

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']
	
	products = Product.objects.all()
	context = {'products':products, 'cartItems':cartItems,'form':form}
	return render(request, 'store/contact.html', context)
def successView(request):
    return HttpResponse('Success! Thank you for your message.')

def store(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']
	print(request.GET)
	category = request.GET.get('category')
	if category:
		products = Product.get_all_products_by_category(category)
	else:
		products = Product.objects.all()
	context = {'products':products, 'cartItems':cartItems}
	return render(request, 'store/store.html', context)
    
def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']   
    items = data['items']

    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/cart.html',context)

def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']   
    items = data['items']

    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/checkout.html',context)



def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('Action:', action)
    print('productId:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete = False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if (action == 'add' and  orderItem.quantity < orderItem.product.maxquantity):
        orderItem.quantity = (orderItem.quantity + 1)
        orderItem.product.maxquantity = (orderItem.product.maxquantity - 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
        orderItem.product.maxquantity = (orderItem.product.maxquantity + 1)
    
    orderItem.save()

    if orderItem.quantity <=0:
            orderItem.delete()
    return JsonResponse('Item was added', safe = False) 

def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
	else:
		customer, order = guestOrder(request, data)

	total = float(data['form']['total'])
	order.transaction_id = transaction_id

	if total == order.get_cart_total:
		order.complete = True
	order.save()

	if order.shipping == True:
		ShippingAddress.objects.create(
		customer=customer,
		order=order,
		address=data['shipping']['address'],
		city=data['shipping']['city'],
		state=data['shipping']['state'],
		zipcode=data['shipping']['zipcode'],
		)

	return JsonResponse('Payment submitted..', safe=False)

def index(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']
	print(request.GET)

	products = Product.objects.all()
	cat = 'laptop'
	if cat:
		products = Product.get_all_products_by_category(cat)
	else:
		products = Product.objects.all()
	context = {'products':products, 'cartItems':cartItems}
	return render(request, 'store/cat.html', context)