from django.db import models
from django.utils.translation import gettext_lazy as _
from config.models import BaseModel
from course.utils import SlugMixin


class CourseCategory(BaseModel, SlugMixin):
    """Danh mục khóa học"""
    name = models.CharField(max_length=100, verbose_name=_("Tên danh mục"))
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name=_("Mô tả"))
    order = models.IntegerField(default=0, verbose_name=_("Thứ tự"))

    class Meta:
        db_table = 'course_category'
        verbose_name = _("Danh mục khóa học")
        verbose_name_plural = _("Danh mục khóa học")
        ordering = ['order']

    def __str__(self):
        return self.name


class Course(BaseModel, SlugMixin):
    """Khóa học chính"""
    category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, verbose_name=_("Tiêu đề"))
    short_description = models.TextField(verbose_name=_("Mô tả ngắn"))
    image_key = models.CharField(max_length=255, blank=True, verbose_name=_("Key ảnh"))
    slug = models.SlugField(unique=True, blank=True)
    order = models.IntegerField(default=0, verbose_name=_("Thứ tự"))

    class Meta:
        db_table = 'course'
        verbose_name = _("Khóa học")
        verbose_name_plural = _("Khóa học")

    def __str__(self):
        return self.title


class CourseClass(BaseModel):
    """Lớp học trong khóa"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='classes')
    title = models.CharField(max_length=200, verbose_name=_("Tiêu đề lớp"))
    short_description = models.TextField(verbose_name=_("Mô tả ngắn"))
    image_key = models.CharField(max_length=255, blank=True)
    address = models.TextField(verbose_name=_("Địa chỉ học"))
    schedule_description = models.TextField(verbose_name=_("Thời gian học"))
    learning_method = models.CharField(
        max_length=10,
        choices=[('offline', 'Offline'), ('online', 'Online')],
        default='offline',
        verbose_name=_("Phương thức")
    )

    class_code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("Mã lớp"),
        help_text=_("Học sinh nhập mã này để tham gia lớp")
    )

    is_open_for_enrollment = models.BooleanField(
        default=True,
        verbose_name=_("Mở đăng ký")
    )
    max_students = models.IntegerField(
        default=30,
        verbose_name=_("Sĩ số tối đa")
    )

    class Meta:
        db_table = 'course_class'
        verbose_name = _("Lớp học")
        verbose_name_plural = _("Lớp học")

    def __str__(self):
        return f"{self.course.title} - {self.title} ({self.class_code})"

    @property
    def current_students_count(self):
        return self.enrollments.filter(status__in=['enrolled', 'studying']).count()

    @property
    def available_slots(self):
        return self.max_students - self.current_students_count


class CourseContentBlock(BaseModel):
    """Nội dung lớp học"""
    course_class = models.ForeignKey(CourseClass, on_delete=models.CASCADE, related_name='content_blocks')
    title = models.CharField(max_length=200, blank=True)
    image_key = models.CharField(max_length=255, blank=True)
    descriptions = models.JSONField(default=list, verbose_name=_("Mô tả chi tiết"))
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'course_content_block'
        ordering = ['order']


class CourseFile(BaseModel):
    """File khóa học"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='files')
    name = models.CharField(max_length=200, verbose_name=_("Tên file"))
    description = models.TextField(blank=True)
    file_key = models.CharField(max_length=255, verbose_name=_("Key file"))

    class Meta:
        db_table = 'course_file'

    def __str__(self):
        return self.name


class CourseRoadmap(BaseModel):
    """Lộ trình khóa học"""
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='roadmap')
    short_description = models.TextField(verbose_name=_("Mô tả ngắn"))
    image_key = models.CharField(max_length=255, blank=True)
    slogan = models.CharField(max_length=200, verbose_name=_("Slogan"))

    class Meta:
        db_table = 'course_roadmap'

    def __str__(self):
        return f"Lộ trình {self.course.title}"


class RoadmapContentBlock(BaseModel):
    """Nội dung lộ trình"""
    roadmap = models.ForeignKey(CourseRoadmap, on_delete=models.CASCADE, related_name='content_blocks')
    title = models.CharField(max_length=200, blank=True)
    image_key = models.CharField(max_length=255, blank=True)
    descriptions = models.JSONField(default=list)
    general_description = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'roadmap_content_block'
        ordering = ['order']


class OutstandingStudent(BaseModel):
    """Học sinh tiêu biểu"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='outstanding_students')
    name = models.CharField(max_length=200, verbose_name=_("Tên"))
    awards = models.JSONField(default=list, verbose_name=_("Giải thưởng"))
    current_education = models.TextField(verbose_name=_("Học tập hiện tại"))

    class Meta:
        db_table = 'outstanding_student'

    def __str__(self):
        return self.name


class CourseAdditionalInfo(BaseModel):
    """Thông tin bổ sung khóa học"""
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='additional_info')

    class Meta:
        db_table = 'course_additional_info'


class CourseAdditionalContentBlock(BaseModel):
    """Nội dung thông tin bổ sung"""
    additional_info = models.ForeignKey(CourseAdditionalInfo, on_delete=models.CASCADE, related_name='content_blocks')
    title = models.CharField(max_length=200, blank=True)
    image_key = models.CharField(max_length=255, blank=True)
    descriptions = models.JSONField(default=list)
    general_description = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'course_additional_content_block'
        ordering = ['order']