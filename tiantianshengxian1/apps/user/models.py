from django.db import models
from dbmodel.base_model import BaseModel
from django.conf import settings
from django.contrib.auth.models import AbstractUser
# itsdangerous内部默认使用了HMAC和SHA1来签名，基于 Django 签名模块。
# 它也支持JSON Web 签名 (JWS)。这个库采用BSD协议，由Armin Ronacher编写，
# 而大部分设计与实现的版权归Simon Willison和其他的把这个库变为现实的Django爱好者们。
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
# Create your models here.


"""
在自己创建user类时需要在setting加配置    否则将和django自己创建的user类冲突
AUTH_USER_MODEL = 'user.User'  #  其中user为app名称，User为模型类名称
"""
class User(BaseModel, AbstractUser):
    """用户模型类"""
    def generate_active_token(self):
        """生成用户签名字符串"""
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm': self.id}
        token = serializer.dumps(info)
        return token.decode()
    class Meta:
        db_table = 'df_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name


class AddressManager(models.Manager):
    """地址模型管理类"""
    # 1. 改变原有方法查询结果集all()
    # 2. 封装方法：用户操作模型类对应的数据表（增删改查）
    def get_default_address(self, user):
        """获取用户的默认地址"""
        # self.model 可以获取self所在模型类
        try:
            address = self.get(user=user, is_default=True)
        except self.model.DoesNotExist:
            # 不存在默认收获地址
            address = None
        return address

class Address(BaseModel):
    """地址模型类"""
    objects = AddressManager()
    user = models.ForeignKey('User', on_delete=models.CASCADE, verbose_name='所属账户')
    receiver = models.CharField(max_length=20, verbose_name='收件人')
    addr = models.CharField(max_length=256, verbose_name='收件地址')
    zip_code = models.CharField(max_length=6, null=True, verbose_name='邮政编码')
    phone = models.CharField(max_length=11, verbose_name='联系电话')
    is_default = models.BooleanField(default=False, verbose_name='是否默认')
    # 元选项指定表名  这样模型类对应表名就不依赖 应用名字了
    class Meta:
        db_table = 'df_adreess'
        verbose_name = '地址'
        verbose_name_plural = verbose_name

