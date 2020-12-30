from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('', views.home,name="Home"),
    path('store/', views.store,name="store"),
    #path('index/', views.index,name="store"),
    path('contact/', views.contact,name="contact"),
    path('cart/', views.cart,name="cart"),
    path('checkout/', views.checkout,name="checkout"),
    path('update_item/',views.updateItem, name="update_item"),
	path('process_order/', views.processOrder, name="process_order"),
    url('store/category=laptop', views.index, name='search_by_all'),
    url('login/',views.loginPage,name="login"),
    url('register/',views.registerPage,name="register"),
    url('success/', views.successView, name='success'),
    ]