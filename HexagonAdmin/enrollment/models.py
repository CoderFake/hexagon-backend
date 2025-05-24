from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from course.models import Course, CourseCategory
from config.models import BaseModel


class StudentInquiry(BaseModel):
    """Đăng ký tư vấn từ học sinh/phụ huynh"""
    # Thông tin học sinh
    student_name = models.CharField(max_length=200, verbose_name=_("Tên học sinh"))
    student_age = models.IntegerField(verbose_name=_("Tuổi"))
    current_grade = models.CharField(max_length=50, blank=True, verbose_name=_("Lớp hiện tại"))
    current_school = models.CharField(max_length=200, blank=True, verbose_name=_("Trường học"))

    # Thông tin liên hệ
    contact_name = models.CharField(max_length=200, verbose_name=_("Người liên hệ"))
    email = models.EmailField(verbose_name=_("Email"))
    phone = models.CharField(max_length=20, verbose_name=_("Số điện thoại"))

    # Khóa học quan tâm
    interested_courses = models.ManyToManyField(CourseCategory, blank=True, verbose_name=_("Khóa học quan tâm"))
    message = models.TextField(blank=True, verbose_name=_("Tin nhắn"))
    preferred_contact_time = models.CharField(max_length=100, blank=True, verbose_name=_("Thời gian liên hệ"))

    # Xử lý
    status = models.CharField(max_length=20, choices=[
        ('new', 'Mới'),
        ('contacted', 'Đã liên hệ'),
        ('scheduled', 'Đã hẹn'),
        ('enrolled', 'Đã ghi danh'),
        ('declined', 'Từ chối'),
    ], default='new')
    is_contacted = models.BooleanField(default=False, verbose_name=_("Đã liên hệ"))
    notes = models.TextField(blank=True, verbose_name=_("Ghi chú nội bộ"))
    assigned_to = models.ForeignKey('user.User', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'student_inquiry'
        verbose_name = _("Đăng ký tư vấn")
        verbose_name_plural = _("Đăng ký tư vấn")
        ordering = ['-created_at']

    def clean(self):
        """Validate student age"""
        if self.student_age < 3 or self.student_age > 25:
            raise ValidationError(_("Tuổi học sinh phải từ 3 đến 25."))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student_name} - {self.contact_name}"


class CourseEnrollment(BaseModel):
    """Ghi danh khóa học chính thức"""
    # Thông tin học sinh
    student_name = models.CharField(max_length=200, verbose_name=_("Họ tên học sinh"))
    date_of_birth = models.DateField(verbose_name=_("Ngày sinh"))
    student_id = models.CharField(max_length=20, unique=True, verbose_name=_("Mã học viên"))
    current_school = models.CharField(max_length=200, blank=True, verbose_name=_("Trường học"))
    address = models.TextField(verbose_name=_("Địa chỉ"))

    # Khóa học
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name=_("Khóa học"))
    enrollment_date = models.DateField(auto_now_add=True, verbose_name=_("Ngày ghi danh"))
    start_date = models.DateField(blank=True, null=True, verbose_name=_("Ngày bắt đầu học"))
    end_date = models.DateField(blank=True, null=True, verbose_name=_("Ngày kết thúc"))

    # Trạng thái
    status = models.CharField(max_length=20, choices=[
        ('enrolled', 'Đã ghi danh'),
        ('studying', 'Đang học'),
        ('completed', 'Hoàn thành'),
        ('dropped', 'Bỏ học'),
        ('suspended', 'Tạm ngừng'),
    ], default='enrolled')

    # Thanh toán
    tuition_fee = models.DecimalField(max_digits=10, decimal_places=0, verbose_name=_("Học phí"))
    paid_amount = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name=_("Đã thanh toán"))
    payment_status = models.CharField(max_length=20, choices=[
        ('unpaid', 'Chưa thanh toán'),
        ('partial', 'Thanh toán một phần'),
        ('paid', 'Đã thanh toán đủ'),
        ('refunded', 'Đã hoàn tiền'),
    ], default='unpaid')

    class Meta:
        db_table = 'course_enrollment'
        verbose_name = _("Ghi danh khóa học")
        verbose_name_plural = _("Ghi danh khóa học")
        ordering = ['-enrollment_date']

    def clean(self):
        """Validate enrollment data"""
        if self.tuition_fee < 0:
            raise ValidationError(_("Học phí không thể âm."))
        if self.paid_amount < 0:
            raise ValidationError(_("Số tiền đã thanh toán không thể âm."))
        if self.paid_amount > self.tuition_fee:
            raise ValidationError(_("Số tiền đã thanh toán không thể lớn hơn học phí."))
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError(_("Ngày bắt đầu phải trước ngày kết thúc."))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def remaining_fee(self):
        """Remaining tuition fee to be paid"""
        return self.tuition_fee - self.paid_amount

    def __str__(self):
        return f"{self.student_name} - {self.course.name}"
