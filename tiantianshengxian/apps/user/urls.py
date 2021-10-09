from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.urls import path, include
from user import views
from user.views import RegisterView, ActiveView, LoginView, \
    UserInfoView, UserAddressView, UserOrderView, LogOutView

urlpatterns = [
    # url(r'^register/$', views.register, name='register'),
    # url(r'^register_handle/$', views.register_handle, name='register_handle'),
    # url(r'^regiter_ajax_handle/$', views.regiter_ajax_handle, name='regiter_ajax_handle')
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^active/(?P<token>.*)$', ActiveView.as_view(), name='active'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    # url(r'^center/$', login_required(UserInfoView.as_view()), name='user'),
    # url(r'^order/$', login_required(UserOrderView.as_view()), name='order'),
    # url(r'^address/$', login_required(UserAddressView.as_view()), name='address'),
    url(r'^center/$', UserInfoView.as_view(), name='center'),
    url(r'^order/(?P<page_index>\d+)/$', UserOrderView.as_view(), name='order'),
    url(r'^address/$', UserAddressView.as_view(), name='address'),
    url(r'^logout/$', LogOutView.as_view(), name='logout'),
]