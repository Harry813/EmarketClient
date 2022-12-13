from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    global_id = models.UUIDField()
    email = models.EmailField(verbose_name='邮箱', max_length=60)
    username = models.CharField(verbose_name='用户名', max_length=30)
    first_name = models.CharField(verbose_name='名', max_length=30)
    last_name = models.CharField(verbose_name='姓', max_length=30)
    date_joined = models.DateTimeField(verbose_name='创建日期', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='上次登录', auto_now=True)

    is_active = None
    is_superuser = None
    groups = None
    user_permissions = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    @property
    def full_name(self):
        return self.first_name + self.last_name

    class Meta:
        verbose_name = "客户"
        verbose_name_plural = "客户"


class UserVisitRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户', blank=True, null=True)
    ip = models.GenericIPAddressField(verbose_name='IP地址')
    visit_time = models.DateTimeField(verbose_name='访问时间', auto_now_add=True)
    uri = models.URLField(verbose_name='访问地址', max_length=200)
    raw = models.JSONField(verbose_name='原始数据', blank=True, null=True)

    class Meta:
        verbose_name = '用户访问记录'
        verbose_name_plural = verbose_name
        ordering = ['-visit_time']

    def __str__(self):
        return f'{self.user.username if self.user else "Unknown"} - {self.ip}'


class Address(models.Model):
    address_line1 = models.CharField(verbose_name="地址1", max_length=255)
    address_line2 = models.CharField(verbose_name="地址2", max_length=255, blank=True, null=True)
    city = models.CharField(verbose_name="城市", max_length=255)
    state = models.CharField(verbose_name="州", max_length=255)
    country = models.CharField(verbose_name="国家", max_length=255)
    zip_code = models.CharField(verbose_name="邮编", max_length=255)
