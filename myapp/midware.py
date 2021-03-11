from datetime import datetime
from django.core.cache import cache
from django.shortcuts import render

from myapp.models import Black


class RecordMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 这里是统计在线人数的代码
        # 需要配置nginx的X-Real-IP才可以使用

        # realip = request.headers["X-Real-IP"]
        #
        # blacks = Black.objects.all()
        # user = request.session.get('user', None)
        # for black in blacks:
        #     if black.uaddress == realip \
        #             or (user and black.fuckuser and black.fuckuser.usermail == user):
        #         if datetime.now() < black.endptime:
        #             return render(request, "site/black.html", {"black": black})
        #
        # online_ips = cache.get("online_ips", [])
        # online_ips2 = []
        # if online_ips:
        #     online_ips2 = cache.get_many(online_ips).keys()
        #
        # cache.set(realip, 0, 15 * 60)
        # if realip not in online_ips2:
        #     online_ips.append(realip)
        #
        # cache.set("online_ips", online_ips)
        response = self.get_response(request)

        return response
