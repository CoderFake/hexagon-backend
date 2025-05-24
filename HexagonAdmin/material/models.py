from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from course.models import Course, Subject
from config.models import BaseModel


class MaterialCategory(BaseModel):
    name = models.CharField(max_length=100, verbose_name=_("Tên danh mục"))
    description = models.TextField(blank=True, verbose_name=_("Mô tả"))
    icon = models.CharField(max_length=50, blank=True, verbose_name=_("Icon"))
    is_public = models.BooleanField(default=True, verbose_name=_("Công khai"))
    order = models.IntegerField(default=0, verbose_name=_("Thứ tự"))

    class Meta:
        db_table = 'material_category'
        verbose_name = _("Danh mục tài liệu")
        verbose_name_plural = _("Danh mục tài liệu")
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Material(BaseModel):
    """Tài liệu học tập (PDF, video, audio, etc.)"""
    title = models.CharField(max_length=200, verbose_name=_("Tiêu đề"))
    description = models.TextField(blank=True, verbose_name=_("Mô tả"))
    category = models.ForeignKey(MaterialCategory, on_delete=models.CASCADE, related_name='materials')
    course = models.ForeignKey(Course, blank=True, null=True, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, blank=True, null=True, on_delete=models.CASCADE)

    # File information
    file_url = models.CharField(max_length=255, verbose_name=_("File key (MinIO)"))
    file_name = models.CharField(max_length=255, verbose_name=_("Tên file"))
    file_size = models.BigIntegerField(null=True, blank=True, verbose_name=_("Kích thước (bytes)"))
    file_type = models.CharField(max_length=10, choices=[
        ('PDF', 'PDF'),
        ('DOC', 'Word'),
        ('VIDEO', 'Video'),
        ('AUDIO', 'Audio'),
        ('IMAGE', 'Hình ảnh'),
        ('OTHER', 'Khác'),
    ], default='PDF')

    # Access control
    is_public = models.BooleanField(default=True, verbose_name=_("Công khai"))
    is_free = models.BooleanField(default=True, verbose_name=_("Miễn phí"))
    access_level = models.CharField(max_length=20, choices=[
        ('public', 'Công khai'),
        ('student', 'Chỉ học viên'),
        ('premium', 'Premium'),
        ('internal', 'Nội bộ'),
    ], default='public')

    # Statistics
    download_count = models.IntegerField(default=0, verbose_name=_("Lượt tải"))
    view_count = models.IntegerField(default=0, verbose_name=_("Lượt xem"))

    uploaded_by = models.ForeignKey('user.User', on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'material'
        verbose_name = _("Tài liệu")
        verbose_name_plural = _("Tài liệu")
        ordering = ['-created_at']

    def clean(self):
        if not self.course and not self.subject:
            raise ValidationError(_("Tài liệu phải thuộc về ít nhất một khóa học hoặc môn học."))
        
        if self.course and self.subject:
            if not self.course.subjects.filter(id=self.subject.id).exists():
                raise ValidationError(_("Môn học được chọn không thuộc khóa học này."))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
