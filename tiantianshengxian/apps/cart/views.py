from django.shortcuts import render
from django.views import View
from utils.maxin import LoginRequireMaxin
from django.http import JsonResponse
from goods.models import GoodsSKU
from django_redis import get_redis_connection
# Create your views here.

class CartView(LoginRequireMaxin, View):
    def get(self, request):
        """显示购物车"""
        # 获取登录用户
        user = request.user
        # 查询redis购物车数据
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        # 先尝试是否有购物车这个商品 获取hash所有的属性用 hgetall(key)  返回值是一个字典
        # {'商品id': 商品数量}
        try:
            cart_dict = conn.hgetall(cart_key)
        except Exception as e:
            return render(request, 'dailyfresh/cart/cart.html')
        # 遍历字典获取商品的信息  cart_dict.items()
        skus = []
        # 保存总数量  和  总价格
        total_count = 0
        total_price = 0
        for sku_id, count in cart_dict.items():
            # 根据商品的id查询商品信息
            sku = GoodsSKU.objects.get(id=sku_id)
            # 计算商品小计  amount=数量*单价
            amount = sku.price*int(count)
            # 保存对应商品对象和小计算   可以动态的给sku商品对象增加属性 保存商品的小计  在首页和列表页也使用到了
            sku.amount = amount
            # 增加属性count保存对应商品数量
            sku.count = int(count)
            skus.append(sku)
            # 累加计算商品总数量和总价格
            total_count += int(count)
            total_price += amount
        # 组织模板上下文
        context = {
            'total_count': total_count,
            'total_price': total_price,
            'skus': skus
        }
        return render(request, 'dailyfresh/cart/cart.html', context)


# 在购物车页面 更新购物车数据
# 采用ajax post请求
class CartUpdateView(View):
    """购物车记录更新"""
    def post(self, request):
        """购物车记录更新"""
        # 判断用户是否登录
        if not request.user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})
            # 接收数据
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')
        # 数据校验
        if not all([sku_id, count]):
            return JsonResponse({'res': 1, 'errmsg': '数据不完整'})
        # 校验添加商品数量
        try:
            count = int(count)
        except Exception as e:
            return JsonResponse({'res': 2, 'errmsg': '商品数目出错'})
        # 检验商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except Exception as e:
            return JsonResponse({'res': 3, 'errmsg': '商品不存在'})
        user = request.user
        # 业务处理:添加购物车记录
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        # 业务处理： 增加或减少购物车数量
        # 校验商品的库存
        if count > sku.stock:
            return JsonResponse({'res': 4, 'errmsg': '商品库存不足'})
        # 设置hash中sku_id对应的值
        conn.hset(cart_key, sku_id, count)
        # 统计购物车中商品的总件数
        total_count = 0
        vals = conn.hvals(cart_key)
        for val in vals:
            total_count = total_count + int(val)
        # 返回应答
        return JsonResponse({'res': 5, 'total_count': total_count, 'errmsg': '更新成功'})

# 在购物车页面 删除购物车商品
class CartDeleteView(View):
    def post(self, request):
        """购物车记录删除"""
        # 判断用户是否登录
        if not request.user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})
            # 接收数据
        sku_id = request.POST.get('sku_id')
        # 数据校验
        if not sku_id:
            return JsonResponse({'res': 1, 'errmsg': '数据不完整'})
        # 检验商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except Exception as e:
            return JsonResponse({'res': 2, 'errmsg': '商品不存在'})
        user = request.user
        # 业务处理:删除购物车记录
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        # 业务处理： 增加或减少购物车数量
        conn.hdel(cart_key, sku_id)
        # 统计购物车中商品的总件数
        total_count = 0
        vals = conn.hvals(cart_key)
        for val in vals:
            total_count = total_count + int(val)
        # 返回应答
        return JsonResponse({'res': 3, 'total_count': total_count, 'message': '删除成功'})

""" 详情页面
添加商品到购物车
1. 请求方式 采用ajax post
如果涉及到数据的修改 采用post 
如果只涉及数据获取 采用get
2. 传递参数:商品id(sku_id) 商品数量(count)
注意！！！ ajax发起的请求都在后台  在浏览器是看不到的
所以即使我们使用了之前写的  登录检测LoginRequireMaxin    我们也看不到那个页面！！！！！
"""
class CartAdd(View):
    """购物车记录添加"""
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})
        # 接收数据
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')
        # 数据校验
        if not all([sku_id, count]):
            return JsonResponse({'res': 1, 'errmsg': '数据不完整'})
        # 校验添加商品数量
        try:
            count = int(count)
        except Exception as e:
            return JsonResponse({'res': 2, 'errmsg': '商品数目出错'})
        # 检验商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except Exception as e:
            return JsonResponse({'res': 3, 'errmsg': '商品不存在'})
        user = request.user
        #业务处理:添加购物车记录
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        # 如果用户购物车本就有该商品 则要先查出来再相加
        # 尝试获取sku_id的值 hget cart_key 属性
        # 如果在hash中不存在该key 函数返回None
        cart_count = conn.hget(cart_key, sku_id)
        if cart_count:
            # 累加购物车中商品数目
            count += int(cart_count)
        # 校验商品的库存
        if count > sku.stock:
            return JsonResponse({'res': 4, 'errmsg': '商品库存不足'})
        # 设置hash中sku_id对应的值
        conn.hset(cart_key, sku_id, count)
        # 计算购物车中商品的条目数
        total_count = conn.hlen(cart_key)
        # 返回应答
        return JsonResponse({'res': 5, "total_count": total_count, 'errmsg': '添加成功'})




