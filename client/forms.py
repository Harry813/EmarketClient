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
        help_text="8-150字符，仅可包含大小写字母、数字以及@/./+/-/_",
        error_messages={
            "invalid": "用户名无效",
            "max_length": "用户名长度不得超过150字符",
            "min_length": "用户名长度不得少于8字符",
            "UserNotExist": "用户不存在",
            "empty": "用户名不得为空"
        },
    )

    password = forms.CharField(
        label=_("密码"),
        max_length=128,
        min_length=8,
        widget=forms.PasswordInput,
        help_text='8-128个字符，至少包含1个数字、1个字母',
        error_messages={
            "invalid": "密码格式错误，请包含8-128个字符，至少包含1个数字、1个字母",
            "max_length": "密码长度不得超过128字符",
            "min_length": "密码长度不得少于8字符",
            "empty": "密码不得为空"
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
