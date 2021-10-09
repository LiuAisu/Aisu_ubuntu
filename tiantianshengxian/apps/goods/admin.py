from django.contrib import admin
from goods.models import GoodsType, Goods, GoodsSKU, \
    GoodsImages, IndexGoodsBanner, IndexTypeGoodsBanner, \
    IndexPromotionBanner
from celery_tasks.tasks import generate_static_index_html
# 更新缓存 在数据修改时删除缓存
from django.core.cache import cache

# Register your models here.
# 在修改对应表的数据时  就会调用admin.ModelAdmin里的save方法   删除时调用delete方法
# 在这里我们需要在修改了表内容时就重新生成一下静态页面 则重写 save方法

class GoodsTypeAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        """新增或更新表的数据时调用"""
        # 调用父类方法 使他完成原有相应功能
        super().save_model(request, obj, form, change)
        # 使用celery发出任务使worker重新生成静态页面
        generate_static_index_html.delay()
        # 清除缓存
        cache.delete('index_page_data')

    def delete_model(self, request, obj):
        """删除表的数据时调用"""
        # 调用父类方法 使他完成原有相应功能
        super().delete_model(request, obj)
        # 使用celery发出任务使worker重新生成静态页面
        generate_static_index_html.delay()
        cache.delete('index_page_data')


class GoodsAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        """新增或更新表的数据时调用"""
        # 调用父类方法 使他完成原有相应功能
        super().save_model(request, obj, form, change)
        # 使用celery发出任务使worker重新生成静态页面
        generate_static_index_html.delay()
        cache.delete('index_page_data')

    def delete_model(self, request, obj):
        """删除表的数据时调用"""
        # 调用父类方法 使他完成原有相应功能
        super().delete_model(request, obj)
        # 使用celery发出任务使worker重新生成静态页面
        generate_static_index_html.delay()
        cache.delete('index_page_data')


class IndexPromotionBannerAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        """新增或更新表的数据时调用"""
        # 调用父类方法 使他完成原有相应功能
        super().save_model(request, obj, form, change)
        # 使用celery发出任务使worker重新生成静态页面
        generate_static_index_html.delay()
        cache.delete('index_page_data')

    def delete_model(self, request, obj):
        """删除表的数据时调用"""
        # 调用父类方法 使他完成原有相应功能
        super().delete_model(request, obj)
        # 使用celery发出任务使worker重新生成静态页面
        generate_static_index_html.delay()
        cache.delete('index_page_data')


class GoodsSKUAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        """新增或更新表的数据时调用"""
        # 调用父类方法 使他完成原有相应功能
        super().save_model(request, obj, form, change)
        # 使用celery发出任务使worker重新生成静态页面
        generate_static_index_html.delay()
        cache.delete('index_page_data')

    def delete_model(self, request, obj):
        """删除表的数据时调用"""
        # 调用父类方法 使他完成原有相应功能
        super().delete_model(request, obj)
        # 使用celery发出任务使worker重新生成静态页面
        generate_static_index_html.delay()
        cache.delete('index_page_data')


class GoodsImagesAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        """新增或更新表的数据时调用"""
        # 调用父类方法 使他完成原有相应功能
        super().save_model(request, obj, form, change)
        # 使用celery发出任务使worker重新生成静态页面
        generate_static_index_html.delay()
        cache.delete('index_page_data')

    def delete_model(self, request, obj):
        """删除表的数据时调用"""
        # 调用父类方法 使他完成原有相应功能
        super().delete_model(request, obj)
        # 使用celery发出任务使worker重新生成静态页面
        generate_static_index_html.delay()
        cache.delete('index_page_data')


class IndexGoodsBannerAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        """新增或更新表的数据时调用"""
        # 调用父类方法 使他完成原有相应功能
        super().save_model(request, obj, form, change)
        # 使用celery发出任务使worker重新生成静态页面
        generate_static_index_html.delay()
        cache.delete('index_page_data')

    def delete_model(self, request, obj):
        """删除表的数据时调用"""
        # 调用父类方法 使他完成原有相应功能
        super().delete_model(request, obj)
        # 使用celery发出任务使worker重新生成静态页面
        generate_static_index_html.delay()
        cache.delete('index_page_data')


class IndexTypeGoodsBannerAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        """新增或更新表的数据时调用"""
        # 调用父类方法 使他完成原有相应功能
        super().save_model(request, obj, form, change)
        # 使用celery发出任务使worker重新生成静态页面
        generate_static_index_html.delay()
        cache.delete('index_page_data')

    def delete_model(self, request, obj):
        """删除表的数据时调用"""
        # 调用父类方法 使他完成原有相应功能
        super().delete_model(request, obj)
        # 使用celery发出任务使worker重新生成静态页面
        generate_static_index_html.delay()
        cache.delete('index_page_data')



admin.site.register(GoodsType, GoodsTypeAdmin)
admin.site.register(Goods, GoodsAdmin)
admin.site.register(GoodsSKU, GoodsSKUAdmin)
admin.site.register(GoodsImages, GoodsImagesAdmin)
admin.site.register(IndexGoodsBanner, IndexGoodsBannerAdmin)
admin.site.register(IndexTypeGoodsBanner, IndexTypeGoodsBannerAdmin)
admin.site.register(IndexPromotionBanner, IndexPromotionBannerAdmin)