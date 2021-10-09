import os.path
import ssl
# 关闭证书验证   非常重要  不关闭将导致 交易查询接口打不开
ssl._create_default_https_context = ssl._create_unverified_context
import time
from django.shortcuts import render, redirect, reverse
from django.views import View
from utils.maxin import LoginRequireMaxin
from goods.models import GoodsSKU
from django_redis import get_redis_connection
from user.models import Address
from django.http import JsonResponse
from order.models import OrderInfo, OrderGoods
from datetime import datetime
from django.db import transaction
from django.conf import settings
from alipay import AliPay, DCAliPay, ISVAliPay
from alipay.utils import AliPayConfig
from signal import signal, SIGPIPE, SIG_DFL
# Create your views here.


"""下面显示提交订单页面 
当<form></form> 中的checkbox被选中时  提交的表单会自动的提交表单中被选中的checkbox的值
但是此时我们设置的提交名字都是相同的
requests.POST里的是Querydict的数据  允许一个键对应对个值  但取时要用requests.POST.getlist而不是requests.POST.get了！！！
"""
class OrderPlaceView(LoginRequireMaxin, View):
    """提交订单页面显示"""

    def post(self, request):
        # 获取登录用户
        user = request.user
        # 获取post提交的表单数据  即商品的id: sku_ids
        sku_ids = request.POST.getlist('sku_ids')
        # 校验参数
        if not sku_ids:
            # 跳转到购物车页面
            return redirect(reverse('cart:show'))
        # 建立redis链接
        conn = get_redis_connection('default')
        # 组织cart_key
        cart_key = 'cart_%d' % user.id
        # 遍历 sku_ids 获取用户要购买的商品信息和数量
        skus = []
        # 定义总金额和总数量
        total_count = 0
        total_price = 0
        for sku_id in sku_ids:
            sku = GoodsSKU.objects.get(id=sku_id)
            # 获取用户要购买商品的数量
            count = conn.hget(cart_key, sku_id)
            # 计算商品的小计
            amount = sku.price * int(count)
            # 动态的给sku增加属性保存购买商品的数量和小计
            sku.count = int(count)
            sku.amount = amount
            skus.append(sku)
            # 累加商品的总价格和总数量
            total_count = total_count + int(count)
            total_price = total_price + amount
        # 运费再实际开发中是需要一个单独模块的  在这里我们定死
        transit_price = 10
        # 实付款
        total_pay = transit_price + total_price
        # 还需要用户的收件地址   所有的地址
        addrs = Address.objects.filter(user=user)
        # 把商品id组成的列表变成以,分割的字符串在传递回页面 为提交订单使用
        sku_ids = ",".join(sku_ids)  # [1,5]  --> 1,5
        # 组织模板上下文
        context = {
            'total_count': total_count,
            'total_price': total_price,
            'skus': skus,
            'transit_price': transit_price,
            'total_pay': total_pay,
            'addrs': addrs,
            'sku_ids': sku_ids
        }
        return render(request, 'dailyfresh/order/place_order.html', context)


"""
订单创建 需要传来的参数  
收货地址addr_id，支付方式pay_method， 商品id:sku_ids
这个也需要用户登录的

订单的创建是需要向两个表都添加数据的 如果第一个表加了数据但是到第二个失败， 此时应该都不加数据
此时使用到mysql事务！！！！！  
djando 使用事务需要 from  django.db import transaction 里的atomic对函数进行装饰
事务 1.原子性 2.稳定性 3.隔离性 4.可靠性
订单的并发问题  解决方案：
1. 悲观锁 在查询时后面加update 就可以创建锁  先拿到锁的往下走 没拿到锁的需要等待锁释放
    sku = GoodsSKU.objects.get(id=sku_id)
    sku = GoodsSKU.objects.select_for_update(id=sku_id)
2. 乐观锁  在查询数据时不加锁 但在修改数据时进行判断当前数据和之前查出来的数据是否相同
3. 使用乐观锁会出现不能重读提交的数据 
 这里需要在mysql的配置文件 改变其隔离性级别为 可读取提交的内容
 但是在django2.0以上  django自动的把级别改为可读提交内容
 
 在冲突比较少时 我们使用乐观锁    提高性能
 在冲突多时使用悲观锁
"""


