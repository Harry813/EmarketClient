import datetime
import logging
import random
import string
from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext as _
from requests import HTTPError

from kern.utils.core import send_request


class RemoteModel(models.Model):
    URL = None

    id = models.UUIDField(primary_key=True)
    raw_data = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_expired(self):
        diff = datetime.datetime.now(datetime.timezone.utc) - self.updated_at
        return diff > datetime.timedelta(hours=1)

    def update(self):
        response = send_request(f"/{self.URL}/", "GET", {"mode": "retrieve", "id": str(self.pk)})
        try:
            response.raise_for_status()
        except HTTPError:
            # todo: 添加日志
            # todo: 添加开发人员警报
            logging.warning(f"Failed to update {self.__class__.__name__} {self.pk}")
            logging.warning(response.text)
            return None

        if response.status_code == 200:
            if response.json() != self.raw_data:
                self.raw_data = response.json()
            self.save()
            return self.raw_data
        else:
            return None

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        super().save(*args, **kwargs)

    @property
    def data(self):
        if self.is_expired or self.raw_data == {}:
            self.update()
        return self.raw_data

    class Meta:
        abstract = True


def generate_invitation_code():
    while True:
        code = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        # return code
        if not User.objects.filter(invitation_code=code).exists():
            return code


class RemoteManager(models.Manager):
    def __delete__(self, instance):
        instance.delete()
        super().__delete__(instance)


class User(AbstractUser):
    id = models.UUIDField(editable=False, primary_key=True)
    email = models.EmailField(verbose_name='邮箱', max_length=100, unique=True)
    username = models.CharField(verbose_name='用户名', max_length=30)
    first_name = models.CharField(verbose_name='名', max_length=30)
    last_name = models.CharField(verbose_name='姓', max_length=30)
    invitation_code = models.CharField(verbose_name='邀请码', max_length=8, unique=True,
                                       default=generate_invitation_code)
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

    @property
    def wishlist(self):
        return WishlistItem.objects.filter(user=self)

    @property
    def short_id(self):
        return str(self.id)[:6]

    def save(self, *args, **kwargs):
        if self.is_superuser:
            return
        super().save(*args, **kwargs)
        if hasattr(self, "wallet"):
            Wallet.objects.create(customer=self)

    class Meta:
        verbose_name = "客户"
        verbose_name_plural = "客户"


class Address(RemoteModel):
    URL = "address"

    @property
    def first_name(self):
        return self.data.get("first_name", "")

    @property
    def last_name(self):
        return self.data.get("last_name", "")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def address_line1(self):
        return self.data.get("address_line1", "")

    @property
    def address_line2(self):
        return self.data.get("address_line2", "")

    @property
    def city(self):
        return self.data.get("city", "")

    @property
    def state(self):
        return self.data.get("state", "")

    @property
    def country(self):
        return self.data.get("country", "")

    @property
    def zip_code(self):
        return self.data.get("zip_code", "")

    @property
    def phone(self):
        return self.data.get("phone", "")


class Product(RemoteModel):
    URL = "product"

    @property
    def name(self):
        return self.data.get("name", "")

    @property
    def short_description(self):
        return self.data.get("short_description", "")

    @property
    def description(self):
        return self.data.get("description", "")

    @property
    def meta_keywords(self):
        return self.data.get("meta_keywords", "")

    @property
    def meta_description(self):
        return self.data.get("meta_description", "")

    @property
    def images(self):
        imgs = self.data.get("images", [])
        return [Image.objects.get(id=img) for img in imgs]

    @property
    def thumbnails(self):
        imgs = self.data.get("thumbnails", [])
        return [Image.objects.get(id=img) for img in imgs]

    @property
    def both_images(self):
        data = []
        for img, thumbnail in zip(self.images, self.thumbnails):
            data.append({"image": img, "thumbnail": thumbnail})
        return data

    @property
    def cover(self):
        return self.images[0]

    @property
    def cover_thumbnail(self):
        return self.thumbnails[0]

    @property
    def variants(self):
        return [ProductVariant.objects.get(id=variant) for variant in self.data.get("variants", [])]

    @property
    def variant(self):
        if self.variants:
            return self.variants[0]
        return None


class ProductVariant(RemoteModel):
    URL = 'variant'

    @property
    def price(self):
        # float to decimal, 2 decimal places
        return Decimal(self.data.get("price", 0)).quantize(Decimal("0.00"))

    @property
    def original_price(self):
        return Decimal(self.data.get("original_price", 0)).quantize(Decimal("0.00"))

    @property
    def point(self):
        return int(self.data.get("point", 0))

    @property
    def product(self):
        return Product.objects.get(id=self.data.get("product"))


class CartItem(models.Model):
    user = models.ForeignKey(verbose_name="客户", on_delete=models.CASCADE, to="User")
    variant = models.ForeignKey(verbose_name="产品", on_delete=models.CASCADE, to="ProductVariant")
    quantity = models.PositiveSmallIntegerField(verbose_name="数量", default=1)
    created_at = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="更新时间", auto_now=True)

    class Meta:
        verbose_name = "购物车商品"
        verbose_name_plural = "购物车商品"

    @property
    def name(self):
        return self.variant.product.name

    @property
    def price(self):
        # float to decimal, 2 decimal places
        return Decimal(self.variant.price.quantize(Decimal("0.00")))

    @property
    def total(self):
        return self.price * self.quantity

    @property
    def image(self):
        return self.variant.product.cover_thumbnail

    @property
    def product(self):
        return self.variant.product

    def save(self, *args, **kwargs):
        if self.quantity == 0:
            self.delete()
        else:
            super().save(*args, **kwargs)


