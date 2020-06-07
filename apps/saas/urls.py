from __future__ import unicode_literals

from django.urls import path

from apps.saas.views import *

urlpatterns = [
    path('test/', test),
]