import datetime
from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.db import models

from kern.utils.core import send_request


class RemoteModel(models.Model):
    id = models.UUIDField(primary_key=True)
    raw_data = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_expired (self):
        diff = datetime.datetime.now(datetime.timezone.utc) - self.updated_at
        return diff > datetime.timedelta(hours=1)

    def update (self, base_url=None):
        response = send_request(f"/{base_url}/?mode=retrieve&id={str(self.id)}", "GET")
        if response.status_code == 200:
            if response.json() != self.raw_data:
                self.raw_data = response.json()
            self.save()
            return self.raw_data
        else:
            return None

    def save (self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        super().save(*args, **kwargs)

    @property
    def data (self):
        if self.is_expired:
            self.update()
        return self.raw_data

    class Meta:
        abstract = True


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
    def full_name (self):
        return self.first_name + self.last_name

    @property
    def wishlist (self):
        return WishlistItem.objects.filter(user=self)

    class Meta:
        verbose_name = "客户"
        verbose_name_plural = "客户"


class UserVisitRecord(models.Model):
    user = models.ForeignKey(verbose_name="客户", on_delete=models.CASCADE, to="User", blank=True, null=True)
    user_agent = models.CharField(verbose_name="用户代理", max_length=255, blank=True, null=True)
    session_key = models.CharField(verbose_name="会话密钥", max_length=255, blank=True, null=True)
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


class Product(RemoteModel):
    @property
    def name (self):
        return self.data.get("name", "")

    @property
    def short_description (self):
        return self.data.get("short_description", "")

    @property
    def description (self):
        return self.data.get("description", "")

    @property
    def meta_keywords (self):
        return self.data.get("meta_keywords", "")

    @property
    def meta_description (self):
        return self.data.get("meta_description", "")

    @property
    def images (self):
        imgs = self.data.get("images", [])
        return [Image.objects.get(id=img) for img in imgs]

    @property
    def thumbnails (self):
        imgs = self.data.get("thumbnails", [])
        return [Image.objects.get(id=img) for img in imgs]

    @property
    def both_images (self):
        data = []
        for img, thumbnail in zip(self.images, self.thumbnails):
            data.append({"image": img, "thumbnail": thumbnail})
        return data

    @property
    def cover (self):
        return self.images[0]

    @property
    def cover_thumbnail (self):
        return self.thumbnails[0]

    @property
    def variants (self):
        return [ProductVariant.objects.get(id=variant) for variant in self.raw_data.get("variants", [])]

    @property
    def variant (self):
        return self.variants[0]

    def update (self, base_url="product"):
        return super().update(base_url=base_url)


class ProductVariant(RemoteModel):
    @property
    def price (self):
        # float to decimal, 2 decimal places
        return Decimal(self.data.get("price", 0)).quantize(Decimal("0.00"))

    @property
    def original_price (self):
        return Decimal(self.data.get("original_price", 0)).quantize(Decimal("0.00"))

    @property
    def product (self):
        return Product.objects.get(id=self.data.get("product"))

    def update (self, base_url="variant"):
        return super().update(base_url=base_url)


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
    variant = models.ForeignKey(verbose_name="产品", on_delete=models.CASCADE, to="ProductVariant")
    quantity = models.IntegerField(verbose_name="数量", default=1)
    created_at = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="更新时间", auto_now=True)

    class Meta:
        verbose_name = "购物车项"
        verbose_name_plural = "购物车项"

    def __str__ (self):
        return f"{self.cart.user.full_name}的购物车项"


class ImageManager(models.Manager):
    def __delete__ (self, instance):
        instance.img.delete()
        super().__delete__(instance)


class Image(models.Model):
    objects = ImageManager()
    id = models.UUIDField(primary_key=True, editable=False)
    img = models.ImageField(verbose_name="图片", upload_to="images/", blank=True, null=True)
    alt = models.CharField(verbose_name="图片描述", max_length=255, blank=True, null=True)
    updated_at = models.DateTimeField(verbose_name="最后更新时间", blank=True, null=True)

    def __str__ (self):
        return f"{self.id}"

    @property
    def url (self):
        return self.img.url


class WishlistItem(models.Model):
    user = models.ForeignKey(verbose_name="客户", on_delete=models.CASCADE, to="User", blank=True, null=True)
    variant = models.ForeignKey(verbose_name="产品", on_delete=models.CASCADE, to="ProductVariant")
    created_at = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    @property
    def product (self):
        return self.variant.product

    class Meta:
        verbose_name = "心愿单项"
        verbose_name_plural = "心愿单项"
