from django.conf.urls import url
from django.urls import path, include

from cart.views import CartView, CartAdd, CartUpdateView, CartDeleteView

urlpatterns = [
    url(r'^show/$', CartView.as_view(), name='show'),
    url(r'^add/$', CartAdd.as_view(), name='add'),
    url(r'^update/$', CartUpdateView.as_view(), name='update'),
    url(r'^delete/$', CartDeleteView.as_view(), name='delete')
]