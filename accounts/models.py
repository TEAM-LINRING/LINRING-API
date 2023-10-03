from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django_extensions.db.models import TimeStampedModel


# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, extra_fields):
        user = self.model(
            **extra_fields
        )
        user.is_active = False
        user.set_password(user.password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.model(
            email=email, password=password
        )
        user.is_active = True
        user.is_superuser = True
        user.is_staff = True
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    name = models.CharField(max_length=128, verbose_name="이름", null=True, blank=True)
    email = models.EmailField(unique=True, verbose_name="이메일")
    password = models.CharField(max_length=256, verbose_name="패스워드")
    birthday = models.DateField(verbose_name="생년월일", null=True, blank=True)
    number = models.CharField(max_length=28, verbose_name="전화번호", null=True, blank=True)
    profile = models.ImageField(verbose_name="프로필 이미지", null=True, blank=True)

    is_active = models.BooleanField(verbose_name="활성화 여부", default=True)
    is_staff = models.BooleanField(verbose_name="스태프 여부", default=False)
    is_superuser = models.BooleanField(verbose_name="최고 관리자 여부", default=False)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    PASSWORD_FIELD = 'password'

    def __str__(self):
        return self.email

    class Meta:
        verbose_name_plural = "유저 관리"
        verbose_name = "유저 관리"


PLACE_CHOICES = (
    ('북악관', '북악관'),
    ('북악관', '북악관'),
    ('북악관', '북악관'),
    ('북악관', '북악관'),
)


class TagSet(TimeStampedModel):
    place = models.CharField(max_length=12, verbose_name="장소", choices=PLACE_CHOICES)
    person = models.CharField(max_length=12, verbose_name="대상")
    method = models.CharField(max_length=12, verbose_name="행동")

    is_active = models.BooleanField(default=True, verbose_name="활성화 여부")
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="tagset_user", verbose_name="유저")

    class Meta:
        verbose_name_plural = "태그셋 관리"
        verbose_name = "태그셋 관리"
