from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = _("Hồ sơ người dùng")
    fields = ['bio', 'address', 'profile_picture']


@admin.register(User)
class UserAdmin(BaseUserAdmin):

    inlines = [UserProfileInline]

    list_display = [
        'email', 'username', 'first_name', 'last_name',
        'is_active', 'is_staff', 'date_joined'
    ]
    list_filter = [
        'is_active', 'is_staff', 'is_superuser',
        'date_joined', 'login_method'
    ]
    search_fields = ['email', 'username', 'first_name', 'last_name', 'phone_number']
    ordering = ['-date_joined']

    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        (_('Thông tin cá nhân'), {
            'fields': ('username', 'first_name', 'last_name', 'phone_number')
        }),
        (_('Quyền hạn'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            ),
            'classes': ('collapse',)
        }),
        (_('Thông tin đăng nhập'), {
            'fields': ('last_login', 'date_joined', 'firebase_id', 'login_method'),
            'classes': ('collapse',)
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'first_name', 'last_name',
                'password1', 'password2', 'is_active', 'is_staff'
            ),
        }),
    )

    readonly_fields = ['date_joined', 'last_login']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    list_display = ['user', 'get_full_name', 'address']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    list_filter = ['user__date_joined']

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    get_full_name.short_description = _("Họ tên")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')