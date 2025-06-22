from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site as DjangoSite
from django.urls import path
from django.db import models
from django.contrib.admin.widgets import AdminSplitDateTime
from .models import Site, SiteSettings, ContactInfo, FAQ, Banner, ContactInquiry
from .views import site_config_view

class CustomDateTimeWidget(AdminSplitDateTime):
    template_name = 'admin/widgets/split_datetime.html'

class BaseModelAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.DateTimeField: {'widget': CustomDateTimeWidget},
    }

admin.site.unregister(Group)
try:
    admin.site.unregister(Permission)
    admin.site.unregister(ContentType)
except Exception as e:
    pass

if admin.site.is_registered(DjangoSite):
    admin.site.unregister(DjangoSite)

@admin.register(Site)
class SiteAdmin(BaseModelAdmin):
    list_display = ['domain', 'name', 'id']
    ordering = ()
    
    fieldsets = (
        ('Cấu hình Site', {
            'fields': ('domain', 'name'),
            'description': 'Cấu hình domain và tên hiển thị của site'
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request)
    
    class Meta:
        verbose_name = "Site"
        verbose_name_plural = "Sites"

@admin.register(SiteSettings)
class SiteSettingsAdmin(BaseModelAdmin):
    list_display = ['key', 'value_preview', 'data_type', 'description_preview', 'updated_at']
    list_filter = ['data_type', 'is_active']
    search_fields = ['key', 'value', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def value_preview(self, obj):
        return obj.value[:50] + '...' if len(obj.value) > 50 else obj.value
    value_preview.short_description = 'Giá trị'
    
    def description_preview(self, obj):
        return obj.description[:30] + '...' if len(obj.description) > 30 else obj.description
    description_preview.short_description = 'Mô tả'

@admin.register(ContactInfo)
class ContactInfoAdmin(BaseModelAdmin):
    list_display = ['email', 'phone', 'address_preview', 'is_active', 'updated_at']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def address_preview(self, obj):
        return obj.address[:50] + '...' if len(obj.address) > 50 else obj.address
    address_preview.short_description = 'Địa chỉ'

@admin.register(FAQ)
class FAQAdmin(BaseModelAdmin):
    list_display = ['question_preview', 'category', 'order', 'is_active', 'updated_at']
    list_filter = ['category', 'is_active']
    search_fields = ['question', 'answer']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['category', 'order']
    
    def question_preview(self, obj):
        return obj.question[:70] + '...' if len(obj.question) > 70 else obj.question
    question_preview.short_description = 'Câu hỏi'

@admin.register(Banner)
class BannerAdmin(BaseModelAdmin):
    list_display = ['title', 'position', 'order', 'is_active', 'start_date', 'end_date']
    list_filter = ['position', 'is_active']
    search_fields = ['title', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['position', 'order']

@admin.register(ContactInquiry)
class ContactInquiryAdmin(BaseModelAdmin):
    list_display = ['full_name', 'phone', 'email', 'inquiry_type', 'status', 'course', 'created_at']
    list_filter = ['inquiry_type', 'status', 'created_at', 'course']
    search_fields = ['full_name', 'phone', 'email', 'message']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        return False

class CustomAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('config/', self.admin_view(site_config_view), name='site_config'),
        ]
        return custom_urls + urls

admin.site.__class__ = CustomAdminSite
admin.site.site_header = 'Hexagon Education Admin'
admin.site.site_title = 'Hexagon Admin'
admin.site.index_title = 'Quản lý hệ thống Hexagon Education'