# 使用悲观锁
class OrderCommit(LoginRequireMaxin, View):
    """订单创建 transaction.atomic 装饰的函数 其中涉及到mysql操作将自动执行事务
    如果要使用保存点 则用 transaction.savepoint()
    保存点提交transaction.savepoint_commit()
    回滚到保存点 transaction.rollback()
    """
    @transaction.atomic
    def post(self, request):
        # 判断用户是否登录
        user = request.user
        if not user.is_authenticated:
            # 用户未登录
            return JsonResponse({'res': 0, 'errmsg': '请登录'})
        # 接收参数
        addr_id = request.POST.get('addr_id')
        pay_method = request.POST.get('pay_method')
        sku_ids = request.POST.get('sku_ids')
        # 校验参数
        if not all([addr_id, pay_method, sku_ids]):
            return JsonResponse({'res': 1, 'errmsg': '参数不完整'})
        # 校验支付方式
        if pay_method not in OrderInfo.PAY_METHODS.keys():
            return JsonResponse({'res': 2, 'errmsg': '非法支付方式'})
        # 校验地址
        try:
            addr = Address.objects.get(id=addr_id)
        except Address.DoesNotExist:
            return JsonResponse({'res': 3, 'errmsg': '地址非法'})
        # 创建订单核心业务：
        # 用户每下一个订单就需要在订单信息表df_order_info加一条记录
        # 创建订单信息记录  缺少的参数 order_id ，total_count ，total_price， transit_price
        # 组织参数
        # 订单id: 年月日时分秒+用户的id  strftime('%Y%m%d%H%M%S')把时间格式化为字符串
        order_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(user.id)

        # 运费 默认10
        transit_price = 10
        # 总数量和总金额
        total_count = 0
        total_price = 0

        # 设置保存点
        save_id = transaction.savepoint()
        try:
            order = OrderInfo.objects.create(order_id=order_id,
                                             user=user, addr=addr,
                                             pay_method=pay_method,
                                             total_count=total_count,
                                             total_price=total_price,
                                             transit_price=transit_price)

            # 用户订单中有几个商品就需要向订单商品表df_order_goods加几条记录
            sku_ids = sku_ids.split(',')  # [1,2,3]
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            for sku_id in sku_ids:
                try:
                    # 尝试获取商品 判断商品是否存在
                    # sku = GoodsSKU.objects.get(id=sku_id)
                    sku = GoodsSKU.objects.select_for_update().get(id=sku_id)
                except GoodsSKU.DoesNotExist:
                    # 商品不存在
                    # 回滚到保存点
                    transaction.savepoint_rollback(save_id)
                    return JsonResponse({'res': 4, 'errmsg': '商品不存在'})
                    # 从redis获取萨和嗯品数量
                count = conn.hget(cart_key, sku_id)
                # 判断商品的库存 如果两个人同时提交订单  就需要判断商品库存
                if int(count) > sku.stock:
                    transaction.savepoint_rollback(save_id)
                    return JsonResponse({'res': 6, 'errmsg': '商品库存不足'})
                # 向df_order_goods加一条记录
                OrderGoods.objects.create(order=order, sku=sku, count=count, price=sku.price)

                # 商品的销量库存更新
                sku.stock = sku.stock - int(count)
                sku.sales = sku.sales + int(count)
                sku.save()

                # 累加计算订单商品总数量和总价格
                amount = sku.price*int(count)
                total_count = total_count+int(count)
                total_price = total_price+amount
            # 更新订单信息表中的商品总数量和总价格
            order.total_count = total_count
            order.transit_price = total_price
            order.save()
        except Exception as e:
            print(e)
            transaction.savepoint_rollback(save_id)
            return JsonResponse({'res': 7, 'errmsg': '下单失败'})
        # 如果都没问题那么 提交事务
        transaction.savepoint_commit(save_id)
        # 清除用户购物车对应记录 把列表当未知参数在列表前加*相当于拆包
        conn.hdel(cart_key, *sku_ids)
        return JsonResponse({'res': 5, 'errmsg': '订单提交成功'})


