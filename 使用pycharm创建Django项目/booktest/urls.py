from django.urls import include, path
from booktest import views

urlpatterns = [
    path('index/', views.index),
]