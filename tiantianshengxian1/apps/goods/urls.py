from django.conf.urls import url
from django.urls import path, include
from goods import views
from goods.views import IndexView
urlpatterns = [
    # url(r'', views.show_index, name='index'),
    url(r'^index/$', IndexView.as_view(), name='index')
]