from django.db import models
from django.utils.translation import gettext_lazy as _
from config.models import BaseModel
from course.utils import SlugMixin


class NewsCategory(BaseModel, SlugMixin):
    """Danh mục bản tin"""
    name = models.CharField(max_length=100, verbose_name=_("Tên danh mục"))
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)

    course = models.ForeignKey(
        'course.Course',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Khóa học")
    )

    category_type = models.CharField(
        max_length=20,
        choices=[
            ('exam_results', 'Kết quả thi'),
            ('upcoming_events', 'Sắp diễn ra'),
            ('general', 'Tổng hợp'),
        ],
        default='general'
    )

    class Meta:
        db_table = 'news_category'
        verbose_name = _("Danh mục bản tin")
        verbose_name_plural = _("Danh mục bản tin")

    def __str__(self):
        return self.name


class News(BaseModel, SlugMixin):
    """Bản tin"""
    category = models.ForeignKey(NewsCategory, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, verbose_name=_("Tiêu đề"))
    slug = models.SlugField(unique=True, blank=True)
    short_description = models.TextField(verbose_name=_("Mô tả ngắn"))
    image_key = models.CharField(max_length=255, blank=True)
    is_published = models.BooleanField(default=False, verbose_name=_("Đã xuất bản"))
    published_at = models.DateTimeField(null=True, blank=True)
    view_count = models.IntegerField(default=0)

    class Meta:
        db_table = 'news'
        verbose_name = _("Bản tin")
        verbose_name_plural = _("Bản tin")
        ordering = ['-published_at']

    def __str__(self):
        return self.title


class NewsContentBlock(BaseModel):
    """Nội dung bản tin"""
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='content_blocks')
    title = models.CharField(max_length=200, blank=True)
    image_key = models.CharField(max_length=255, blank=True)
    descriptions = models.JSONField(default=list)
    general_description = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'news_content_block'
        ordering = ['order']