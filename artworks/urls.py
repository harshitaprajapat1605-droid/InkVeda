from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('gallery/', views.gallery, name='gallery'),
    path('artwork/<int:pk>/', views.artwork_detail, name='artwork_detail'),
    path('checkout/<int:pk>/', views.checkout, name='checkout'),
    path('receipt/<str:order_id>/', views.receipt, name='receipt'),
    path('upi-payment/<str:order_id>/', views.upi_payment, name='upi_payment'),
    path('track-order/', views.track_order, name='track_order'),
    path('custom-order/', views.custom_order, name='custom_order'),
    path('custom-order/payment/<int:pk>/', views.custom_order_payment, name='custom_order_payment'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('admin-analytics/', views.admin_analytics, name='admin_analytics'),
]
