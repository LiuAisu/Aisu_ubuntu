from django.conf.urls import url
from django.urls import path, include
from goods import views
from goods.views import IndexView, DetailView, GoodsListView
urlpatterns = [
    # url(r'', views.show_index, name='index'),
    url(r'^index/$', IndexView.as_view(), name='index'),
    url(r'^detail/(?P<sku_id>\d+)$', DetailView.as_view(), name='detail'),
    url(r'^list/(?P<type_id>\d+)/(?P<page_index>\d+)$', GoodsListView.as_view(), name='list')
]