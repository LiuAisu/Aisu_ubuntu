from django.contrib import admin
from goods.models import GoodsType, Goods, GoodsSKU, \
    GoodsImages, IndexGoodsBanner, IndexTypeGoodsBanner, \
    IndexPromotionBanner
# from celery_tasks.tasks import generate_static_index_html
# 更新缓存 在数据修改时删除缓存
from django.core.cache import cache

# Register your models here.
# 在修改对应表的数据时  就会调用admin.ModelAdmin里的save方法   删除时调用delete方法
# 在这里我们需要在修改了表内容时就重新生成一下静态页面 则重写 save方法





admin.site.register(GoodsType)
admin.site.register(Goods)
admin.site.register(GoodsSKU)
admin.site.register(GoodsImages)
admin.site.register(IndexGoodsBanner)
admin.site.register(IndexTypeGoodsBanner)
admin.site.register(IndexPromotionBanner)
