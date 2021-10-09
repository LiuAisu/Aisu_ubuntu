# import requests
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader, RequestContext
from booktest.models import BookInfo, AreaInfo, PicImage
from datetime import date
from PIL import Image, ImageDraw, ImageFont
from django.utils.six import BytesIO
from django.conf import settings
"""该文件做视图函数  来使用视图函数来处理浏览器的请求  视图函数处理过后 要返回内容给浏览器"""


# Create your views here.
# 视图函数必须要有一个参数  该参数是http request类型的一个对象
# 该函数作用就是 当浏览器访问 http://127.0.0.1:8000/index时 调用所定义的视图函数
# 还要进行url配置 目的建立url地址和视图的对应关系
# 视图的request就是  HttpResponse类型的实例对象
# request包含浏览器请求的信息   这个request就是 我们自己作web框架时的env字典参数保存到request对象里

# render(request, tempetes_path, content_dict) 和我们自己定义的my_render效果相同

# django模板加载顺序是  先去模板文件夹找  再去INSTALL_APPS下的每个应用下找  前提是应用中有模板文件夹
def index2(request):
    """这里测试django模板加载顺序"""
    template_path = 'booktest/index2.html'
    # 模板变量  {{}}
    context_dicts = {'content': '成功找到了应用下的index2模板文件'}
    return render(request, template_path, context_dicts)


"""模板变量解析过程  例：book.btitle
   1. 首先将book当作是字典  把btitle 当键值 book['btitle']
   2. 把book当作一个对象 把btitle当作一个对象的属性  book.btitle
   3. 把book当成一个对象 把btitle当作对象的方法 取对象的返回值  
   当 book.0  即点后面是数值时 
   1. 首先将book当作是字典  把0当键值 book['0']
   2. 把book当作列表  取列表下表为0 的值 book[0]
   如果模板解析失败则使用空白充当模板变量
   使用模板变量时  点前面可能是  字典， 列表， 对象
   """


def tem_var(request):
    """这里测试模板变量"""
    tem_dict = {"title": '字典时取键值'}
    tem_list = ['李江龙', '刘海俊', '张云鹤']
    book = BookInfo.objects.get(id=1)
    templete_path = 'booktest/tem_var.html'
    context_dict = {'my_dict': tem_dict, 'my_list': tem_list, 'my_book': book}
    return render(request, templete_path, context_dict)


'''模板标签的使用'''
def tem_tags(request):
    books = BookInfo.objects.all()
    context_dict = {'my_book': books}
    templete_path = 'booktest/tem_tags.html'
    return render(request, templete_path, context_dict)


def my_render(request, template_path, context_dict=None):
    # 使用模板文件
    # 1.加载模板文件   去模板目录下获取html文件的内容 得到一个模板对象。
    temp = loader.get_template(template_path)  # 返回值模板对象
    # 2.定义模板上下文  向模板文件传递数据  这个字典就是向模板传参数的  为空时 不传
    # 在django1.x中 RequestContext或Context可用升级后不可用  直接 temp.render({})
    # context = RequestContext(request, context_dict)
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
    books = BookInfo.objects.all()
    # 使用模板
    template_path = 'booktest/index.html'
    # 模板变量  {{}}
    context_dicts = {'books': books}
    res_html = my_render(request, template_path, context_dicts)
    return res_html


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


def cerate(request):
    '''新增一本书'''
    # 1. 创建BookInfo对象
    book = BookInfo()
    book.btitle = '流星蝴蝶剑'
    book.bpub_date = date(1990, 1, 2)
    book.bread = 44
    book.bcomment = 56
    book.is_delete = False
    # 保存进数据库
    book.save()
    # 3. 返回应答
    # return HttpResponse('ok')
    # 4. 让浏览器重新访问某个地址 （重定向）   使用HttpResponseRedirect  /index表示 127.0.0.1：8000/index/
    # django.shortcuts里的 redirect和这个作用相同
    # return HttpResponseRedirect(redirect_to='/index')
    return redirect(to='/index')


def delete_book(request, bid):
    # 1. 通过bid 获取要删除的图书对象
    book = BookInfo.objects.get(id=bid)
    # 2. 删除
    book.delete()
    # 3. 重定向
    return HttpResponseRedirect(redirect_to='/index')


