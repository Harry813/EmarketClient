from django import forms
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.translation import gettext as _

from kern.models import User


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
