from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from course.utils import SlugMixin
from config.models import BaseModel


class Subject(BaseModel, SlugMixin):
    """Môn học (Mathematics, Physics, Chemistry, etc.)"""
    name = models.CharField(max_length=200, verbose_name=_("Tên môn học"))
    slug = models.SlugField(unique=True, blank=True, verbose_name=_("Slug"))
    code = models.CharField(max_length=20, unique=True, verbose_name=_("Mã môn"))
    description = models.TextField(blank=True, verbose_name=_("Mô tả"))
    icon_class = models.CharField(max_length=50, blank=True, verbose_name=_("Icon class"))
    color = models.CharField(max_length=7, default='#2952bf', verbose_name=_("Màu sắc"))
    order = models.IntegerField(default=0, verbose_name=_("Thứ tự"))

    slug_source_field = 'name'

    class Meta:
        db_table = 'subject'
        verbose_name = _("Môn học")
        verbose_name_plural = _("Môn học")
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class CourseCategory(BaseModel, SlugMixin):
    """Danh mục khóa học (Mathley, IGCSE, A-level, ASPX)"""
    name = models.CharField(max_length=100, verbose_name=_("Tên danh mục"))
    slug = models.SlugField(unique=True, blank=True, verbose_name=_("Slug"))
    short_name = models.CharField(max_length=20, verbose_name=_("Tên viết tắt"))
    description = models.TextField(verbose_name=_("Mô tả"))
    subtitle = models.TextField(blank=True, verbose_name=_("Phụ đề"))
    age_range_min = models.IntegerField(verbose_name=_("Độ tuổi tối thiểu"))
    age_range_max = models.IntegerField(verbose_name=_("Độ tuổi tối đa"))
    hero_image = models.CharField(max_length=255, blank=True, verbose_name=_("Ảnh khoá học"))
    icon = models.CharField(max_length=255, blank=True, verbose_name=_("Icon"))
    color = models.CharField(max_length=7, default='#2952bf', verbose_name=_("Màu chủ đạo"))
    order = models.IntegerField(default=0, verbose_name=_("Thứ tự"))

    slug_source_field = 'name'

    class Meta:
        db_table = 'course_category'
        verbose_name = _("Danh mục khóa học")
        verbose_name_plural = _("Danh mục khóa học")
        ordering = ['order', 'name']

    def clean(self):
        """Validate age range"""
        if self.age_range_min >= self.age_range_max:
            raise ValidationError(_("Độ tuổi tối thiểu phải nhỏ hơn độ tuổi tối đa."))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Course(BaseModel, SlugMixin):
    """Khóa học cụ thể trong từng danh mục"""
    category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE, related_name='courses')
    name = models.CharField(max_length=200, verbose_name=_("Tên khóa học"))
    slug = models.SlugField(unique=True, blank=True, verbose_name=_("Slug"))
    description = models.TextField(verbose_name=_("Mô tả"))
    content = models.TextField(blank=True, verbose_name=_("Nội dung chi tiết"))
    subjects = models.ManyToManyField(Subject, through='CourseSubject', verbose_name=_("Môn học"))
    duration_months = models.IntegerField(verbose_name=_("Thời lượng (tháng)"))
    hours_per_week = models.CharField(max_length=50, verbose_name=_("Giờ/tuần"))
    class_schedule = models.JSONField(default=dict, blank=True, verbose_name=_("Lịch học"))
    image = models.CharField(max_length=255, blank=True, verbose_name=_("Ảnh khóa học"))
    price = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name=_("Học phí"))
    max_students = models.IntegerField(default=20, verbose_name=_("Sĩ số tối đa"))
    order = models.IntegerField(default=0, verbose_name=_("Thứ tự"))

    slug_source_field = 'name'

    class Meta:
        db_table = 'course'
        verbose_name = _("Khóa học")
        verbose_name_plural = _("Khóa học")
        ordering = ['category', 'order', 'name']

    def clean(self):
        """Validate course data"""
        if self.duration_months <= 0:
            raise ValidationError(_("Thời lượng khóa học phải lớn hơn 0."))
        if self.max_students <= 0:
            raise ValidationError(_("Sĩ số tối đa phải lớn hơn 0."))
        if self.price < 0:
            raise ValidationError(_("Học phí không thể âm."))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category.short_name} - {self.name}"


