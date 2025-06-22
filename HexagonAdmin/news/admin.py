from django.contrib import admin
from .models import *
from config.admin import BaseModelAdmin


class NewsContentBlockInline(admin.StackedInline):
    model = NewsContentBlock
    extra = 0


@admin.register(NewsCategory)
class NewsCategoryAdmin(BaseModelAdmin):
    list_display = ['name', 'category_type', 'course', 'is_active']
    list_filter = ['category_type', 'course']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(News)
class NewsAdmin(BaseModelAdmin):
    list_display = ['title', 'category', 'is_published', 'published_at']
    list_filter = ['category', 'is_published']
    inlines = [NewsContentBlockInline]
    prepopulated_fields = {'slug': ('title',)}