def areas_get(request):
    '''获取石家庄市的上级地区和下级地区'''
    # 1. 获取石家庄市信息
    area = AreaInfo.objects.get(atitle='石家庄市')
    # 2.查询石家庄市的上级地区
    """通过多类条件查询一类数据
    一类名.objects.filter(多类名__多类属性__条件名)
    通过一类条件查询多类数据
    多类名.objects.filter(关联属性__一类属性名__条件名)"""
    parent = area.aParent
    # parent = AreaInfo.objects.filter(AreaInfo__aParent__=100000)
    # 3. 查询石家庄市下级地区
    childrens = area.areainfo_set.all()
    # childrens = AreaInfo.objects.filter(aParent__id__=area.aParent)
    return my_render(request, 'booktest/areas.html', {'area': area, 'parent': parent, 'childrens': childrens})


# 登录判断装饰器  作csrf防护 跨站攻击防护
def login_require(view_func):
    """登录判断装饰器"""
    def wapper(request, *view_args, **view_kwargs):
        if request.session.has_key('islogin_now') or request.session.has_key('islogin'):
            # 用户已登录
            return view_func(request, *view_args, **view_kwargs)
        else:
            return redirect('/login/')
    return wapper


def login(request):
    """显示登录页面"""
    # 获取cookie username  先判断一下是否有这个cookie存在

    # 判断用户是否登录
    if request.session.has_key('islogin'):
        # 已经登录直接跳转到密码修改界面
        return redirect('/login_pwd_change/')
    else:
        if 'username' in request.COOKIES:
            # 获取记住的用户名
            username = request.COOKIES['username']
        else:
            username = ''
            # my_render里使用的是HttpResponse 返回的渲染页面并不会自动的渲染csrf_token 要使用自带的render函数
        return render(request, 'booktest/login.html', {'username': username})


def login_cheak(request):
    # 在request中有
    # path(请求路径),
    # method(请求放方式),
    # encoding(提交数据的编码方式),
    # GET(QueryDict的对象 以POST方式提交的参数),
    # POST(QueryDict的对象 以GET方式提交的参数),
    # COOKIES(标准的python字典  键和值都是字符串),
    # session(一个可读可写的类似字典的对象  表示当前会话  只有Django启用会话支持时可用)
    # FILES (一个类似字典的对象  包含所有上传文件)
    """登录校验视图"""
    # request.POST 保存的是 以POST方式提交的参数
    # request.GET 保存的是 以GET方式提交的参数   两个都是QueryDict的对象 和字典很类似  但是在这里一个键可以对应多个值
    # 从QueryDict的对象取数据  有request.POST.get('username')方法  还有直接request.POST['username']   request..POST.getlist()取出多个值放在列表
    # 1. 获取用户提交表单里的用户名和密码
    username = request.POST.get('username')
    password = request.POST.get('password')
    # 这个remember 是 on 或 none
    remember = request.POST.get('remember')
    remember_login = request.POST.get('login')
    # 获取用户输入的验证码
    vcode = request.POST.get('vcode')
    # 获取session中保存的验证码
    vcode_session = request.session.get('verifycode')
    if vcode != vcode_session:
        return redirect('/login')
    # print(username + password)
    # 2. 进行登录的校验
    # 实际开发时 根据用户名和密码查找数据库
    if username == 'aisu' and password == 'ss123456':
        # redirect返回值就是一个HttpResponse类对象   cookie就需要HttpResponse类对象设置
        response = redirect('/login_pwd_change/')
        if remember == 'on':
            # 设置过期时间为120秒
            response.set_cookie('username', username)
        if remember_login == 'on':
            # print('wowowo')
            request.session['islogin'] = username
            # response.set_cookie('password', password, max_age=120)
        else:
            request.session['islogin_now'] = username
            request.session.set_expiry(0)
        return response
    else:
        return redirect('/login/')
    # 3. 返回应答



# 调用时 首先调用装饰器login_require(login_pwd_change) 传入这个被装饰器装饰的函数 返回的是wapper()函数
#  再调wapper(request)
@login_require
def login_pwd_change(request):
    """显示密码修改界面"""
    # 进行用户登录判断 多个页面判断用户登录 就可以使用登录装饰器
    """if not request.session.has_key('islogin'):
        return redirect('/login')"""
    return render(request, 'booktest/login_pwd_change.html')


