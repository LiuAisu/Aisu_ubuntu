from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
import re
from django.views.generic import View
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.conf import settings
from django.core.mail import send_mail
from celery_tasks.tasks import send_register_active_email
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from utils.maxin import LoginRequireMaxin
from user.models import User, Address
from django_redis import get_redis_connection
from goods.models import GoodsSKU
import os
# Create your views here.
def register(request):
    # 判断请求方式 让同一个页面作不同的事情
    if request.method == 'GET':
        """显示注册页面"""
        temp_path = 'dailyfresh/user/register.html'
        return render(request, temp_path)
    else:
        """进行注册处理"""
        # 接收数据
        user_name = request.POST.get('user_name')
        pass_word = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        cpass_word = request.POST.get('cpwd')
        # 进行数据校验  all方法可以判断可迭代对象的每个数据是否为空
        if not all([user_name, pass_word, email, cpass_word]):
            # 数据不完整
            return render(request, 'dailyfresh/user/register.html', {'errmsg': '数据不完整'})
        try:
            user = User.objects.filter(username=user_name)
        except User.DoesNotExist:
            user = None
        if user:
            return render(request, 'dailyfresh/user/register.html', {'errmsg': '用户名已存在！'})
        if pass_word != cpass_word:
            return render(request, 'dailyfresh/user/register.html', {'errmsg': '输入密码不一致！'})
        re1 = r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$'
        obj = re.compile(re1)
        if not obj.match(email):
            # 三个数据都不为空  校验邮箱
            return render(request, 'dailyfresh/user/register.html', {'errmsg': '邮箱格式不正确'})
        if allow != 'on':
            return render(request, 'dailyfresh/user/register.html', {'errmsg': '请同意协议'})
        # 进行业务处理  进行注册  创建用户  使用认证系统 直接create_user
        """user = User()
        user.username = user_name
        user.password = pass_word
        user.save()"""
        user = User.objects.create_user(user_name, email, pass_word)
        # 创建用户是默认激活的  我们需要通过邮箱激活  所以设置为不激活
        user.is_active = 0
        user.save()
        return redirect(reverse('goods:index'))

"""已经综合到注册视图"""
def register_handle(request):
    """进行注册处理"""
    # 接收数据
    user_name = request.POST.get('user_name')
    pass_word = request.POST.get('pwd')
    email = request.POST.get('email')
    allow = request.POST.get('allow')
    # 进行数据校验  all方法可以判断可迭代对象的每个数据是否为空
    if not all([user_name, pass_word, email]):
        # 数据不完整
        return render(request, 'dailyfresh/user/register.html', {'errmsg': '数据不完整'})
    try:
        user = User.objects.filter(username=user_name)
    except User.DoesNotExist:
        user = None
    if user:
        return render(request, 'dailyfresh/user/register.html', {'errmsg': '用户名已存在！'})
    re1 = r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$'
    obj = re.compile(re1)
    if not obj.match(email):
        # 三个数据都不为空  校验邮箱
        return render(request, 'dailyfresh/user/register.html', {'errmsg': '邮箱格式不正确'})
    if allow != 'on':
        return render(request, 'dailyfresh/user/register.html', {'errmsg': '请同意协议'})
    # 进行业务处理  进行注册  创建用户  使用认证系统 直接create_user
    """user = User()
    user.username = user_name
    user.password = pass_word
    user.save()"""
    user = User.objects.create_user(user_name, email, pass_word)
    # 创建用户是默认激活的  我们需要通过邮箱激活  所以设置为不激活
    user.is_active = 0
    user.save()
    return redirect(reverse('goods:index'))


def regiter_ajax_handle(request):
    username = request.POST.get('user_name')
    password = request.POST.get('password')
    email = request.POST.get('email')
    print(username+password+email)
    return JsonResponse({'res': 1})


