from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User

USERNAME_RE = r'^[a-zA-Z0-9_.\u4e00-\u9fa5]+$'


class SignupForm(UserCreationForm):
    """
    用户注册表单
    """
    nickname = forms.CharField(
        regex=USERNAME_RE,
        widget=forms.TextInput,
        max_length=64,
        label='昵称',
        error_messages={'invalid': '昵称只能包含字母、数字、汉字、下划线和点'},
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = [
            ''
        ]
