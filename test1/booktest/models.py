from django.db import models
from datetime import date
# Create your models here.


# 有关系时就把少的较一类多的叫多类
# 一类
# 图书类



class BookInfo(models.Model):
    """图书模型类"""

    btitle = models.CharField (max_length=20)
    bpub_date = models.DateField()
    objects = models.Manager()

    # 增加 bread 阅读量 和 bcomment 评论量 属性
    # bread = models.IntegerField(default=0)
    # bcomment = models.IntegerField(default=0)
    # 是否删除  默认不删除  作软删除标记
    # is_delete = models.BooleanField(default=False)

    """可以在这里面重写方法 改变返回值如下"""
    # 返回书名
    def __str__(self):
        return self.btitle

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
    # is_delete = models.BooleanField(default=False)
    # 返回英雄名
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