@login_require
def login_pwd_change_action(request):
    """显示密码修改成功界面"""
    # 进行用户登录判断
    """if not request.session.has_key('islogin'):
        return redirect('/login')"""
    pwd = request.POST.get('pwd')
    # 获取记住的用户名
    if request.session.has_key('islogin'):
        username = request.session['islogin']
        conxtext = {'content': '%s修改密码为%s' % (username, pwd)}
        return render(request, 'booktest/login_pwd_vhange_action.html', conxtext)
    else:
        username = request.session['islogin_now']
        conxtext = {'content': '%s修改密码为%s' % (username, pwd)}
        return render(request, 'booktest/login_pwd_vhange_action.html', conxtext)


def ajax_test(request):
    """显示ajax页面"""
    return my_render(request, 'booktest/ajax_test.html')


def ajax_handle(request):
    """ajax请求处理"""
    # 返回json数据
    return JsonResponse({"res": 1})


def login_ajax(request):
    """显示ajax登录页面"""
    return my_render(request, 'booktest/login_ajax.html')


# ajax 请求在后台 不要重定向页面  处理返回json数据  至于跳转页面 通过回调函数
def login_ajax_cheak(request):
    """ajax登录校验"""
    # 1. 获取用户名和密码
    username = request.POST.get('username')
    password = request.POST.get('password')
    # 2. 进行校验
    if username == 'aisu' and password == 'ss123456':
        return JsonResponse({'res': 1})
    else:
        return JsonResponse({'res': 0})
    # 3. 返回json数据


def set_cookie(request):
    """设置cookie信息  需要一个HttpResponse类的对象 或子类对象"""
    response = HttpResponse('设置cookie')
    # 设置一个cookie信息 名字为num 值为1   max_age=14*24*3600, expires= 都可以设置保存cookie的时间 这里设置60秒过期
    response.set_cookie('num', 1, max_age=60)
    # 返回
    return response


def get_cookie(request):
    """取出cookie值    cookie默认在浏览器关闭时删除"""
    cookie = request.COOKIES['num']
    return HttpResponse(cookie)


"""session存进去什么就取出什么 而cookie 取出的只是字符串"""


def set_session(request):
    """设置session使用request对象"""
    request.session['username'] = 'aisu'
    request.session['password'] = 18
    """设置session的过期时间 是设置这个session_id 的cookie时间的   默认2周过期  """
    """request.session.set_expiry(10) 如果不填写就默认  填写0 就是关闭浏览器过期  填写时间就是经过秒数过期"""
    request.session.set_expiry(10)
    return HttpResponse('设置session')


def get_session(request):
    """获取session也使用request对象   session保存在服务器  常使用在密码等安全性要求高的场景"""
    username = request.session['username']
    password = request.session['password']
    return HttpResponse(username + str(password))


def clear_session(request):
    """清除session信息    request.session.clear()这里清除的只是session_data值的部分 而这条数据不删除  """
    """request.session.flush() 删除的是这整条数据"""
    """如果这个session 里有多个数据 删除其中的一个 用 del request.session['键']"""
    request.session.flush()
    # request.session.clear()
    return HttpResponse('清除成功')


def tem_inhert(request):
    """模板继承
    使用{% block b1 %}
    <h1></h1>
    {% endblock b1 %}  注意空格
    {{ block.super }} 用于继承父模板内容"""
    return render(request, 'booktest/tem_child.html')


def html_escape(request):
    """模板转义  即将特殊符号 如>转为 &gt
     例如：<h1>hellow</h1>   变为&lt;h1&gt;hellow&lt;/h1&gt;  而没有当作标签
     1. 使用safe 可以一个字段的关闭转义
     2. 使用autoescape 关闭段转义
    {% autoescape off %}
    {{content}}
    {{content}}
    {% endautoescape %}
    模板硬编码中的字符串默认不经过转义：<br/>
    {{ test|default:'<h1>hellow</h1>' }}"""
    conxt_dict = {'content': '<h1>hellow</h1>'}
    return render(request, 'booktest/html_escape.html', conxt_dict)