# 使用乐观锁
class OrderCommit1(LoginRequireMaxin, View):
    """订单创建 transaction.atomic 装饰的函数 其中涉及到mysql操作将自动执行事务
    如果要使用保存点 则用 transaction.savepoint()
    保存点提交transaction.savepoint_commit()
    回滚到保存点 transaction.rollback()
    """
    @transaction.atomic
    def post(self, request):
        # 判断用户是否登录
        user = request.user
        if not user.is_authenticated:
            # 用户未登录
            return JsonResponse({'res': 0, 'errmsg': '请登录'})
        # 接收参数
        addr_id = request.POST.get('addr_id')
        pay_method = request.POST.get('pay_method')
        sku_ids = request.POST.get('sku_ids')
        # 校验参数
        if not all([addr_id, pay_method, sku_ids]):
            return JsonResponse({'res': 1, 'errmsg': '参数不完整'})
        # 校验支付方式
        if pay_method not in OrderInfo.PAY_METHODS.keys():
            return JsonResponse({'res': 2, 'errmsg': '非法支付方式'})
        # 校验地址
        try:
            addr = Address.objects.get(id=addr_id)
        except Address.DoesNotExist:
            return JsonResponse({'res': 3, 'errmsg': '地址非法'})
        # 创建订单核心业务：
        # 用户每下一个订单就需要在订单信息表df_order_info加一条记录
        # 创建订单信息记录  缺少的参数 order_id ，total_count ，total_price， transit_price
        # 组织参数
        # 订单id: 年月日时分秒+用户的id  strftime('%Y%m%d%H%M%S')把时间格式化为字符串
        order_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(user.id)

        # 运费 默认10
        transit_price = 10
        # 总数量和总金额
        total_count = 0
        total_price = 0

        # 设置保存点
        save_id = transaction.savepoint()
        try:
            order = OrderInfo.objects.create(order_id=order_id,
                                             user=user, addr=addr,
                                             pay_method=pay_method,
                                             total_count=total_count,
                                             total_price=total_price,
                                             transit_price=transit_price)

            # 用户订单中有几个商品就需要向订单商品表df_order_goods加几条记录
            sku_ids = sku_ids.split(',')  # [1,2,3]
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            for sku_id in sku_ids:
                for i in range(3):
                    try:
                        # 尝试获取商品 判断商品是否存在
                        sku = GoodsSKU.objects.get(id=sku_id)
                        # sku = GoodsSKU.objects.select_for_update().get(id=sku_id)
                    except GoodsSKU.DoesNotExist:
                        # 商品不存在
                        # 回滚到保存点
                        transaction.savepoint_rollback(save_id)
                        return JsonResponse({'res': 4, 'errmsg': '商品不存在'})
                        # 从redis获取商品数量
                    count = conn.hget(cart_key, sku_id)
                    # 判断商品的库存 如果两个人同时提交订单  就需要判断商品库存
                    if int(count) > sku.stock:
                        transaction.savepoint_rollback(save_id)
                        return JsonResponse({'res': 6, 'errmsg': '商品库存不足'})
                    # 商品的销量库存更新
                    """sku.stock = sku.stock - int(count)
                    sku.sales = sku.sales + int(count)
                    sku.save()"""
                    orgin_stock = sku.stock
                    new_stock = orgin_stock - int(count)
                    new_sales = orgin_stock + int(count)
                    # update df_goods_sku set stock=new_stock, sales=new_sales
                    res = GoodsSKU.objects.filter(id=sku_id, stock=orgin_stock).update(stock=new_stock, sales=new_sales)
                    # 返回受到影响的行数
                    if res == 0:
                        # 尝试3次都不成功
                        if i == 2:
                            transaction.savepoint_rollback(save_id)
                            return JsonResponse({'res': 8, 'errmsg': '下单失败'})
                        else:
                            continue
                    # 向df_order_goods加一条记录
                    OrderGoods.objects.create(order=order, sku=sku, count=count, price=sku.price)
                    # 累加计算订单商品总数量和总价格
                    amount = sku.price*int(count)
                    total_count = total_count+int(count)
                    total_price = total_price+amount
                    # 如果没出错直接成功 跳出循环
                    break
            # 更新订单信息表中的商品总数量和总价格
            order.total_count = total_count
            order.transit_price = total_price
            order.save()
        except Exception as e:
            transaction.savepoint_rollback(save_id)
            return JsonResponse({'res': 7, 'errmsg': '下单失败'})
        # 如果都没问题那么 提交事务
        transaction.savepoint_commit(save_id)
        # 清除用户购物车对应记录 把列表当未知参数在列表前加*相当于拆包
        conn.hdel(cart_key, *sku_ids)
        return JsonResponse({'res': 5, 'errmsg': '订单提交成功'})



