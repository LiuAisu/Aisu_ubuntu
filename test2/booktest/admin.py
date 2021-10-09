from django.contrib import admin
from booktest.models import BookInfo, HeroInfo, AreaInfo, PicImage, Htmlfield_Choice_test
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

class AreaStackedInline(admin.StackedInline):
    # 写多类的名字
    model = AreaInfo
    # 在一类对应的管理类加属性 inline 对应这个类

    # 指定添加框的个数
    extra = 2

class AreaTabularInline(admin.TabularInline):
    # 写多类的名字
    model = AreaInfo
    # 在一类对应的管理类加属性 inline 对应这个类

    # 指定添加框的个数
    extra = 2

class AreaInfoAdmin(admin.ModelAdmin):
    """地区模型管理类"""
    list_per_page = 10  # 指定每页显示10条数据
    # 如果想让 自己定义的方法对应的列也能点击 需要给对应类中对应方法 加一个属性 admin_order_field
    list_display = ['id', 'atitle', 'view_title', 'view_parent']
    # 如果想让管理页面底部也有下拉选择框则需要在管理类中加属性  actions_on_bottom
    # actions_on_top 可以取消顶部下拉选择框
    actions_on_bottom = True
    actions_on_top = False

    # 页面的右侧还可以有一个 过滤栏  list_filter
    list_filter = ['atitle']
    # 在页面上方增加一个搜索框  并指定搜索内容为atitle  search_fields
    search_fields = ['atitle']
    # 指定编辑页面属性的显示顺序 fields  和分组fieldsets  两者只能用一个
    # fields = ['aParent', 'atitle']
    # 分组显示 并指定该组内显示的字段 两个元组  里面的元组 前面是    组标题  后面是显示的字段
    fieldsets = (
        ('基本', {'fields':['atitle']}),
        ('父级', {'fields': ['aParent']})
    )


    # 在一对多的情况下可以在一端页面  显示编辑  多端的内容  需要创建AreaStackedInline类
    # 有两种嵌入多类内容的方式一种是  块嵌入AreaStackedInline继承admin.ModelAdmin  一种以表格嵌入AreaTabularInline
    # 两种效果相同但显示格式不同
    inlines = [AreaTabularInline]


"""创建后登陆后台管理页面 使用 python manage.py runserver
在 应用下的admin.py中注册模型类
注册模型类  告诉框架根据注册的模型类来生成对应的表管理界面"""
admin.site.register(BookInfo, BookInfoAdmin)
admin.site.register(HeroInfo, HeroInfoAdmin)
admin.site.register(AreaInfo, AreaInfoAdmin)
admin.site.register(PicImage)
admin.site.register(Htmlfield_Choice_test)




