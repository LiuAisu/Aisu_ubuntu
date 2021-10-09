from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader, RequestContext
from booktest.models import BookInfo
"""该文件做视图函数  来使用视图函数来处理浏览器的请求  视图函数处理过后 要返回内容给浏览器"""
# Create your views here.
# 视图函数必须要有一个参数  该参数是http request类型的一个对象
# 该函数作用就是 当浏览器访问 http://127.0.0.1:8000/index时 调用所定义的视图函数
# 还要进行url配置 目的建立url地址和视图的对应关系


def my_render(request, template_path, context_dict=None):
    # 使用模板文件
    # 1.加载模板文件   去模板目录下获取html文件的内容 得到一个模板对象。
    temp = loader.get_template(template_path)  # 返回值模板对象
    # 2.定义模板上下文  向模板文件传递数据  这个字典就是向模板传参数的  为空时 不传
    # 在django1.x中 RequestContext或Context可用升级后不可用  直接 temp.render({})
    # context = RequestContext(request, {})
    # 3.模板渲染  得到一个标准的html内容
    res_html = temp.render(context_dict)
    # 返回浏览器
    return HttpResponse(res_html)

def index(request):
    # 进行处理 和M 及 T进行交互  处理完成后返回应答给浏览器
    # 最终返回的是一个  HttpResponse() 对象
    # 在项目中的urls 配置一个包含该应用的 urls
    # 在通过 path 或re_path 或 url 来匹配应用
    # return HttpResponse('老铁没毛病')

    template_path = 'booktest/index.html'
    # 模板变量  {{}}
    context_dicts = {'content': "已经替换字符串", 'list': list(range(1, 10))}
    res_html = my_render(request, template_path, context_dicts)
    return res_html


def index2(request):
    return HttpResponse('hellow python')


# 显示图书的信息
def show_books(request):
    """显示图书信息"""
    # 1.通过M查找 图书表中的数据
    books = BookInfo.objects.all()
    books_dict = {'books': books}
    return my_render(request, 'booktest/show_books.html', books_dict)


def detail(request, bid):
    """根据对应地址 访问对应页面"""
    # 1.根据bid 查询图书信息
    book = BookInfo.objects.get(id=bid)
    # 2.查询和book关联的英雄信息
    heros = book.heroinfo_set.all()
    # 3.使用模板 把数据传给模板
    return my_render(request, 'booktest/detail.html', {'book': book, 'heros': heros})




