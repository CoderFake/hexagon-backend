from django.contrib import admin
from .models import *


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'student_id', 'user', 'parent_name', 'parent_phone', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'student_id', 'parent_name', 'user__username']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:
            form.base_fields['user'].queryset = form.base_fields['user'].queryset.filter(student_profile__isnull=True)
        return form


@admin.register(StudentCourseEnrollment)
class StudentCourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['get_student_name', 'user', 'course_class', 'status', 'payment_status', 'enrollment_date', 'enrollment_method']
    list_filter = ['status', 'payment_status', 'enrollment_method', 'course__category']
    search_fields = ['user__username', 'user__full_name', 'user__student_profile__name', 'course__title', 'course_class__title']

    def get_student_name(self, obj):
        return obj.student_name
    get_student_name.short_description = 'Tên học sinh'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form


@admin.register(StudentInquiry)
class StudentInquiryAdmin(admin.ModelAdmin):
    list_display = ['student_name', 'contact_name', 'phone', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    filter_horizontal = ['interested_courses']