class ImageManager(models.Manager):
    def __delete__(self, instance):
        instance.img.delete()
        super().__delete__(instance)


class Image(models.Model):
    objects = ImageManager()
    id = models.UUIDField(primary_key=True, editable=False)
    img = models.ImageField(verbose_name="图片", upload_to="images/", blank=True, null=True)
    alt = models.CharField(verbose_name="图片描述", max_length=255, blank=True, null=True)
    updated_at = models.DateTimeField(verbose_name="最后更新时间", blank=True, null=True)

    def __str__(self):
        return f"{self.id}"

    @property
    def url(self):
        return self.img.url


class WishlistItem(models.Model):
    user = models.ForeignKey(verbose_name="客户", on_delete=models.CASCADE, to="User", blank=True, null=True)
    variant = models.ForeignKey(verbose_name="产品", on_delete=models.CASCADE, to="ProductVariant")
    created_at = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    @property
    def product(self):
        return self.variant.product

    class Meta:
        verbose_name = "心愿单项"
        verbose_name_plural = "心愿单项"


class Order(RemoteModel):
    URL = "order"

    STATUS = {
        "CREATED": _("已创建"),
        "PAID": _("已付款"),
        "PROCESSING": _("处理中"),
        "UNPAID": _("逾期未付款"),
        "CONFIRMED": _("仓库确认"),
        "SHIPPED": _("已发货"),
        "COMPLETED": _("已完成"),
        "CANCELLED": _("已取消")
    }
    CARRIER = [
        ("ROYALMAIL", "Royal Mail"),
        ("PARCELFORCE", "Parcel Force"),
        ("YODEL", "Yodel"),
        ("DPD", "DPD"),
        ("TNT", "TNT"),
        ("DHL", "DHL"),
        ("UPS", "UPS"),
        ("FEDEX", "FedEx"),
        ("MYHERMES", "MyHermes"),
        ("COLLECTPLUS", "Collect+"),
    ]
    user = models.ForeignKey(verbose_name="客户", on_delete=models.CASCADE, to="User")
    is_active = models.BooleanField(verbose_name="是否激活", default=True)

    def __str__(self):
        return f"ORD #{str(self.id)[-6:]}"

    @property
    def items(self):
        return self.data.get("items", [])

    @property
    def quantity(self):
        return sum([item["quantity"] for item in self.items])

    @property
    def subtotal(self):
        return Decimal(self.data.get("subtotal", 0)).quantize(Decimal("0.00"))

    @property
    def shipping(self):
        return Decimal(self.data.get("shipping", 0)).quantize(Decimal("0.00"))

    @property
    def shipment(self):
        return self.data.get("shipment", {})

    @property
    def carrier(self):
        if self.shipment:
            return self.shipment.get("carrier")
        return

    @property
    def payment(self):
        if self.status in ["PAID", "PROCESSING", "CONFIRMED", "SHIPPED", "COMPLETED"]:
            return self.data.get("payment", {})
        return None

    @property
    def discount(self):
        return Decimal(self.data.get("discount", 0)).quantize(Decimal("0.00"))

    @property
    def total(self):
        return Decimal(self.data.get("total", 0)).quantize(Decimal("0.00"))

    @property
    def date(self):
        created_at = self.data.get("created_at")
        return created_at.split("T")[0]

    @property
    def status(self):
        return self.data.get("status")

    def get_status_display(self):
        return self.STATUS.get(self.status, self.status)

    @property
    def short_id(self):
        return str(self.id)[-6:]

    @property
    def billing_address(self):
        return Address.objects.filter(id=self.data.get("billing_address")).first()

    @property
    def shipping_address(self):
        return Address.objects.filter(id=self.data.get("shipping_address")).first()

    def save(self, *args, **kwargs):
        if self.is_active:
            Order.objects.filter(user=self.user, is_active=True).update(is_active=False)
        super().save(*args, **kwargs)


class ErrorLog(models.Model):
    """
    todo: 尚未完成
    """
    STATUS = [
        (0, "未发送"),
        (1, "已发送")
    ]

    id = models.UUIDField(primary_key=True, editable=False)
    detail = models.TextField()
    status = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def send(self):
        res = send_request("/error/", "POST", {"detail": self.detail})

        try:
            res.raise_for_status()
        except HTTPError:
            return False

        if res.status_code == 200:
            self.status = 1
            self.save()
            return True
        else:
            return False


class Wallet(RemoteModel):
    URL = "wallet"

    id = None
    customer = models.OneToOneField(verbose_name="客户", on_delete=models.CASCADE, to="User", primary_key=True,
                                    related_name="wallet")

    @property
    def available_balance(self):
        return Decimal(self.data.get("available_balance", 0)).quantize(Decimal("0.00"))

    @property
    def frozen_balance(self):
        return Decimal(self.data.get("frozen_balance", 0)).quantize(Decimal("0.00"))

    @property
    def bind_balance(self):
        return Decimal(self.data.get("bind_balance", 0)).quantize(Decimal("0.00"))

    @property
    def is_withdrawable(self):
        return self.available_balance >= 50


class Point(RemoteModel):
    URL = "point"

    id = None
    customer = models.ForeignKey(verbose_name="客户", on_delete=models.CASCADE, to="User", primary_key=True)

    @property
    def point(self):
        return int(self.data.get("point", 0))

    @property
    def frozen_point(self):
        return int(self.data.get("frozen_point", 0))

    @property
    def exchanged(self):
        return self.data.get("exchanged", False)

    @property
    def cashable_amount(self):
        return Decimal(self.data.get("cashable_amount", 0)).quantize(Decimal("0.00"))
