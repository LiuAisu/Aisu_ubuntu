from django.shortcuts import render
from django.views.generic import View
from goods.models import GoodsType, IndexTypeGoodsBanner, IndexPromotionBanner, IndexGoodsBanner
from django_redis import get_redis_connection
from utils.maxin import LoginRequireMaxin
from django.core.cache import cache

# Create your views here.


def show_index(request):
    """首页"""
    temp_path = 'dailyfresh/goods/index.html'
    return render(request, temp_path)


# 使用缓存  django.core.cache   cache.set(key, value, timeout)   cache.get(key)
"""把页面使用到的数据存放在缓存中，
当再一次使用这些数据时 先从缓存中获取 
如果查询不到再去数据库查询 减少数据库的查询次数"""
class IndexView(LoginRequireMaxin, View):
    def get(self, request):
        """产生首页静态页面"""
        # 尝试从缓存中获取数据  如果获取不到 返回none
        context = cache.get('index_page_data')
        # 缓存中没有就正常从数据库查  在数据库的数据更改时要更新缓存  我们在admin里改
        if context is None:
            print('设置缓存')
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
        user = request.user
        cart_count = 0
        if user.is_authenticated:
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)
        # 组织模板上下文
        context.update(cart_count=cart_count)
        """context = {
            'types': types,
            'goods_banners': goods_banners,
            'promotion_banners': promotion_banners,
            'cart_count': cart_count}"""
        return render(request, 'dailyfresh/goods/index.html', context)





