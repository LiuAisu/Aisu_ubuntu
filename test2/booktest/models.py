from django.db import models
from datetime import date
# Create your models here.
from tinymce.models import HTMLField

class BookInfomanageer(models.Manager):
    """图书模型管理器类"""
    # 作用
    # 1. 改变查询结果集
    def all(self):
        # 1. 调用父类all()方法   获取所有数据
        books = super().all()   # 返回数据是一个查询集query
        # 对数据进行过滤  筛选出 is_delete=0的数据
        books = books.filter(is_delete=False)
        # 返回books
        return books

    # 2. 封装函数：操作模型类对应的数据表  增删改查
    def create_book(self, btitle, bpub_date):
        # 1.创建模型类对象
        # 获取self所在的模型类   self 是这个模型管理器类实例对象  self.model能够直接得到管理器类实例 对象 所在的模型类的类名
        model_class = self.model
        # book = BookInfo()
        book = model_class()
        book.btitle = btitle
        book.bpub_date = bpub_date
        book.save()
        # 返回对象
        return book


# 有关系时就把少的较一类多的叫多类
# 一类
# 图书类
# 当已经做好了数据表 后改变应用的名称 此时会导致找不到数据表  要想模型类对应的 表不依赖于应用名  就需要使用  元选项  指定表名

class BookInfo(models.Model):
    """图书模型类"""

    btitle = models.CharField(max_length=20)
    # 日期类型两个可选参数 auto_now和auto_now_add 默认都为False
    # auto_now_add=True时自动把当前时间加进去(创建时间)  auto_now=True代表更新时间  两个只能用一个
    bpub_date = models.DateField()
    # TimeField表示时间  DateTimeField表示日期时间  也有auto_now和auto_now_add两个参数
    objects = BookInfomanageer()

    # 增加 bread 阅读量 和 bcomment 评论量 属性
    bread = models.IntegerField(default=0)
    bcomment = models.IntegerField(default=0)
    # 是否删除  默认不删除  作软删除标记
    is_delete = models.BooleanField(default=False)

    # 两种文件字段
    # FileField  用于上传文件字段   ImageField用于上传图片
    """可以在这里面重写方法 改变返回值如下"""
    # 返回书名
    def __str__(self):
        return self.btitle

    # 当已经做好了数据表 后改变应用的名称 此时会导致找不到数据表  要想模型类对应的 表不依赖于应用名  就需要使用  元选项  指定表名
    # 定义一个元类 在元类里指定表名
    class Meta:
        db_table = 'bookinfo'  # 指定模型类对应的表名

"""# 向数据表插入数据
b = BookInfo()
b.btitle = '天龙八部'
b.bpub_date = date(1990, 1, 1)
b.save()
b = BookInfo()
b.btitle = '天龙八部'
b.bpub_date = date(1990, 1, 1)
b.save()
# 从数据表查询数据
# 返回值是一个BookInfo的实例对象  作用是根据输入条件从数据库查询出来 保存到b1这个实例对象里面
b1 = BookInfo.objects.get(id=1)
print(b1.btitle)
# 更改数据库内容  直接用b1对象来改 改完后save
b1.btitle='三国演义'
b1.save()
# 删除改条数据
b1.delete()"""

# 一本图书可能有很多个英雄 所以英雄表和图书表是有关系的
# 关系属性 建立图书类和英雄人物类一对多关系
# 多类   创建关系属性即创建外键


class HeroInfo(models.Model):
    """英雄模型类"""
    hname = models.CharField(max_length=20)
    # bool类型 性别   False代表男
    hgender = models.BooleanField(default=False)
    # 备注
    hcomment = models.CharField(max_length=128)
    # 添加外键和之前不同  要加on_delete=models.CASCADE 且
    # 可以不加名字 但外键要在主表上面！！！！
    hbook = models.ForeignKey("BookInfo", on_delete=models.CASCADE)  #!!!定义外键一定要加 on_delete=
    # 假如图书表 10本图书  英雄表100个英雄 英雄可能属于不同的书  即外键就是图书表的主键
    # 使用默认的管理工具
    objects = models.Manager()
    # 是否删除  默认不删除  作软删除标记
    is_delete = models.BooleanField(default=False)

    # decimalfield  小数 max_digits 总位数 decimal_paaces小数位数
    # price = models.DecimalField(max_digits=10, decimal_places=2)

    # 返回英雄名  这里作后台管理使用
    def __str__(self):
        return self.hname

"""from booktest.models import BookInfo
from booktest.models import HeroInfo
b = BookInfo.objects.get(id=4)
h = HeroInfo()
h.hname = '段誉'
h.hgender = True
h.hcomment = '六脉神剑'
h.hbook = b
h.save()"""


# Create your models here.
# 1.生成迁移文件   python manage.py makemigrations
# 2.执行迁移   python manage.py migrate

#
# sudo vi /etc/mysql/mysql.conf.d/mysqld.cnf


class AreaInfo(models.Model):
    # objects是models.Manager()对象   模型管理器对象
    objects = models.Manager()
    # 地区名称  如果想指定  类属性显示的标题  则需要增加verbose_name参数
    atitle = models.CharField(verbose_name='地区名称', max_length=20)
    # 关系属性  代表当前地区的父级   blank=True代表在后台管理也可为空
    # 这里建立的代表和自身相关联    也是一种特殊的一对多
    aParent = models.ForeignKey('self', verbose_name='父级地区名称', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.atitle

    # 也可以写方法
    def view_title(self):
        return self.atitle

    def view_parent(self):
        parent = self.aParent
        if parent:
            return parent.atitle
        else:
            return "Null"
    # 如果想让 自己定义的方法对应的列也能点击 需要给对应类中对应方法 加一个属性 admin_order_field
    # 如果想给对应方法  指定标题的名字也需要加属性
    view_title.admin_order_field = 'id'
    view_title.short_description = '地区名称'


# 这个类测试后台上传图片或者文件
class PicImage(models.Model):
    objects = models.Manager()
    """这里的upload_to 属性指定要上传的目录 这个目录是相对于media的"""
    good_pic = models.ImageField(upload_to='booktest/images')

    def __str__(self):
        # 这个name就是文件的名字 指的是在数据库存在记录的名字
        return self.good_pic.name


class Htmlfield_Choice_test(models.Model):
    """测试富文本和choice"""
    status_choices = (
        (0, '下架'),
        (0, '上架'),
    )
    status = models.SmallIntegerField(default=1, choices=status_choices, verbose_name='商品状态')
    detail = HTMLField(verbose_name='商品详情')

    class Meta:
        db_table = 'df_goods_test'


