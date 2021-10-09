from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

"""这个函数 将在视图函数前调用 """
# 这个函数必须定义到一个类里面 并且这个函数必须是这个类的实例对象的函数


# 中间件类
"""中间件类有以下几个函数
1. process_request 浏览器访问django 产生一个request对象  调用这个函数 然后url配置 
2. precess_view 函数 在url配置后调用 precess_view函数  然后调用view视图函数
3. process_response 视图函数之后 调用process_response函数
"""
class BlockIPSMiddleware(MiddlewareMixin):
    EXCLUDE_IPS = ['192.168.233.1']
    def process_view(self, request, view_func, *view_args, **view_kwargs):
        browser_ip = request.META['REMOTE_ADDR']
        if str(browser_ip) in BlockIPSMiddleware.EXCLUDE_IPS:
            return HttpResponse('这个ip已被禁止%s' % browser_ip)


class TestMiddleware(MiddlewareMixin):
    """服务器重启的时候  接受第一个请求时调用"""
    def __init__(self, get_response):
        super(TestMiddleware, self).__init__()
        self.get_response = get_response
        print('----init----')

    def process_request(self, request):
        """产生request对象时调用"""
        print("----process_request----")

    def process_view(self, request, view_func, *view_args, **view_kwargs):
        """url匹配之后 视图函数调用之前"""
        print('----process_view----')

    def process_exception(self, request, exception):
        """视图函数发生异常时候调用"""
        if isinstance(exception, ValueError):
            return HttpResponse("404")

    def process_response(self, request, response):
        """视图函数调用之后 内容返回浏览器之前  需要返回一个值 这里的response参数就是视图函数的返回值"""
        print('----process_response----')
        return response
