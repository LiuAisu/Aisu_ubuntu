# 定义索引类
from haystack import indexes
from goods.models import GoodsSKU

# 指定对于某个类的某些数据创建索引
# 索引类名格式： 模型类名+index
"""
全文检索表单  method="get"    action地址自己设置 单需要在主urls里配置
<form method="get" action="/search_goods">
搜索框输入的名字必须为q
<input type="text" class="input_text fl" name="q" placeholder="搜索商品">
<input type="submit" class="input_btn fr" name="" value="搜索">
</form>
url(r'^search_goods', include('haystack.urls')),
还需要一个 templates/search/search.html文件  这个文件也必须固定
框架会个给这个模板文件传递几个模板变量 
传递的模板变量
1. 搜索的关键字：{{ query }}
2. 搜索完数据后会进行分页  把当前页面的page对象传递来 名字就叫page: {{ page }}
page的每一个元素的object对象就是模型类的对象
3. 分页对应的paginator对象  paginator
whoosh默认的分词类对中文的支持不是很好  我们使用jieba分词模块
jieba可以对中文进行分词 cut_all=True代表是只要能分析出来的词语都分析出来
jieba.cut(中文字符串, cut_all=True) 返回值为生成器 生成器的每个值就是分词的结果
在python包里的haystack/whoosh_backend.py下
schema_fields[field_class.index_fieldname] = TEXT(
                    stored=True,
                    analyzer=field_class.analyzer or ChineseAnalyzer(),
                    field_boost=field_class.boost,
                    sortable=True,
}
更改为 analyzer=field_class.analyzer or ChineseAnalyzer(),
然后在setting里更改使用自己的配置文件
重新生成索引文件
"""


class GoodsSKUIndex(indexes.SearchIndex, indexes.Indexable):
    # 索引类里面的索引字段  document=True 说明是一个索引字段
    # use_template=True  把指定根据表中的那些字段来建立索引字段的说明放在一个文件中
    # 这个文件应该放在templates目录下search下indexes下的（模型类所在的应用名下的（模型类名小写_text.txt）中  目录是固定的
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        # 返回模型类
        return GoodsSKU
    # 建立索引的数据  方法返回那些内容 就会对那些内容建立索引  这里就是返回所有  即对所有数据进行索引创建
    def index_queryset(self, using=None):
        return self.get_model().objects.all()