# 类视图的使用
"""View里有as_view()函数 将类视图自动转化为视图函数 django自动判断请求类型调用不同的类方法
明确的限定 请求方式不同调用的方法不同"""
class RegisterView(View):
    """注册类视图"""
    def get(self, request):
        """显示注册页面"""
        temp_path = 'dailyfresh/user/register.html'
        return render(request, temp_path)

    def post(self, request):
        """进行注册处理"""
        # 接收数据
        user_name = request.POST.get('user_name')
        pass_word = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        cpass_word = request.POST.get('cpwd')
        # 进行数据校验  all方法可以判断可迭代对象的每个数据是否为空
        if not all([user_name, pass_word, email, cpass_word]):
            # 数据不完整
            return render(request, 'dailyfresh/user/register.html', {'errmsg': '数据不完整'})
        try:
            user = User.objects.filter(username=user_name)
        except User.DoesNotExist:
            user = None
        if user:
            return render(request, 'dailyfresh/user/register.html', {'errmsg': '用户名已存在！'})
        if pass_word != cpass_word:
            return render(request, 'dailyfresh/user/register.html', {'errmsg': '输入密码不一致！'})
        re1 = r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$'
        obj = re.compile(re1)
        if not obj.match(email):
            # 三个数据都不为空  校验邮箱
            return render(request, 'dailyfresh/user/register.html', {'errmsg': '邮箱格式不正确'})
        if allow != 'on':
            return render(request, 'dailyfresh/user/register.html', {'errmsg': '请同意协议'})
        # 进行业务处理  进行注册  创建用户  使用认证系统 直接create_user
        """user = User()
        user.username = user_name
        user.password = pass_word
        user.save()"""
        user = User.objects.create_user(user_name, email, pass_word)
        # 创建用户是默认激活的  我们需要通过邮箱激活  所以设置为不激活
        user.is_active = 0
        user.save()
        # 查询用户id  加密  itsdangerous 包可以加密 还可以设置加密的过期时间  还有几种加密方式
        # 发送激活邮件，  包含激活链接： 设计链接 http://127.0.0.1:8000/user/active/加密后 用户id
        # 激活链接中应该包含 用户的信息，并且加密身份信息
        # Serializer(加密密钥， 加密的过期时间)
        # dumps()返回加密后的信息
        # loads()用来解密  如果加密的东西过期那么 会产生一个错误

        # 加密用户信息 生成激活token
        serializer = Serializer(settings.SECRET_KEY, 3600)
        token_info = {"username": user.username, "user_id": user.id}
        token = serializer.dumps(token_info)
        token_decode = token.decode('utf8')
        # 发送邮件
        """    这里使用celery异步处理
        subject = '刘海俊测试邮件'
        message = ''
        html_message = '<h1>欢迎注册</h1>请点击以下链接激活账户</br><a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>' % (token_decode, token_decode)
        sender = settings.EMAIL_FROM
        receiver = [email]
        # 这里发邮件是阻塞的  我们要使用异步 celery
        send_mail(subject, message, sender, receiver, html_message=html_message)"""
        send_register_active_email.delay(email, user_name, token_decode)
        return redirect(reverse('user:login'), {'errmsg': ''})

class ActiveView(View):
    """用户激活"""
    def get(self, request, token):
        # 进行解密 获取用户信息
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            token_info = serializer.loads(token)
            # print(token_info)
            # 获取用户信息
            user_id = token_info['user_id']
            user = User.objects.get(id=user_id)
            if user.is_active == True:
                return HttpResponse('该用户已激活！')
                #redirect(reverse('user:login'))
            elif user.username == token_info['username']:
                user.is_active = 1
                user.save()
                return redirect(reverse('user:login'))
        except SignatureExpired as e:
            # 激活链接已过期
            return HttpResponse('链接已经过期！')



class LoginView(View):
    def get(self, request):
        """显示登录页面"""
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''
        return render(request, 'dailyfresh/user/login.html', {'username': username, 'checked': checked})

    def post(self, request):
        """登录校验"""
        # 接收数据
        user_name = request.POST.get('username')
        pass_word = request.POST.get('pwd')
        # 校验数据
        if not all([user_name, pass_word]):
            return render(request, 'dailyfresh/user/login.html', {'errmsg': '数据不完整'})
        # 登录 用户名 密码 校验 这里使用django自带认证方法authenticate
        # 登录校验
        user = authenticate(username=user_name, password=pass_word)
        if user is not None:
            if user.is_active:
                # 记录用户的登录状态  使用django认证系统生成session
                login(request, user)
                # 获取登录后所要跳转的地址  默认跳转到首页
                next_url = request.GET.get('next', reverse('goods:index'))
                response = redirect(next_url)
                # 判断用户是否需要记住用户名
                remember_username = request.POST.get('remember_user')
                if remember_username == 'on':
                    # 记住用户名
                    response.set_cookie('username', user_name, max_age=3600)
                else:
                    # print('ssssssssssssssssssssss')
                    response.delete_cookie('username')
                return response
            else:
                # 如果用户没有激活
                email = user.email
                serializer = Serializer(settings.SECRET_KEY, 3600)
                token_info = {"username": user_name, "user_id": user.id}
                token = serializer.dumps(token_info)
                token_decode = token.decode('utf8')
                # 发送 激活 邮件
                send_register_active_email.delay(email, user_name, token_decode)
                return render(request, 'dailyfresh/user/login.html', {'errmsg': '用户尚未激活，已为您重新发送激活邮件'})
        else:
            return render(request, 'dailyfresh/user/login.html', {'errmsg': '用户名或密码不正确'})



