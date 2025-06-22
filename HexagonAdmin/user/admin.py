from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile
from config.admin import BaseModelAdmin


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = _("Hồ sơ người dùng")
    fields = ['bio', 'address', 'profile_picture']
    extra = 0
    
    def has_add_permission(self, request, obj=None):
        return True
    
    def get_queryset(self, request):
        return super().get_queryset(request)


@admin.register(User)
class UserAdmin(BaseUserAdmin):

    inlines = [UserProfileInline]

    list_display = [
        'email', 'username', 'full_name', 'phone_number',
        'is_active', 'is_staff', 'date_joined'
    ]
    list_filter = [
        'is_active', 'is_staff', 'is_superuser',
        'date_joined', 'login_method'
    ]
    search_fields = ['email', 'username', 'full_name', 'phone_number', 'profile__address']
    ordering = ['-date_joined']

    fieldsets = (
        (_('Thông tin đăng nhập'), {
            'fields': ('email', 'password'),
            'description': 'Thông tin cơ bản để đăng nhập hệ thống'
        }),
        (_('Thông tin cá nhân'), {
            'fields': ('username', 'full_name', 'phone_number'),
            'description': 'Thông tin cá nhân của người dùng'
        }),
        (_('Quyền hạn'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            ),
            'classes': ('collapse',),
            'description': 'Phân quyền và trạng thái tài khoản'
        }),
        (_('Thông tin hệ thống'), {
            'fields': ('last_login', 'date_joined', 'firebase_id', 'login_method'),
            'classes': ('collapse',),
            'description': 'Thông tin được hệ thống tự động ghi nhận'
        }),
    )

    add_fieldsets = (
        (_('Tạo tài khoản mới'), {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'full_name', 'phone_number',
                'password1', 'password2', 'is_active', 'is_staff'
            ),
            'description': 'Điền thông tin để tạo tài khoản người dùng mới'
        }),
    )

    readonly_fields = ['date_joined', 'last_login']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile')
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not hasattr(obj, 'profile'):
            UserProfile.objects.create(user=obj)


class UserProfileAdmin(BaseModelAdmin):

    list_display = ['user', 'get_full_name', 'address']
    search_fields = ['user__email', 'user__full_name']
    list_filter = ['user__date_joined']

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    get_full_name.short_description = _("Họ tên")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')