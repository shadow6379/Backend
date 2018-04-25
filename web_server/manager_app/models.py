from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class ManagerInfo(models.Model):
    username = models.CharField(max_length=20, verbose_name=u'用户名', unique=True)
    password = models.CharField(max_length=32, verbose_name=u'密码')
    email = models.EmailField(verbose_name=u'邮箱')
    gender_choices = (
        (0, u'保密'),
        (1, u'男'),
        (2, u'女')
    )
    gender = models.IntegerField(choices=gender_choices, default=0, verbose_name=u'性别')
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name='电话号码')
    other = models.TextField(null=True, blank=True, verbose_name=u'其它')

    class Meta:
        verbose_name = u'管理员'
        verbose_name_plural = u'管理员信息'

