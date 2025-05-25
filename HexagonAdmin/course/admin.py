from django.contrib import admin
from .models import *


class CourseContentBlockInline(admin.TabularInline):
    model = CourseContentBlock
    extra = 0


class CourseClassInline(admin.StackedInline):
    model = CourseClass
    extra = 0
    inlines = [CourseContentBlockInline]


class CourseFileInline(admin.TabularInline):
    model = CourseFile
    extra = 0


class OutstandingStudentInline(admin.TabularInline):
    model = OutstandingStudent
    extra = 0


class RoadmapContentBlockInline(admin.StackedInline):
    model = RoadmapContentBlock
    extra = 0


class CourseRoadmapInline(admin.StackedInline):
    model = CourseRoadmap
    inlines = [RoadmapContentBlockInline]


class CourseAdditionalContentBlockInline(admin.StackedInline):
    model = CourseAdditionalContentBlock
    extra = 0


class CourseAdditionalInfoInline(admin.StackedInline):
    model = CourseAdditionalInfo
    inlines = [CourseAdditionalContentBlockInline]


@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'is_active']
    list_editable = ['order']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'order', 'is_active']
    list_filter = ['category', 'is_active']
    inlines = [
        CourseClassInline,
        CourseFileInline,
        CourseRoadmapInline,
        OutstandingStudentInline,
        CourseAdditionalInfoInline
    ]
    prepopulated_fields = {'slug': ('title',)}