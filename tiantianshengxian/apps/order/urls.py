from django.conf.urls import url
from django.urls import path, include
from order.views import OrderPlaceView, OrderCommit, OrderPayView, OrderCheckView, OrderCommentView
urlpatterns = [
            url(r'^place/$', OrderPlaceView.as_view(), name='place'),
            url(r'^commit/$', OrderCommit.as_view(), name='commit'),
            url(r'^pay/$', OrderPayView.as_view(), name='pay'),
            url(r'^check/$', OrderCheckView.as_view(), name='check'),
            url(r'^comment/(?P<order_id>\d+)/$', OrderCommentView.as_view(), name='comment'),
]