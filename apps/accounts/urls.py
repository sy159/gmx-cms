from __future__ import unicode_literals

from django.urls import path
from apps.accounts.views import *

urlpatterns = [
    path('test/', test),
]