"""验证码处理  使用Pillow包  这个包是图片处理包"""
def verify_code(request):
    """生成一个验证码图片"""
    import random
    bgcolor = (random.randrange(20, 100), random.randrange(20, 100), 255)
    witdth = 100
    height = 25
    im = Image.new('RGB', (witdth, height), bgcolor)
    draw = ImageDraw.Draw(im)
    for i in range(0, 100):
        xy = (random.randrange(0, witdth), random.randrange(0, height))
        fill = (random.randrange(0, 255), 255, random.randrange(0, 255))
        draw.point(xy, fill=fill)
    str1 = 'ABC123EFG456HIJ789KLM0OPQRSTUVWXYZ'
    rand_str = ''
    for i in range(0, 4):
        rand_str += str1[random.randrange(0, len(str1))]
    font = ImageFont.truetype('FreeMono.ttf', 23)
    fontcolor = (255, random.randrange(0, 255), random.randrange(0, 255))
    draw.text((5, 2), rand_str[0], font=font, fill=fontcolor)
    draw.text((25, 2), rand_str[1], font=font, fill=fontcolor)
    draw.text((50, 2), rand_str[2], font=font, fill=fontcolor)
    draw.text((75, 2), rand_str[3], font=font, fill=fontcolor)
    del draw
    request.session['verifycode'] = rand_str
    buf = BytesIO()
    im.save(buf, 'png')
    return HttpResponse(buf.getvalue(), 'image/png')


"""当很多页面都使用了某个超链接时   更改了这个超链接的名字 那就无法找到这个页面
此时  就需要反向解析 动态获得 url地址 path('areas/', views.areas, name='index'), 
这里的name参数就是用在反向解析的 
先配置namaspace  path('', include("booktest.urls"), namespace='booktest'),一般都是应用名字
1. """
def url_reverse(request):
    """url反向解析页面"""
    return render(request, 'booktest/url_reverse.html')


def show_wargs(request, a=0, b=0):
    return HttpResponse(str(a)+':'+str(b))


def show_kwargs(request, c=0, d=0):
    return HttpResponse(str(c)+':'+str(d))

from django.urls import reverse
def redict_index(request):
    """通过反向解析 重定向页面"""
    url = reverse('booktest:show_kwargs', kwargs={"c": 3, "d": 4})
    return redirect(url)


# ip禁止装饰器
EXCLUDE_IPS = ['192.168.233.1']
def block_ip(view_func):
    def wrapper(request, *wargs, **kwargs):
        browser_ip = request.META['REMOTE_ADDR']
        if str(browser_ip) in EXCLUDE_IPS:
            return HttpResponse('这个ip已被禁止%s' % browser_ip)
        else:
            return view_func(request, *wargs, **kwargs)
    return wrapper


"""中间件是django框架给我们预留的函数接口 让我们可以干预请求和应答的过程  
例如：禁止某些ip 访问网站
1. 在应用下 新建middleware.py  一般叫这个名字 可以改
2. 在middleware.py创建 中间件类
3. 在中间件类中创建 间件函数  这个函数名字 必须为 process_view()  这是django预留的不可以改 
4. 在settings里的 middleware_classes中注册这个中间件类 
5. 这个中间件类必须继承  jango.utils.deprecation 包里的 MiddlewareMixin类
"""


# @block_ip
def ip_fobbitton(request):
    """这里测试中间件  禁止ip访问"""
    # 1. 使用request的META属性的REMOTE——ADDR获取浏览器的ip
    # 手动的添加禁止列表来禁止 某个 ip访问该网址 但是该ip仍然可以访问该服务iq器其他网址
    # 可以使用装饰器的方式来判断ip是否禁止 以达到同时禁止该ip访问其他网址
    browser_ip = request.META['REMOTE_ADDR']
    print('123456')
    """if str(browser_ip) in EXCLUDE_IPS:
        return HttpResponse('这个ip已被禁止%s' % browser_ip)"""
    return HttpResponse('访问的ip是%s' % browser_ip)


"""下面测试用户上传图片或文件"""
def show_upload(request):
    """显示上传图片页面"""
    return render(request, 'booktest/upload_pic.html')


def upload_action(request):
    """上传图片处理"""
    # 1. 获取上传图片  通过表单提交的图片在request.FILES里
    # request.FILES这个是一个字典  根据上传时指定的名字返回一个上传图片的对象
    # django在存储文件时有两种方式 一种是 当文件小于2.5m 存在内存中 时叫memoryfileuploadhandler
    # 一种是当文件 不小于于2.5m  放在一个临时文件中   temporaryfileuploadhandler
    # 这个对象有一个name属性 即是文件的名字

    image = request.FILES['pic']
    # 2. 创建文件
    save_path = '%s/booktest/images/%s' % (settings.MEDIA_ROOT, image.name)
    with open(save_path, 'wb') as f:
        # 3. 获取上传图片的内容 写到文件中
        # 获取文件内容的方式两种 1. chunks() 将文件分段返回 2. read()将文件一次性返回(非常占用内存 可能造成电脑死机)
        for content in image.chunks():
            f.write(content)
    # 4. 保存上传文件的目录  在数据库中保存上传记录
    PicImage.objects.create(good_pic='booktest/%s' % image.name)
    # 5. 返回
    return HttpResponse('文件上传成功！')