"""订单支付界面  python 使用支付宝 pip install alipay-sdk-python
生成电脑私爻rsar genrsa -out app_private.pem 2048
前端需要传过来 1. 订单编号 
1. 让这个类去接入支付宝
"""
class OrderPayView(LoginRequireMaxin, View):
    """订单支付"""
    def init_alipay(self):
        app_private_key_string = open(os.path.join(settings.BASE_DIR, 'apps/order/app_private_key.pem')).read()
        alipay_public_key_string = open(os.path.join(settings.BASE_DIR, 'apps/order/alipay_public_key.pem')).read()
        # print(alipay_public_key_string)
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调 url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=True,  # 默认 False
            # verbose=False,  # 输出调试数据
            config=AliPayConfig(timeout=15)  # 可选，请求超时时间
        )
        return alipay
    # print(app_private_key_string)
    def post(self, request):
        try:
            user = request.user
            if not user.is_authenticated:
                # 用户未登录
                return JsonResponse({'res': 0, 'errmsg': '请登录'})
            # 接收参数
            order_id = request.POST.get('order_id')
            # 校验参数
            if not order_id:
                return JsonResponse({'res': 1, 'errmsg': '无效的订单id'})
            try:
                order = OrderInfo.objects.get(order_id=order_id, user=user, pay_method=3, order_status=1)
            except OrderInfo.DoesNotExist:
                return JsonResponse({'res': 2, 'errmsg': '无效的订单'})
            # 业务处理 ：使用python sdk调用支付宝的支付接口
            # 初始化
            alipay = self.init_alipay()
            # 调用支付接口
            total_pay = order.total_price + order.transit_price
            order_string = alipay.api_alipay_trade_page_pay(
                out_trade_no=order_id,  # 订单id
                total_amount=str(total_pay),  # 订单总金额
                subject='刘海俊测试支付%s' % order_id,
                return_url=None,
                notify_url=None,
            )
            # time.sleep(5)
            pay_url = 'https://openapi.alipaydev.com/gateway.do' + '?' + order_string
            # return redirect(pay_url)
            # print('13456789')
            return JsonResponse({'res': 3, 'pay_url': pay_url})
        except Exception as e:
            print(e)


