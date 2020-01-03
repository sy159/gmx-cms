from __future__ import unicode_literals

from django.urls import path
from apps.accounts.views import *

urlpatterns = [
    path('test/', test),
    path('login/', login, name="login"),
    path('logout/', logout, name="logout"),
    path('signup/', signup, name="signup"),
]
