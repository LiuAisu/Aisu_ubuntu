from django.urls import path, re_path
from booktest import views
from django.conf.urls import url


"""注意匹配时 从上到下 匹配到就停  所以使用url或re_path 时要严格匹配字符串开头和结尾  $"""
urlpatterns = [
    # 通过url函数设置url路由配置项  下面三种都表示同一个视图  建立 url index/ 与视图 index的匹配
    # 注意path 比对是路径 不是re
    path('index/', views.index, name='index'),
    path('index2/', views.index2, name='index'),
    path('show_books/', views.show_books, name='index'),
    # 用正则 有参数传递时 默认把匹配到的括号里的内容当参数传递给视图
    # path('books/<int:id>/', views.detail, name='index'),
    url(r'^books/(\d+)/$', views.detail, name='index'),

    # url 是django1里面的   这种是 用index来进行字符串的匹配   请求是/index/  在django中  前面的那个/不进行匹配
    # url(r'^index/$', views.index),
    # url(r'^index2/$', views.index2),
    # 这个和url相似
    # re_path(r'^index/$', views.index, name='index'),
    # re_path(r'^index2/$', views.index2, name='index'),
]