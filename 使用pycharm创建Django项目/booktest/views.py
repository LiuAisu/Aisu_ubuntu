from django.shortcuts import render
from django.template import loader, RequestContext
from django.http import HttpResponse
# Create your views here.

# render(request, tempetes_path, content_dict) 和我们自己定义的my_render效果相同
def my_render(request, tempetes_path, content_dict=None):
    temp = loader.get_template(tempetes_path)
    # context = RequestContext(request, content_dict)
    response = temp.render(content_dict)
    return HttpResponse(response)


def index(request):
    tempetes_path = 'booktest/index.html'
    content_dict = {'content': 'my_django'}
    response = my_render(request, tempetes_path, content_dict)
    return render(request, tempetes_path, content_dict)