"""查看订单的付款结果"""
class OrderCheckView(LoginRequireMaxin, View):
    def init_alipay(self):
        app_private_key_string = open(os.path.join(settings.BASE_DIR, 'apps/order/app_private_key.pem')).read()
        alipay_public_key_string = open(os.path.join(settings.BASE_DIR, 'apps/order/alipay_public_key.pem')).read()
        # print(alipay_public_key_string)
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调 url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=True,  # 默认 False
            # verbose=False,  # 输出调试数据
            config=AliPayConfig(timeout=15)  # 可选，请求超时时间
        )
        return alipay

    def post(self, request):
        """查询支付结果"""
        user = request.user
        if not user.is_authenticated:
            # 用户未登录
            return JsonResponse({'res': 0, 'errmsg': '请登录'})
        # 接收参数
        order_id = request.POST.get('order_id')
        # 校验参数
        if not order_id:
            return JsonResponse({'res': 1, 'errmsg': '无效的订单id'})
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user, pay_method=3, order_status=1)
        except OrderInfo.DoesNotExist:
            return JsonResponse({'res': 2, 'errmsg': '无效的订单'})
        alipay = self.init_alipay()
        # 调用支付查询接口
        # 返回值是一个字典
        while True:
            result = alipay.api_alipay_trade_query(out_trade_no=order_id, trade_no=None)
            # print(result)
            """ response = {
                "alipay_trade_query_response": {
                        "trade_no": "2017032121001004070200176844",  支付宝交易号
                        "code": "10000",   支付接口调用状态
                        "invoice_amount": "20.00",
                        "open_id": "20880072506750308812798160715407",
                        "fund_bill_list": [
                            {
                                "amount": "20.00",
                                "fund_channel": "ALIPAYACCOUNT"
                            }
                        ],
                        "buyer_logon_id": "csq***@sandbox.com",
                        "send_pay_date": "2017-03-21 13:29:17",
                        "receipt_amount": "20.00",
                        "out_trade_no": "out_trade_no15",
                        "buyer_pay_amount": "20.00",
                        "buyer_user_id": "2088102169481075",
                        "msg": "Success",
                        "point_amount": "0.00",
                        "trade_status": "TRADE_SUCCESS",   订单状态
                        "total_amount": "20.00"
                    },
                    "sign": ""
                }"""
            code = result.get('code')
            if  code == '10000' and result.get('trade_status') == 'TRADE_SUCCESS':
                # 订单支付成功
                # 获取支付宝交易号
                trade_no = result.get('trade_no')
                # 更新数据库订单状态
                order.trade_no = trade_no
                order.order_status = 4
                order.save()
                # 返回结果
                return JsonResponse({'res': 3, 'errmsg': '支付成功'})
            elif code == '40004' or (code == '10000' and result.get('trade_status') == 'WAIT_BUYER_PAY'):
                # 订单等待用户支付
                # 等待几秒再次查询
                time.sleep(5)
                continue
            else:
                # 支付出错
                return JsonResponse({'res': 4, 'errmsg': '支付失败'})



"""评论"""
class OrderCommentView(LoginRequireMaxin, View):
    def get(self, request, order_id):
        """获取订单id打开评论页面"""
        user = request.user
        if not user.is_authenticated:
            # 用户未登录
            return redirect(reverse('user:order'))
        # 校验参数
        if not order_id:
            return redirect(reverse('user:order'))
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user)
        except OrderInfo.DoesNotExist:
            return redirect(reverse('user:order'))
        # 获取订单状态标题
        order_status_name = OrderInfo.ORDER_STATUS[order.order_status]
        # 获取订单商品信息
        order_skus = OrderGoods.objects.filter(order_id=order_id)
        for order_sku in order_skus:
            # 计算商品的小计
            amount = order_sku.price*order_sku.count
            # 动态给商品加小计属性
            order_sku.amount = amount
        # 动态给订单添加商品属性
        order.order_skus = order_skus
        # 使用模板
        # print('123456')
        return render(request, 'dailyfresh/order/order_coment.html', {'order': order})

    def post(self, request, order_id):
        """处理评论内容"""
        """获取订单id打开评论页面"""
        user = request.user

        if not user.is_authenticated:
            # 用户未登录
            return redirect(reverse('order:comment'))
        # 校验参数
        if not order_id:
            return redirect(reverse('order:comment'))
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user)
        except OrderInfo.DoesNotExist:
            return redirect(reverse('order:comment'))
        # 获取评论总数
        total_count = int(request.POST.get('total_count'))
        for i in range(1, total_count+1):
            # 获取评论的商品id
            sku_id = request.POST.get('sku_%d' % i)
            # 获取对应评论
            comment = request.POST.get('content_%d' % i)
            try:
                order_good = OrderGoods.objects.get(order=order, sku_id=sku_id)
            except OrderGoods.DoesNotExist:
                continue
            order_good.comment = comment
            order_good.save()
        order.order_status = 5
        order.save()
        return redirect(reverse('user:order', kwargs={'page_index': 1}))
















