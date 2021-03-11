from django.conf.urls import static, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include

from ehaforum import settings

urlpatterns = [
    path('', include('myapp.urls')),
    path('admin/', admin.site.urls),
    url(r'^static/(?P<path>.*)$', static.serve, {'document_root': settings.STATIC_ROOT}, name='static'),
]

urlpatterns += staticfiles_urlpatterns()
