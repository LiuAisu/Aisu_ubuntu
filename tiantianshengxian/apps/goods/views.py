from django.shortcuts import render, redirect, reverse
from django.views.generic import View
from goods.models import GoodsType, IndexTypeGoodsBanner, IndexPromotionBanner, IndexGoodsBanner, GoodsSKU
from order.models import OrderGoods
from django_redis import get_redis_connection
from utils.maxin import LoginRequireMaxin
from django.core.cache import cache
from django.core.paginator import Paginator

# Create your views here.


def show_index(request):
    """首页"""
    temp_path = 'dailyfresh/goods/index.html'
    return render(request, temp_path)


# 使用缓存  django.core.cache   cache.set(key, value, timeout)   cache.get(key)
"""把页面使用到的数据存放在缓存中，
当再一次使用这些数据时 先从缓存中获取 
如果查询不到再去数据库查询 减少数据库的查询次数"""

class IndexView(View):
    def get(self, request):
        """产生首页静态页面"""
        # 尝试从缓存中获取数据  如果获取不到 返回none
        context = cache.get('index_page_data')
        # 缓存中没有就正常从数据库查  在数据库的数据更改时要更新缓存  我们在admin里改
        if context is None:
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
            # 设置缓存
            cache.set('index_page_data', context, 3600)
        # 获取用户购物车商品
        # 使用hash值作为购物车存储  hash是 key name value  在这里就可以用 key=cart_用户id, name=商品id, value=商品数量
        user = request.user
        if user.is_authenticated:
            conn = get_redis_connection('default')
            # 取出 key=cart_用户id
            cart_key = 'cart_%d' % user.id
            # 取这个对应key的元需数目
            cart_count = conn.hlen(cart_key)
        else:
            cart_count = 0
        # 组织模板上下文
        # 把这个cart_count加到字典
        context.update(cart_count=cart_count)
        """context = {
            'types': types,
            'goods_banners': goods_banners,
            'promotion_banners': promotion_banners,
            'cart_count': cart_count}"""
        return render(request, 'dailyfresh/goods/index.html', context)


class DetailView(View):
    def get(self, request, sku_id):
        # 获取商品
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            # 商品不存在
            return redirect(reverse('dailyfresh/goods/index.html'))
        # 获取商品的分类信息
        types = GoodsType.objects.all()
        # 获取商品的评论信息
        sku_orders = OrderGoods.objects.filter(sku=sku).exclude(comment='')
        # 获取新品信息
        new_skus = GoodsSKU.objects.filter(type=sku.type).order_by('create_time')[0:2]
        # 获取同一个spu的其他商品规格 排除自身
        same_spu_skus = GoodsSKU.objects.filter(goods=sku.goods).exclude(id=sku_id)
        # 获取购物车商品数量 并添加最近浏览
        user = request.user
        if user.is_authenticated:
            conn = get_redis_connection('default')
            # 取出 key=cart_用户id
            cart_key = 'cart_%d' % user.id
            # 取这个对应key的元需数目
            cart_count = conn.hlen(cart_key)
            # 添加用户历史浏览记录
            history_key = 'history_%d' % user.id
            # 移除列表中已经存在的对应的goods_id    如果没有这个元素将不会作任何事
            conn.lrem(history_key, 0, sku_id)
            # 把goods_id插入到列表的左侧
            conn.lpush(history_key, sku_id)
            # 只保存最新浏览的5个商品的id
            conn.ltrim(history_key, 0, 4)
        else:
            cart_count = 0
        # 组织模板上下文
        context = {'sku': sku, 'types': types,
                   'sku_orders': sku_orders,
                   'new_skus': new_skus,
                   'cart_count': cart_count,
                   'same_spu_skus': same_spu_skus}
        return render(request, 'dailyfresh/goods/detail.html', context)


# 设计请求地址
# 种类id/页码/排序方式
# /list/种类id/页码/排序方式
# /list/种类id/页码？sort=排序方式
# 在这里我们让每页最多显示5个页码   两种情况 总页数小于等于 5页
# 如果当前页是前三页 我们要显示 1，2，3，4，5页码
# 如果当前页是后3页 显示后5页
# 其他情况显示当前页前两页
class GoodsListView(View):
    """列表页"""
    def get(self, request, type_id, page_index):
        # 先获取请求的种类id的种类    并检测是否存在  不存在直接返回首页
        try:
            good_type = GoodsType.objects.get(id=type_id)
        except GoodsType.DoesNotExist:
            return redirect(reverse('dailyfresh/goods/index.html'))
        # 获取商品的分类信息
        types = GoodsType.objects.all()
        # 获取排序方式  sort=default按照默认id排序  sort=price按照价格排序 sort=hot 按照销量排序
        sort = request.GET.get('sort')
        # 获取 分类 商品的信息  即从Goods_SKU查商品数据  并降序排序
        if sort == 'price':
            skus = GoodsSKU.objects.filter(type=good_type).order_by('price')
        elif sort == 'hot':
            skus = GoodsSKU.objects.filter(type=good_type).order_by('-sales')
        else:
            # 其他任何情况都默认
            skus = GoodsSKU.objects.filter(type=good_type).order_by('-id')
        # 对数据进行分页  Paginator类  第一个参数是列表等克服可迭代元素  第二个参数是每页显示的数量
        paginator = Paginator(skus, 2)
        # 判断参数是否能够转换为数字
        try:
            page_index = int(page_index)
        except Exception as e:
            page_index = 1
        # 判断页数是否大于分页的总数
        if page_index > paginator.num_pages:
            page_index = 1
        # 获取第page_index页  的实例对象
        skus_page = paginator.page(page_index)
        # 在这里我们让每页最多显示5个页码
        # 总页数小于等于 5页
        # 如果当前页是前三页 我们要显示 1，2，3，4，5页码
        # 如果当前页是后3页 显示后5页
        # 其他情况显示当前页前两页
        num_pages = paginator.num_pages
        if num_pages < 5:
            # 显示全部页码
            pages = range(1, num_pages+1)
        elif page_index <= 3:
            pages = range(1, 6)
        elif num_pages - page_index <= 2:
            pages = range(num_pages-4, num_pages+1)
        else:
            pages = range(page_index-2, page_index + 3)
        # 获取新品信息
        new_skus = GoodsSKU.objects.filter(type=good_type).order_by('create_time')[0:2]
        # 获取用户购物车商品数目
        user = request.user
        cart_count = 0
        if user.is_authenticated:
            conn = get_redis_connection('default')
            # 取出 key=cart_用户id
            cart_key = 'cart_%d' % user.id
            # 取这个对应key的元需数目
            cart_count = conn.hlen(cart_key)
        else:
            cart_count = 0
        # 组织模板上下文
        context = {
            'type': good_type,
            'types': types,
            'skus_page': skus_page,
            'new_skus': new_skus,
            'cart_count': cart_count,
            'sort': sort,
            'pages': pages}
        return render(request, 'dailyfresh/goods/list.html', context)
















