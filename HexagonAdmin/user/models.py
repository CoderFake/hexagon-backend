from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import uuid

class User(AbstractUser):
    """
    Custom user model that extends AbstractUser.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_("ID"))
    username = models.CharField(max_length=150, unique=True, verbose_name=_("Tên đăng nhập"))
    email = models.EmailField(unique=True, verbose_name=_("Địa chỉ email"))
    first_name = models.CharField(max_length=150, verbose_name=_("Họ"))
    last_name = models.CharField(max_length=150, verbose_name=_("Tên"))
    full_name = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Họ và tên"))
    password = models.CharField(max_length=128, verbose_name=_("Mật khẩu"))
    phone_number = models.CharField(
        max_length=17, 
        null=True, 
        blank=True, 
        verbose_name=_("Số điện thoại")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Trạng thái hoạt động"))
    is_staff = models.BooleanField(default=False, verbose_name=_("Nhân viên"))
    is_superuser = models.BooleanField(default=False, verbose_name=_("Quản trị viên"))
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name=_("Ngày tham gia"))
    last_login = models.DateTimeField(null=True, blank=True, verbose_name=_("Lần đăng nhập cuối"))
    firebase_id = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("ID Firebase"))
    login_method = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("Phương thức đăng nhập"))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'user'
        verbose_name = _("Người dùng")
        verbose_name_plural = _("Người dùng")
        ordering = ['date_joined']

    def __str__(self):
        return self.email

class UserProfile(models.Model):
    """
    User profile model that extends the User model.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name=_("Người dùng"))
    bio = models.TextField(null=True, blank=True, verbose_name=_("Tiểu sử"))
    address = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Địa chỉ"))
    profile_picture = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Hình ảnh đại diện "))

    class Meta:
        db_table = 'user_profile'
        verbose_name = _("Hồ sơ người dùng")
        verbose_name_plural = _("Hồ sơ người dùng")
        ordering = ['user__date_joined']

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"