from django.shortcuts import render
from django.views import View

from utils.maxin import LoginRequireMaxin


class CartView(LoginRequireMaxin, View):
    def get(self, request):
        """显示购物车"""
        return render(request, 'dailyfresh/cart/cart.html')
# Create your views here.
