from django.contrib import admin
from .models import *


class NewsContentBlockInline(admin.StackedInline):
    model = NewsContentBlock
    extra = 0


@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'course', 'is_active']
    list_filter = ['category_type', 'course']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_published', 'published_at']
    list_filter = ['category', 'is_published']
    inlines = [NewsContentBlockInline]
    prepopulated_fields = {'slug': ('title',)}