"""下面是分页显示地区"""
from django.core.paginator import Paginator
# 前端访问时应该传过来一个页码  如果不传的话默认就是显示第一页
# 当没有字符传过来时 django默认把参数传递为  空字符串
def show_area(request, pindex):
    """分页  使用django.core.paginator  下Paginator类 """
    # 1. 查询省级地区信息
    # 当进行分页时  查询数据没有进行排序时 就会报警告UnorderedObjectListWarning: Pagination may yield inconsistent results with an
    # unordered object_list: <class 'booktest.models.AreaInfo'> QuerySet.
    areas = AreaInfo.objects.filter(aParent__isnull=True).order_by("id") # 一定要排序
    # 获取分页对象 参数为查询后的查询集   数字表示每页几个
    # paginator类属性有 1. num_pages 返回分页总页数 2. page_range 返回分页后分页的页码列表
    paginator = Paginator(areas, 10)
    # print(paginator.num_pages)
    # print(paginator.page_range)
    # 过去分页的内容   用page参数为要获取的页数 返回page类实例对象

    # page类属性有  object_list 返回包含当前页数据的查询集  pager可直接遍历
    # number返回当前页码
    # paginator返回对应的Paginator对象
    # page实例对象的方法
    # 1. has_previous 判断当前页是否有前一页
    # 2. has_next 判断当前页是否有下一页
    # 3. previous_page_number 返回当前页前一页的页码
    # 3. nest_page_number 返回当前页下一页的页码
    if pindex == '':
        # 判断是否为空  为空 默认取第一页
        pindex = 1
    else:
        pindex = int(pindex)
    pager = paginator.page(pindex)
    # page_list = pager.object_list
    return render(request, 'booktest/show_area.html', {'pager': pager})


"""省市县三级列表"""
def area_three(request):
    """省市县获取"""
    return render(request, 'booktest/areas_three.html')

def prov(request):
    """获取所有省级的地区"""
    # 1. 拿到数据
    areas = AreaInfo.objects.filter(aParent__isnull=True).order_by("id")
    # 2. 遍历areas  并拼接出json数据 ：包含标题 atitle  id 用来获取该省
    areas_list = []
    for area in areas:
        areas_list.append((area.id, area.atitle))
    # 3. 返回数据
    return JsonResponse({'data': areas_list})


"""获取对应省下市的信息"""
def city(request, prov_id):
    """获取prov_id下级地区的信息"""
    # 方式一 先查处这个省 再由一到多查
    # areas_p = AreaInfo.objects.get(id=prov_id)
    # areas = areas_p.areainfo_set.all()
    # 方式二  通过类直接查
    areas_c = AreaInfo.objects.filter(aParent__id=prov_id)
    areas_list = []
    for area in areas_c:
        areas_list.append((area.id, area.atitle))
    # 3. 返回数据
    return JsonResponse({'data': areas_list})


"""获取县级地区并返回json数据"""
def dis(request, city_id):
    """获取prov_id下级地区的信息"""
    # 方式一 先查处这个省 再由一到多查
    # areas_p = AreaInfo.objects.get(id=dis_id)
    # areas = areas_p.areainfo_set.all()
    # 方式二  通过类直接查
    areas_c = AreaInfo.objects.filter(aParent__id=city_id)
    areas_list = []
    for area in areas_c:
        areas_list.append((area.id, area.atitle))
    # 3. 返回数据
    return JsonResponse({'data': areas_list})


"""这里测试 存储redis_session"""
def set_redis_session(request):
    """设置session存在redis里"""
    request.session['redis_username'] = 'aisu'
    request.session['age'] = 18
    return HttpResponse("redis-session设置成功")


def get_redis_session(request):
    """从redis取出session"""
    redis_username = request.session['redis_username']
    age = request.session['age']
    return HttpResponse(redis_username + ":" + str(age))






















