from django.db import models
from django.utils.translation import gettext_lazy as _
from config.models import BaseModel


class Student(BaseModel):
    """Học sinh"""
    user = models.OneToOneField(
        'user.User',
        on_delete=models.CASCADE,
        related_name='student_profile',
        verbose_name=_("Tài khoản đăng nhập")
    )

    name = models.CharField(max_length=200, verbose_name=_("Họ tên"))
    date_of_birth = models.DateField(verbose_name=_("Ngày sinh"))
    student_id = models.CharField(max_length=20, unique=True, verbose_name=_("Mã học viên"))
    phone = models.CharField(max_length=20, verbose_name=_("Số điện thoại"))
    address = models.TextField(verbose_name=_("Địa chỉ"))
    parent_name = models.CharField(max_length=200, verbose_name=_("Tên phụ huynh"))
    parent_phone = models.CharField(max_length=20, verbose_name=_("SĐT phụ huynh"))

    courses = models.ManyToManyField(
        'course.Course',
        through='StudentCourseEnrollment',
        verbose_name=_("Khóa học đã đăng ký")
    )

    class Meta:
        db_table = 'student'
        verbose_name = _("Học sinh")
        verbose_name_plural = _("Học sinh")

    def __str__(self):
        return f"{self.name} ({self.student_id})"


class StudentCourseEnrollment(BaseModel):
    """Đăng ký khóa học của học sinh"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name=_("Học sinh"))
    course = models.ForeignKey('course.Course', on_delete=models.CASCADE, verbose_name=_("Khóa học"))
    course_class = models.ForeignKey(
        'course.CourseClass',
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name=_("Lớp học cụ thể")
    )

    enrollment_date = models.DateField(auto_now_add=True, verbose_name=_("Ngày đăng ký"))
    enrollment_method = models.CharField(
        max_length=20,
        choices=[
            ('admin', 'Admin đăng ký'),
            ('class_code', 'Nhập mã lớp'),
            ('online_form', 'Form online'),
        ],
        default='admin',
        verbose_name=_("Phương thức đăng ký")
    )
    start_date = models.DateField(null=True, blank=True, verbose_name=_("Ngày bắt đầu học"))
    end_date = models.DateField(null=True, blank=True, verbose_name=_("Ngày kết thúc"))

    status = models.CharField(
        max_length=20,
        choices=[
            ('enrolled', 'Đã đăng ký'),
            ('studying', 'Đang học'),
            ('completed', 'Hoàn thành'),
            ('dropped', 'Bỏ học'),
            ('suspended', 'Tạm ngừng'),
        ],
        default='enrolled',
        verbose_name=_("Trạng thái")
    )

    tuition_fee = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        verbose_name=_("Học phí")
    )
    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        default=0,
        verbose_name=_("Đã thanh toán")
    )
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('unpaid', 'Chưa thanh toán'),
            ('partial', 'Thanh toán một phần'),
            ('paid', 'Đã thanh toán đủ'),
            ('refunded', 'Đã hoàn tiền'),
        ],
        default='unpaid',
        verbose_name=_("Trạng thái thanh toán")
    )

    # Kết quả học tập
    final_grade = models.CharField(max_length=5, blank=True, verbose_name=_("Điểm cuối khóa"))
    notes = models.TextField(blank=True, verbose_name=_("Ghi chú"))

    class Meta:
        db_table = 'student_course_enrollment'
        unique_together = ['student', 'course_class']
        verbose_name = _("Đăng ký khóa học")
        verbose_name_plural = _("Đăng ký khóa học")

    @property
    def remaining_fee(self):
        return self.tuition_fee - self.paid_amount

    def __str__(self):
        return f"{self.student.name} - {self.course_class.title}"


class StudentInquiry(BaseModel):
    """Đăng ký tư vấn - giữ nguyên như cũ"""
    student_name = models.CharField(max_length=200, verbose_name=_("Tên học sinh"))
    student_age = models.IntegerField(verbose_name=_("Tuổi"))
    contact_name = models.CharField(max_length=200, verbose_name=_("Người liên hệ"))
    email = models.EmailField(verbose_name=_("Email"))
    phone = models.CharField(max_length=20, verbose_name=_("Số điện thoại"))
    interested_courses = models.ManyToManyField(
        'course.Course',
        blank=True,
        verbose_name=_("Khóa học quan tâm")
    )
    message = models.TextField(blank=True, verbose_name=_("Tin nhắn"))
    status = models.CharField(
        max_length=20,
        choices=[
            ('new', 'Mới'),
            ('contacted', 'Đã liên hệ'),
            ('converted', 'Đã chuyển đổi thành học sinh'),
        ],
        default='new'
    )

    class Meta:
        db_table = 'student_inquiry'
        verbose_name = _("Đăng ký tư vấn")
        verbose_name_plural = _("Đăng ký tư vấn")

    def __str__(self):
        return f"{self.student_name} - {self.contact_name}"