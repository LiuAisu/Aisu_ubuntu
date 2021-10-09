from django.urls import path
from booktest import views
from django.conf.urls import url


"""注意匹配时 从上到下 匹配到就停  所以使用url或re_path 时要严格匹配字符串开头和结尾  $"""
urlpatterns = [
    # 通过url函数设置url路由配置项  下面三种都表示同一个视图  建立 url index/ 与视图 index的匹配
    # 注意path 比对是路径 不是re
    url(r'^index2/$', views.index2, name='index2/'),
    path('index/', views.index, name='index'),
    path('show_books/', views.show_books, name='show_books/'),
    # 用正则 有参数传递时 默认把匹配到的括号里的内容当参数传递给视图
    # path('books/<int:id>/', views.detail, name='index'),
    url(r'^books/(\d+)/$', views.detail, name='^books/'),
    url(r'^create/$', views.cerate, name='^create/'),
    url(r'^delete/(\d+)/$', views.delete_book, name='delete/'),
    # 捕获关键字参数   正则组名必须和视图关键字参数名字相同
    # url(r'^delete/(?P<num>\d+)/$', views.delete_book, name='index'),
    path('areas/', views.areas_get, name='areas/'),
    path('login/', views.login),
    path('login_cheak/', views.login_cheak),
    path('ajax_test/', views.ajax_test),
    path('ajax_handle/', views.ajax_handle),
    path('login_ajax/', views.login_ajax),
    path('login_ajax_cheak/', views.login_ajax_cheak),
    path('set_cookie/', views.set_cookie),
    path('get_cookie/', views.get_cookie),
    path('set_session/', views.set_session),
    path("get_session/", views.get_session),
    path('clear_session/', views.clear_session),
    path('tem_var/', views.tem_var),
    path('tem_tags/', views.tem_tags),
    path('tem_inhert/', views.tem_inhert),
    path('html_escape/', views.html_escape),
    path('login_pwd_change/', views.login_pwd_change),
    path('login_pwd_change_action/', views.login_pwd_change_action),
    path('verify_code/', views.verify_code),
    path('url_reverse/', views.url_reverse, name='url_reverse'),
    url(r'^show_wargs/(\d+)/(\d+)/$', views.show_wargs, name='show_wargs'),
    url(r'^show_kwargs/(?P<c>\d+)/(?P<d>\d+)/$', views.show_kwargs, name='show_kwargs'),
    path('redict_index/', views.redict_index),
    path('ip_fobbitton/', views.ip_fobbitton),
    path('show_upload/', views.show_upload),
    path('upload_action/', views.upload_action),
    # \d*可以有可以没有   \d+至少有一个
    url(r'^show_area(?P<pindex>\d*)/$', views.show_area),
    url(r'^area_three/$', views.area_three),
    url(r'^prov/$', views.prov),
    url(r'^city(\d+)/$', views.city),
    url(r'^dis(\d+)/$', views.dis),
    url(r'^set_redis_session/$', views.set_redis_session),
    url(r'^get_redis_session/$', views.get_redis_session),
    # url 是django1里面的   这种是 用index来进行字符串的匹配   请求是/index/  在django中  前面的那个/不进行匹配
    # url(r'^index/$', views.index),
    # url(r'^index2/$', views.index2),
    # 这个和url相似
    # re_path(r'^index/$', views.index, name='index'),
    # re_path(r'^index2/$', views.index2, name='index'),
]