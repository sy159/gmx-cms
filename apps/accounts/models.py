from django.db import models
from django.contrib.auth.models import User


# 自定义用户表
class UserInfo(models.Model):
    userid = models.OneToOneField(User, primary_key=True, related_name="user_info", verbose_name="用户id", on_delete=models.CASCADE)
    host = models.CharField("域名", max_length=20, help_text="可用于多域名配置")
    tel = models.CharField("电话", max_length=15, null=True, blank=True, help_text="注册手机号")
    faq = models.TextField("备注", null=True, blank=True)
    created = models.DateTimeField("新建时间", auto_now_add=True)

    class Meta:
        verbose_name = '用户详情'
        verbose_name_plural = verbose_name
        db_table = 'user_info'

    def __str__(self):
        return '%s-%s' % (self.userid, self.userid.username)

    def save(self, *args, **kwargs):
        pass
        super(UserInfo, self).save(*args, **kwargs)
