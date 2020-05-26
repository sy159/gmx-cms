from __future__ import unicode_literals

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm


# 后台登录表单
class AdminLoginForm(AuthenticationForm):
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            elif not self.user_cache.is_active:
                raise forms.ValidationError(
                    self.error_messages['inactive'],
                    code='inactive',
                )
            # 用于域名判断（只能是当前域名下的超管登录）
            elif username not in ["root", ] and self.user_cache.user_info.host != self.request.get_host():
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
        return self.cleaned_data
