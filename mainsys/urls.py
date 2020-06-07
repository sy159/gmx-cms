from __future__ import unicode_literals

import os

from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve

from apps.accounts.forms import AdminLoginForm
from mainsys.settings import APP_ROOT, APPS_CANNOT_INTSALL, MEDIA_ROOT
from mainsys.settings import SITE_HEADER
from apps.saas.views import home, index

admin.autodiscover()

admin.site.login_form = AdminLoginForm  # 源码提供login_form自定义登录表单验证

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'media/(?P<path>.*)', serve, {"document_root": MEDIA_ROOT}),  # 查看媒体文件
    path('oauth/', include('oauth2_provider.urls', namespace='oauth2_provider')),  # 用于oauth2授权
    path('', home, name='home'),  # home
    re_path('index/(?P<page>.+)/', index, name='index_page')  # /index/about/  or /index/.../
]

admin.site.site_header = SITE_HEADER or "后台管理系统"
admin.site.site_title = SITE_HEADER or "后台管理系统"

# 根据apps里的目录进行动态添加url
for ap in os.listdir(APP_ROOT):
    if ap not in APPS_CANNOT_INTSALL and os.path.isdir(os.path.join(APP_ROOT, ap)) and \
            os.path.exists(os.path.join(os.path.join(APP_ROOT, ap), "__init__.py")) and \
            os.path.exists(os.path.join(os.path.join(APP_ROOT, ap), "urls.py")):
        urlpatterns.append(path(ap + "/", include(ap + ".urls")))

# 自定义错误页面
handler403 = "apps.core.views.forbidden"
handler404 = "apps.core.views.page_not_found"
handler500 = "apps.core.views.server_error"
