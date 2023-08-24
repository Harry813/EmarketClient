import re

from django import forms
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.translation import gettext as _

from kern.models import User
from kern.utils.core import send_request


class LoginForm(forms.Form):
    username_validator = UnicodeUsernameValidator()
    username = forms.CharField(
        label=_("用户名/邮箱"),
        max_length=150,
        min_length=8,
        validators=[username_validator],
        help_text=_("8-150字符，仅可包含大小写字母、数字以及@/./+/-/_"),
        error_messages={
            "invalid": _("用户名无效"),
            "max_length": _("用户名长度不得超过150字符"),
            "min_length": _("用户名长度不得少于8字符"),
            "UserNotExist": _("用户不存在"),
            "empty": _("用户名不得为空")
        },
    )

    password = forms.CharField(
        label=_("密码"),
        max_length=128,
        min_length=8,
        widget=forms.PasswordInput,
        help_text=_('8-128个字符，至少包含1个数字、1个字母'),
        error_messages={
            "invalid": _("密码格式错误，请包含8-128个字符，至少包含1个数字、1个字母"),
            "max_length": _("密码长度不得超过128字符"),
            "min_length": _("密码长度不得少于8字符"),
            "empty": _("密码不得为空")
        }
    )

    remember_me = forms.BooleanField(label=_("记住我"), required=False)

    def clean_password (self):
        password = self.cleaned_data.get("password")
        try:
            validate_password(password)
        except ValidationError as e:
            raise ValidationError(e)
        return password

    def clean_username (self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(Q(username=username) | Q(email=username)):
            return username
        else:
            raise ValidationError("User Not Found", code="UserNotExist")


class RegisterForm(forms.Form):
    first_name = forms.CharField(
        label=_("名"),
        max_length=30,
        min_length=1,
        help_text="1-30个字符",
        error_messages={
            "max_length": _("名长度不得超过30字符"),
            "min_length": _("名长度不得少于1字符"),
        }
    )

    last_name = forms.CharField(
        label=_("姓"),
        max_length=30,
        min_length=1,
        help_text="1-30个字符",
        error_messages={
            "max_length": _("姓长度不得超过30字符"),
            "min_length": _("姓长度不得少于1字符"),
        }
    )

    username_validator = UnicodeUsernameValidator()
    username = forms.CharField(
        label=_("用户名"),
        max_length=150,
        min_length=8,
        validators=[username_validator],
        help_text=_("8-150字符，仅可包含大小写字母、数字以及@/./+/-/_"),
        error_messages={
            "invalid": _("用户名无效"),
            "max_length": _("用户名长度不得超过150字符"),
            "min_length": _("用户名长度不得少于8字符"),
            "UserExist": _("用户已存在"),
            "empty": _("用户名不得为空")
        },
    )

    email = forms.EmailField(
        label=_("邮箱"),
        max_length=254,
        help_text=_("您的邮箱地址，用于找回密码等"),
        error_messages={
            "invalid": _("请输入有效的邮箱地址"),
            "max_length": _("邮箱长度不得超过254字符"),
            "empty": _("邮箱不得为空")
        }
    )

    password = forms.CharField(
        label=_("密码"),
        max_length=128,
        min_length=8,
        widget=forms.PasswordInput,
        help_text=_('8-128个字符，至少包含1个数字、1个字母'),
        error_messages={
            "invalid": _("密码格式错误，请包含8-128个字符，至少包含1个数字、1个字母"),
            "max_length": _("密码长度不得超过128字符"),
            "min_length": _("密码长度不得少于8字符"),
            "empty": _("密码不得为空")
        }
    )

    password_confirm = forms.CharField(
        label=_("确认密码"),
        max_length=128,
        min_length=8,
        widget=forms.PasswordInput,
        help_text=_('请再次输入密码'),
    )

    invitor = forms.CharField(
        label=_("邀请码"),
        max_length=8,
        min_length=8,
        required=False,
        help_text=_("邀请码可选，若有邀请码请填写"),
        error_messages={
            "max_length": _("邀请码长度不得超过8字符"),
            "min_length": _("邀请码长度不得少于8字符"),
        }
    )

    def clean_password (self):
        password = self.cleaned_data.get("password")
        try:
            validate_password(password)
        except ValidationError as e:
            raise ValidationError(e)
        return password

    def clean_username (self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username):
            raise ValidationError(_("用户名已存在，请前往登录"), code="UserExist")
        else:
            return username

    def clean_email (self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email):
            raise ValidationError(_("邮箱已被注册，请更换邮箱或前往登录"), code="EmailExist")
        else:
            return email

    def clean_password_confirm (self):
        password = self.cleaned_data.get("password")
        password_confirm = self.cleaned_data.get("password_confirm")
        if password == password_confirm:
            return password_confirm
        else:
            raise ValidationError("两次输入的密码不一致", code="invalid")

    def clean_invitor(self):
        invitor = self.cleaned_data.get("invitor")
        if invitor:
            try:
                User.objects.get(invitor=invitor)
            except User.DoesNotExist:
                raise ValidationError("邀请码不存在", code="invalid")
        return invitor


class CheckoutForm(forms.Form):
    COUNTRY_CHOICES = (
        ('', _('请选择国家')),
        ('GB', _('英国')),
        # ('CN', _('中国')),
        # ('US', _('美国')),
        # ('CA', _('加拿大')),
        # ('JP', _('日本')),
        # ('KR', _('韩国')),
        # ('FR', _('法国')),
        # ('DE', _('德国')),
        # ('IT', _('意大利')),
    )

    billing_first_name = forms.CharField(
        label=_("名"),
        max_length=30,
        min_length=1,
        help_text="1-30个字符",
        error_messages={
            "max_length": _("名长度不得超过30字符"),
            "min_length": _("名长度不得少于1字符"),
        }
    )

    def clean_billing_first_name (self):
        billing_first_name = self.cleaned_data.get("billing_first_name")
        return billing_first_name.capitalize()

    billing_last_name = forms.CharField(
        label=_("姓"),
        max_length=30,
        min_length=1,
        help_text="1-30个字符",
        error_messages={
            "max_length": _("姓长度不得超过30字符"),
            "min_length": _("姓长度不得少于1字符"),
        }
    )

    def clean_billing_last_name (self):
        billing_last_name = self.cleaned_data.get("billing_last_name")
        return billing_last_name.capitalize()

    billing_address_line1 = forms.CharField(
        label=_("地址"),
        max_length=100,
        min_length=1,
        help_text="1-100个字符",
        error_messages={
            "max_length": _("地址1长度不得超过100字符"),
            "min_length": _("地址1长度不得少于1字符"),
        }
    )

    def clean_billing_address_line1 (self):
        billing_address_line1 = self.cleaned_data.get("billing_address_line1")
        return billing_address_line1.capitalize()

    billing_address_line2 = forms.CharField(
        label=_("地址2"),
        max_length=100,
        min_length=1,
        help_text="1-100个字符",
        required=False,
        error_messages={
            "max_length": _("地址2长度不得超过100字符"),
            "min_length": _("地址2长度不得少于1字符"),
        }
    )

    def clean_billing_address_line2 (self):
        billing_address_line2 = self.cleaned_data.get("billing_address_line2")
        return billing_address_line2.capitalize()

    billing_city = forms.CharField(
        label=_("城市"),  # translate: Town/city
        max_length=100,
        min_length=1,
        help_text="1-100个字符",
        error_messages={
            "max_length": _("城市长度不得超过100字符"),
            "min_length": _("城市长度不得少于1字符"),
        }
    )

    def clean_billing_city (self):
        billing_city = self.cleaned_data.get("billing_city")
        return billing_city.capitalize()

    billing_state = forms.CharField(
        label=_("州/县"),
        max_length=100,
        min_length=1,
        help_text="1-100个字符",
        error_messages={
            "max_length": _("州长度不得超过100字符"),
            "min_length": _("州长度不得少于1字符"),
        }
    )

    def clean_billing_state (self):
        billing_state = self.cleaned_data.get("billing_state")
        return billing_state.upper()

    billing_country = forms.ChoiceField(
        label=_("国家"),
        choices=COUNTRY_CHOICES,
        initial="GB",
        error_messages={
            "invalid_choice": _("请选择国家"),
        }
    )

    billing_zip_code = forms.CharField(
        label=_("邮编"),
        max_length=100,
        min_length=1,
        help_text="1-20个字符",
        error_messages={
            "max_length": _("邮编长度不得超过20字符"),
            "min_length": _("邮编长度不得少于1字符"),
        }
    )

    def clean_billing_zip_code (self):
        billing_zip_code = self.cleaned_data.get("billing_zip_code")
        return billing_zip_code.upper()

    billing_phone = forms.CharField(
        label=_("电话"),
        max_length=100,
        min_length=1,
        help_text="1-20个字符",
        error_messages={
            "max_length": _("电话长度不得超过20字符"),
            "min_length": _("电话长度不得少于1字符"),
        }
    )

    ship_to_different_address = forms.BooleanField(
        label=_("送货地址不同"),
        required=False,
    )

    shipping_first_name = forms.CharField(
        label=_("名"),
        max_length=30,
        min_length=1,
        help_text="1-30个字符",
        required=False,
        error_messages={
            "max_length": _("名长度不得超过30字符"),
            "min_length": _("名长度不得少于1字符"),
        }
    )

    def clean_shipping_first_name (self):
        shipping_first_name = self.cleaned_data.get("shipping_first_name")
        return shipping_first_name.capitalize()

    shipping_last_name = forms.CharField(
        label=_("姓"),
        max_length=30,
        min_length=1,
        help_text="1-30个字符",
        required=False,
        error_messages={
            "max_length": _("姓长度不得超过30字符"),
            "min_length": _("姓长度不得少于1字符"),
        }
    )

    def clean_shipping_last_name (self):
        shipping_last_name = self.cleaned_data.get("shipping_last_name")
        return shipping_last_name.capitalize()

    shipping_address_line1 = forms.CharField(
        label=_("地址"),
        max_length=100,
        min_length=1,
        help_text="1-100个字符",
        required=False,
        error_messages={
            "max_length": _("地址1长度不得超过100字符"),
            "min_length": _("地址1长度不得少于1字符"),
        }
    )

    def clean_shipping_address_line1 (self):
        shipping_address_line1 = self.cleaned_data.get("shipping_address_line1")
        return shipping_address_line1.capitalize()

    shipping_address_line2 = forms.CharField(
        label=_("地址2"),
        max_length=100,
        min_length=1,
        help_text="1-100个字符",
        required=False,
        error_messages={
            "max_length": _("地址2长度不得超过100字符"),
            "min_length": _("地址2长度不得少于1字符"),
        }
    )

    def clean_shipping_address_line2 (self):
        shipping_address_line2 = self.cleaned_data.get("shipping_address_line2")
        return shipping_address_line2.capitalize()

    shipping_city = forms.CharField(
        label=_("城市"),
        max_length=100,
        min_length=1,
        help_text="1-100个字符",
        required=False,
        error_messages={
            "max_length": _("城市长度不得超过100字符"),
            "min_length": _("城市长度不得少于1字符"),
        }
    )

    def clean_shipping_city (self):
        shipping_city = self.cleaned_data.get("shipping_city")
        return shipping_city.capitalize()

    shipping_state = forms.CharField(
        label=_("州/县"),
        max_length=100,
        min_length=1,
        help_text="1-100个字符",
        required=False,
        error_messages={
            "max_length": _("州长度不得超过100字符"),
            "min_length": _("州长度不得少于1字符"),
        }
    )

    def clean_shipping_state (self):
        shipping_state = self.cleaned_data.get("shipping_state")
        return shipping_state.upper()

    shipping_country = forms.ChoiceField(
        label=_("国家"),
        choices=COUNTRY_CHOICES,
        initial="GB",
        required=False,
        error_messages={
            "invalid_choice": _("请选择国家"),
        }
    )

    shipping_zip_code = forms.CharField(
        label=_("邮编"),
        max_length=100,
        min_length=1,
        help_text="1-20个字符",
        required=False,
        error_messages={
            "max_length": _("邮编长度不得超过20字符"),
            "min_length": _("邮编长度不得少于1字符"),
        }
    )

    def clean_shipping_zip_code (self):
        shipping_zip_code = self.cleaned_data.get("shipping_zip_code")
        return shipping_zip_code.upper()

    shipping_phone = forms.CharField(
        label=_("电话"),
        max_length=100,
        min_length=1,
        help_text="1-20个字符",
        required=False,
        error_messages={
            "max_length": _("电话长度不得超过20字符"),
            "min_length": _("电话长度不得少于1字符"),
        }
    )

    note = forms.CharField(
        label=_("订单备注"),
        max_length=500,
        min_length=0,
        help_text="0-255个字符",
        required=False,
        error_messages={
            "max_length": _("备注长度不得超过255字符"),
            "min_length": _("备注长度不得少于0字符"),
        },
    )

    payment_method = forms.ChoiceField(
        label=_("支付方式"),
        help_text="部分支付方式可能需要支付额外的手续费",
        error_messages={
            "invalid_choice": _("请选择支付方式"),
        }
    )

    use_bind_balance = forms.BooleanField(
        label=_("使用绑定余额支付"),
        required=False,
        initial=True,
    )

    def clean (self):
        cleaned_data = super().clean()
        ship_to_different_address = cleaned_data.get("ship_to_different_address")
        if ship_to_different_address:
            if not cleaned_data.get("shipping_first_name"):
                self.add_error("shipping_first_name", _("必填项"))
            if not cleaned_data.get("shipping_last_name"):
                self.add_error("shipping_last_name", _("必填项"))
            if not cleaned_data.get("shipping_address_line1"):
                self.add_error("shipping_address_line1", _("必填项"))
            if not cleaned_data.get("shipping_address_line2"):
                self.add_error("shipping_address_line2", _("必填项"))
            if not cleaned_data.get("shipping_city"):
                self.add_error("shipping_city", _("必填项"))
            if not cleaned_data.get("shipping_state"):
                self.add_error("shipping_state", _("必填项"))
            if not cleaned_data.get("shipping_country"):
                self.add_error("shipping_country", _("必填项"))
            if not cleaned_data.get("shipping_zip_code"):
                self.add_error("shipping_zip_code", _("必填项"))
            if not cleaned_data.get("shipping_phone"):
                self.add_error("shipping_phone", _("必填项"))

        return cleaned_data

    def __init__ (self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        response = send_request("/payment/", "GET", {"mode": "choice"})
        if response.status_code == 200:
            self.fields["payment_method"].choices = [
                (payment_method["key"], payment_method["val"]) for payment_method in response.json()
            ]
        else:
            self.fields["payment_method"].choices = []
        self.fields["payment_method"].choices.insert(0, (None, "请选择支付方式"))
