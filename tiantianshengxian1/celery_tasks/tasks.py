import django
from celery import Celery
from django.conf import settings
from django.core.mail import send_mail
import os
from django.template import loader, RequestContext
from django.shortcuts import render
from django_redis import get_redis_connection
# 在任务处理者一端也是需要加载django环境的初始化   这段初始化代码放在任务处理者那里！！！
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tiantianshengxian.settings')
django.setup()
# 导入这类需要在上面django配置下面 否则 在celery worker启动时就会报错
from goods.models import GoodsType, IndexTypeGoodsBanner, IndexPromotionBanner, IndexGoodsBanner
"""celery的任务发出者  中间人  任务的处理者可以在不同的电脑上
处理者也需要任务的代码"""
# 启动任务的处理者  celery -A 创建的Celery对象(app 这个名字不能改)
# 创建一个celery的实例对象
# 参数 celery_tasks.tasks 第一个是给celery起一个名字  一般是路径
# 参数 broker 中间人  这里使用的是redis     使用数据库
redis_server = ''
app = Celery('celery_tasks.tasks', broker='redis://:ss123456@127.0.0.1:6379/8')
# 定义任务函数


@app.task
def send_register_active_email(to_email, username, token):
    # 发送邮件
    subject = '刘海俊测试邮件'
    message = ''
    html_message = '<h1>%s，欢迎注册</h1>请点击以下链接激活账户' \
                   '</br><a href="http://127.0.0.1:8000/user/active/%s">' \
                   'http://127.0.0.1:8000/user/active/%s</a>' % (username, token, token)
    sender = settings.EMAIL_FROM
    receiver = [to_email]
    # 这里发邮件是阻塞的  我们要使用异步 celery
    send_mail(subject, message, sender, receiver, html_message=html_message)

@app.task
def generate_static_index_html():
    """产生首页静态页面"""
    # 获取商品种类信息
    types = GoodsType.objects.all()
    # 获取首页轮播商品信息
    goods_banners = IndexGoodsBanner.objects.all().order_by('index')
    # 获取商品促销活动信息
    promotion_banners = IndexPromotionBanner.objects.all().order_by('index')
    # 获取首页分类商品展示信息
    for type_eve in types:
        image_banners = IndexTypeGoodsBanner.objects.filter(type=type_eve, display_type=1).order_by('index')
        title_banners = IndexTypeGoodsBanner.objects.filter(type=type_eve, display_type=0).order_by('index')
        type_eve.image_banners = image_banners
        type_eve.title_banners = title_banners
    context = {
        'types': types,
        'goods_banners': goods_banners,
        'promotion_banners': promotion_banners}
    # 不需要返回HttpResponse对象
    # 使用常规渲染
    # return render(request, 'dailyfresh/goods/index.html', context)
    temp = loader.get_template('dailyfresh/goods/static_index.html')
    # 渲染模板
    static_index_html = temp.render(context)
    # 生成静态页面  返回替换后的html内容
    save_path = os.path.join(settings.BASE_DIR, 'static/dailyfresh/index.html')
    with open(save_path, 'w') as f:
        f.write(static_index_html)












