from django.contrib import admin
from .models import *


class StudentCourseEnrollmentInline(admin.TabularInline):
    model = StudentCourseEnrollment
    extra = 0
    fields = ['course', 'course_class', 'status', 'tuition_fee', 'paid_amount', 'payment_status']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'student_id', 'user', 'parent_name', 'parent_phone', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'student_id', 'parent_name', 'user__username']
    inlines = [StudentCourseEnrollmentInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:  # Tạo mới
            form.base_fields['user'].queryset = form.base_fields['user'].queryset.filter(student_profile__isnull=True)
        return form


@admin.register(StudentCourseEnrollment)
class StudentCourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course_class', 'status', 'payment_status', 'enrollment_date', 'enrollment_method']
    list_filter = ['status', 'payment_status', 'enrollment_method', 'course__category']
    search_fields = ['student__name', 'course__title', 'course_class__title']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form


@admin.register(StudentInquiry)
class StudentInquiryAdmin(admin.ModelAdmin):
    list_display = ['student_name', 'contact_name', 'phone', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    filter_horizontal = ['interested_courses']