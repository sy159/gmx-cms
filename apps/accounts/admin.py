from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from apps.accounts.models import *

if User in admin.site._registry:
    admin.site.unregister(User)

if Group in admin.site._registry:
    admin.site.unregister(Group)


class UserInfoInline(admin.StackedInline):
    model = UserInfo
    can_delete = False  # 嵌入不可删除
    readonly_fields = ["created", "tel"]  # 只读字段
    raw_id_fields = ["userid"]  # 单对多关系的选择

    # filter_horizontal = ("userid",)  # 多对多关系的选择

    # 设置只读函数
    def get_readonly_fields(self, request, obj=None):
        if request.user.username in ["root", ]:
            return ["created", ]
        return self.readonly_fields


@admin.register(User)
class UserInfoAdmin(UserAdmin):
    fieldsets = (("用户信息", {"fields": ["username", "password", "last_login", "date_joined"]}),
                 ("后台权限", {"fields": ["is_active", "is_staff", "is_superuser"]}),
                 )
    list_display = ["id", "username", "get_tel", "is_active"]
    list_display_links = ['username', ]
    list_filter = ['is_superuser', "user_info__created"]
    search_fields = ['username', "user_info__tel"]  # 筛选框
    readonly_fields = ['last_login', 'date_joined']
    inlines = [UserInfoInline, ]

    def get_tel(self, obj):
        return obj.user_info.tel

    get_tel.short_description = "电话"

    # 只允许查看属于当前域名下的用户
    def get_queryset(self, request):
        qs = super(UserInfoAdmin, self).get_queryset(request)
        if request.user.username in ["root", ]:
            return qs
        return qs.filter(user_info__host=request.get_host())
