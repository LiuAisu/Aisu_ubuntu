from django.contrib.auth.decorators import login_required


class LoginRequireMaxin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        # 调用父类方法
        view = super(LoginRequireMaxin, cls).as_view(**initkwargs)
        return login_required(view)