from __future__ import unicode_literals

from django.urls import path, re_path

from apps.core.views import *

urlpatterns = [
    re_path('log/(?P<log_name>.+)/(?P<row_num>\d+)/', log_view),
    path('delcache/', delcache),
]
