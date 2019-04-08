import os
from uuid import uuid4

from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


def generate_upload_filename(instance, filename):
    filename, ext = os.path.splitext(filename)
    filename = f"{uuid4()}{ext}"
    return "mugshots/%s/%s" % (instance.id, filename)


def check_image_extension(field):
    _allowed_ext = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
    _, ext = os.path.splitext(field.name)
    ext = ext.lower()
    if ext not in _allowed_ext:
        raise ValidationError(f"图片文件只允许以下后缀 {','.join(_allowed_ext)}")


class MyUserManager(BaseUserManager):
    def create_user(self, email, nickname, password=None, *args, **kwargs):
        """
        创建用户
        :param email:
        :param nickname:
        :param password:
        :param args:
        :param kwargs:
        :return:
        """
        if not email:
            raise ValueError('Email address is required when creating user')

        user = self.model(
            email=self.normalize_email(email),
            nickname=nickname,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nickname, password):
        """
        创建超级用户
        :param email:
        :param nickname:
        :param password:
        :return:
        """
        user = self.create_user(
            email=email,
            nickname=nickname,
            password=password
        )

        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


# Create your models here.
class User(AbstractUser):
    """
    用户
    """
    PRIVILEGE_LEVEL = (
        (0, '游客'),
        (5, '普通用户'),
        (10, '高级用户'),
        (100, '管理员'),
        (200, '超级管理员')
    )

    username = models.CharField(verbose_name='用户名', max_length=64, blank=True, null=True)
    email = models.EmailField(verbose_name='邮箱', max_length=255, unique=True)
    nickname = models.CharField(verbose_name='昵称', max_length=64, unique=True)
    mugshot = models.ImageField(verbose_name='头像', upload_to=generate_upload_filename, validators=[check_image_extension], blank=True, null=True)
    description = models.TextField(verbose_name='个人简介', max_length=512, blank=True, null=True)
    privilege_level = models.IntegerField(verbose_name='权限等级', choices=PRIVILEGE_LEVEL, default=0)

    objects = MyUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']

    class Meta(AbstractUser.Meta):
        ordering = ['-date_joined']
        verbose_name = '用户'
        verbose_name_plural = verbose_name
