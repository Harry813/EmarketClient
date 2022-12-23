import time

from django.contrib.auth.models import AbstractUser
from django.db import models

from kern.utils.core import send_request


class User(AbstractUser):
    uuid = models.UUIDField(blank=True, null=True)
    email = models.EmailField(verbose_name='邮箱', max_length=100, unique=True)
    username = models.CharField(verbose_name='用户名', max_length=30)
    first_name = models.CharField(verbose_name='名', max_length=30)
    last_name = models.CharField(verbose_name='姓', max_length=30)
    date_joined = models.DateTimeField(verbose_name='创建日期', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='上次登录', auto_now=True)

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
    user = models.ForeignKey(verbose_name="客户", on_delete=models.CASCADE, to="User", blank=True, null=True)
    user_agent = models.CharField(verbose_name="用户代理", max_length=255, blank=True, null=True)
    visited_at = models.DateTimeField(verbose_name="访问时间", auto_now_add=True)
    ip = models.GenericIPAddressField(verbose_name="IP地址", blank=True, null=True)
    referer = models.CharField(verbose_name="来源", max_length=255, blank=True, null=True)
    path = models.CharField(verbose_name="路径", max_length=255, blank=True, null=True)
    query_string = models.CharField(verbose_name="查询字符串", max_length=255, blank=True, null=True)
    method = models.CharField(verbose_name="方法", max_length=255, blank=True, null=True)
    is_synced = models.BooleanField(default=False)

    class Meta:
        verbose_name = "客户访问记录"
        verbose_name_plural = "客户访问记录"

    @property
    def cust (self):
        return self.user.full_name if self.user else "旅客"

    def __str__ (self):
        return f"{self.cust}[{self.ip}] @ {self.visited_at}"


class Address(models.Model):
    address_line1 = models.CharField(verbose_name="地址1", max_length=255)
    address_line2 = models.CharField(verbose_name="地址2", max_length=255, blank=True, null=True)
    city = models.CharField(verbose_name="城市", max_length=255)
    state = models.CharField(verbose_name="州", max_length=255)
    country = models.CharField(verbose_name="国家", max_length=255)
    zip_code = models.CharField(verbose_name="邮编", max_length=255)


class Product(models.Model):
    id = models.UUIDField(primary_key=True)
    raw_data = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)

    def update (self):
        response = send_request("/product/?mode=retrieve&id=" + str(self.id), "GET")
        if response.status_code == 200:
            if response.json() != self.raw_data:
                self.raw_data = response.json()
                self.save()
            return self.raw_data
        else:
            return None

    @property
    def data (self):
        if time.time() - self.updated_at.timestamp() > 3600:
            self.update()
        return self.raw_data

    @property
    def images (self):
        images = self.data.get("images", [])
        imgs = []
        thumbnails = []
        for a, b in images:
            if a is None:
                imgs.append(b)
            else:
                imgs.append(a)
            if b is None:
                thumbnails.append(a)
            else:
                thumbnails.append(b)
        imgs = Image.objects.filter(id__in=imgs)
        thumbnails = Image.objects.filter(id__in=thumbnails)
        return list(zip(imgs, thumbnails))


class ProductVariant(models.Model):
    id = models.UUIDField(primary_key=True)
    product = models.ForeignKey(verbose_name="产品", on_delete=models.CASCADE, to="Product")

    @property
    def data (self):
        data = send_request("/variant/?mode=retrieve&id=" + str(self.product.id), "GET")
        return data


class Cart(models.Model):
    user = models.ForeignKey(verbose_name="客户", on_delete=models.CASCADE, to="User", blank=True, null=True)
    created_at = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="更新时间", auto_now=True)

    class Meta:
        verbose_name = "购物车"
        verbose_name_plural = "购物车"

    def __str__ (self):
        return f"{self.user.full_name}的购物车"


class CartItem(models.Model):
    cart = models.ForeignKey(verbose_name="购物车", on_delete=models.CASCADE, to="Cart")
    product = models.ForeignKey(verbose_name="产品", on_delete=models.CASCADE, to="Product")
    quantity = models.IntegerField(verbose_name="数量", default=1)
    created_at = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="更新时间", auto_now=True)

    class Meta:
        verbose_name = "购物车项"
        verbose_name_plural = "购物车项"

    def __str__ (self):
        return f"{self.cart.user.full_name}的购物车项"


class Image(models.Model):
    id = models.UUIDField(primary_key=True)
    image = models.ImageField(verbose_name="图片", upload_to="images/")
    alt = models.CharField(verbose_name="图片描述", max_length=255, blank=True, null=True)

    def __str__ (self):
        return f"{self.id}"

    @property
    def url (self):
        return self.image.url