class CourseSubject(BaseModel):
    """Quan hệ giữa khóa học và môn học với phân bổ giờ học"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    lecture_hours = models.IntegerField(default=0, verbose_name=_("Giờ lý thuyết"))
    tutorial_hours = models.IntegerField(default=0, verbose_name=_("Giờ bài tập"))
    lab_hours = models.IntegerField(default=0, verbose_name=_("Giờ thí nghiệm"))
    is_required = models.BooleanField(default=True, verbose_name=_("Bắt buộc"))

    class Meta:
        db_table = 'course_subject'
        unique_together = ['course', 'subject']
        verbose_name = _("Môn học trong khóa")
        verbose_name_plural = _("Môn học trong khóa")

    def clean(self):
        """Validate that at least one hour type is specified and all hours are non-negative"""
        if self.lecture_hours < 0 or self.tutorial_hours < 0 or self.lab_hours < 0:
            raise ValidationError(_("Số giờ học không thể âm."))
        
        total_hours = self.lecture_hours + self.tutorial_hours + self.lab_hours
        if total_hours == 0:
            raise ValidationError(_("Phải có ít nhất một loại giờ học được chỉ định."))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.course.name} - {self.subject.name}"


class Alumni(BaseModel):
    """Cựu học viên tiêu biểu đã tốt nghiệp và đạt thành tích"""
    name = models.CharField(max_length=200, verbose_name=_("Họ tên"))
    photo = models.CharField(max_length=255, blank=True, verbose_name=_("Ảnh"))
    courses_attended = models.ManyToManyField(Course, blank=True, verbose_name=_("Khóa học đã tham gia"))

    # Thành tích học tập
    academic_achievements = models.JSONField(default=list, verbose_name=_("Thành tích học thuật"))
    exam_results = models.JSONField(default=dict, verbose_name=_("Kết quả thi"))

    # Trường hiện tại hoặc đã tốt nghiệp
    current_school = models.CharField(max_length=200, blank=True, verbose_name=_("Trường hiện tại"))
    university_admitted = models.CharField(max_length=200, blank=True, verbose_name=_("Trường đại học trúng tuyển"))
    scholarship_received = models.TextField(blank=True, verbose_name=_("Học bổng nhận được"))

    # Thông tin bổ sung
    testimonial = models.TextField(blank=True, verbose_name=_("Lời cảm nhận"))
    linkedin_url = models.URLField(blank=True, verbose_name=_("LinkedIn"))
    graduation_year = models.IntegerField(blank=True, null=True, verbose_name=_("Năm tốt nghiệp khỏi Hexagon"))
    is_featured = models.BooleanField(default=False, verbose_name=_("Nổi bật trên trang chủ"))

    class Meta:
        db_table = 'alumni'
        verbose_name = _("Cựu học viên")
        verbose_name_plural = _("Cựu học viên")
        ordering = ['-graduation_year', 'name']

    def __str__(self):
        return self.name


class ExamInfo(BaseModel):
    """Thông tin về các kỳ thi (IGCSE, A-level, etc.)"""
    name = models.CharField(max_length=200, verbose_name=_("Tên kỳ thi"))
    short_name = models.CharField(max_length=50, verbose_name=_("Tên viết tắt"))
    course_category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE)
    description = models.TextField(blank=True, verbose_name=_("Mô tả"))
    subjects_available = models.ManyToManyField(Subject, blank=True, verbose_name=_("Môn thi"))
    exam_schedule = models.JSONField(default=list, verbose_name=_("Lịch thi trong năm"))
    registration_info = models.TextField(blank=True, verbose_name=_("Thông tin đăng ký"))
    syllabus_options = models.JSONField(default=dict, verbose_name=_("Tùy chọn syllabus"))

    class Meta:
        db_table = 'exam_info'
        verbose_name = _("Thông tin kỳ thi")
        verbose_name_plural = _("Thông tin kỳ thi")
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.course_category.name}"