# 执行过login()函数的user对象都可以通过request.user获得相关的用户信息
class UserInfoView(LoginRequireMaxin, View):
    """用户中心信息页"""
    def get(self, request):
        """显示用户中心页"""
        # request.auth.authenticated()
        # django会把request.user也传给模板文件
        # 获取用户的个人信息  默认收货地址
        user = request.user
        address = Address.objects.get_default_address(user)
        # 获取用户浏览历史记录
        # strictredis = StrictRedis(host='127.0.0.1', port='6379', db=9)
        # from django_redis import get_redis_connection直接可以返回django配置项里的默认的redis配置对象
        strict_redis = get_redis_connection("default")
        # 取出用户历史浏览记录
        history_key = 'history_%d' % user.id
        # 获取最新的5个商品id  返回一个列表
        sku_ids = strict_redis.lrange(history_key, 0, 4)
        # 从数据库中查询对应id的商品具体信息
        """下面这种方法是先把数据查出来 但是查数据的时候并没有按照原来的顺序返回 因此遍历排序
        goods_li = GoodsSKU.objects.filter(id__in=sku_ids)
        goods_res = []
        for a_id in sku_ids:
            for goods in goods_li:
                if a_id == goods.id:
                    goods_res.append(goods)"""
        # 这种方法是遍历一个id 查一个
        goods_li = []
        for a_id in sku_ids:
            goods = GoodsSKU.objects.filter(id__=a_id)
            goods_li.append(goods)
        # 组织上下文
        content = {'page': 'user',
                   'address': address,
                   'goods_li': goods_li}
        return render(request, 'dailyfresh/user/user_center_info.html', content)


class UserOrderView(LoginRequireMaxin, View):
    """用户中心订单信息页"""
    def get(self, request):
        """显示用户中心页"""
        # 获取用户订单信息

        return render(request, 'dailyfresh/user/user_center_order.html', {'page': 'order'})


class UserAddressView(LoginRequireMaxin, View):
    """用户中心信息页"""
    def get(self, request):
        """显示用户中心页"""
        # 获取用户默认地址信息
        user = request.user  # 登录的用户对应的User对象
        """try:
            address = Address.objects.get(user=user, is_default=True)
        except Address.DoesNotExist:
            # 不存在默认收获地址
            address = None"""
        address = Address.objects.get_default_address(user)
        return render(request, 'dailyfresh/user/user_center_site.html', {'page': 'address', 'address': address})

    def post(self, request):
        # 获取用户提交的地址信息
        receiver_name = request.POST.get('receiver')
        receiver_address = request.POST.get('address')
        zip_code = request.POST.get('zip_code')
        phone_num = request.POST.get('phone')
        # 校验数据
        if not all([receiver_name, receiver_address, phone_num]):
            return render(request, 'dailyfresh/user/user_center_site.html', {'errmsg': '数据不完整！'})
        # 校验手机号
        if not re.match(r'^1[3|4|5|7|8][0-9]{9}$', phone_num):
            return render(request, 'dailyfresh/user/user_center_site.html', {'errmsg': '手机号码格式不正确！'})

        # 业务处理：地址添加
        # 如果用户已存在默认收货地址， 添加的地址不作为默认地址否则作为默认地址
        user = request.user  # 登录的用户对应的User对象
        """try:
            address = Address.objects.get(user=user, is_default=True)
        except Address.DoesNotExist:
            # 不存在默认收获地址
            address = None"""
        address = Address.objects.get_default_address(user)
        if address:
            is_default = False
        else:
            is_default = True
        # 添加地址
        Address.objects.create(user=user,
                               receiver=receiver_name,
                               addr=receiver_address,
                               zip_code=zip_code,
                               phone=phone_num,
                               is_default=is_default)
        # 返回应答
        return redirect(reverse('user:address'))


class LogOutView(LoginRequireMaxin, View):
    def get(self, request):
        """退出登录"""
        # 清除session
        logout(request)
        return redirect(reverse('goods:index'))
















