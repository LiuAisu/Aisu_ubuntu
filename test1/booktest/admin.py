from django.contrib import admin
from booktest.models import BookInfo
from booktest.models import HeroInfo
# Register your models here.
# 这里做网站的后管理的事情   管理相关文件
# 需要先本地化  进行时区和语言的配置
# 创建超级管理员
# python manage.py createsuperuser

"""可以自定义模型管理类 来告诉django管理页面显示那些内容"""
# 例 需要继承admin.ModelAdmin
class BookInfoAdmin(admin.ModelAdmin):
    '''图书模型管理类'''
    # 要显示什么内容就在list_display加什么
    list_display = ['id', 'btitle', 'bpub_date']
    # 需要让django知道 该管理类对应那个注册类  将参数传到注册语句


class HeroInfoAdmin(admin.ModelAdmin):
    list_display = ['id', 'hname', 'hgender', 'hcomment', 'hbook']
"""创建后登陆后台管理页面 使用 python manage.py runserver
在 应用下的admin.py中注册模型类
注册模型类  告诉框架根据注册的模型类来生成对应的表管理界面"""
admin.site.register(BookInfo, BookInfoAdmin)
admin.site.register(HeroInfo, HeroInfoAdmin)




