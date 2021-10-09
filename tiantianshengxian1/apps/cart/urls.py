from django.conf.urls import url
from django.urls import path, include

from cart.views import CartView

urlpatterns = [
    url(r'^cart/$', CartView.as_view(), name='cart'),
]