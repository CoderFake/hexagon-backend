from django.db import models
from django.utils.translation import gettext_lazy as _
from course.models import CourseCategory
from course.utils import SlugMixin
from config.models import BaseModel

class NewsCategory(BaseModel):
    """Danh mục tin tức"""
    name = models.CharField(max_length=100, verbose_name=_("Tên danh mục"))
    slug = models.SlugField(unique=True, verbose_name=_("Slug"))
    description = models.TextField(blank=True, verbose_name=_("Mô tả"))
    color = models.CharField(max_length=7, default='#2952bf', verbose_name=_("Màu sắc"))

    class Meta:
        db_table = 'news_category'
        verbose_name = _("Danh mục tin tức")
        verbose_name_plural = _("Danh mục tin tức")

    def __str__(self):
        return self.name

class News(BaseModel, SlugMixin):
    """Tin tức và bài viết"""
    title = models.CharField(max_length=200, verbose_name=_("Tiêu đề"))
    slug = models.SlugField(unique=True, blank=True, verbose_name=_("Slug"))
    excerpt = models.TextField(verbose_name=_("Tóm tắt"))
    content = models.TextField(verbose_name=_("Nội dung"))
    image = models.CharField(max_length=255, blank=True, verbose_name=_("Ảnh đại diện"))
    author = models.ForeignKey('user.User', on_delete=models.CASCADE, verbose_name=_("Tác giả"))
    category = models.ForeignKey(NewsCategory, blank=True, null=True, on_delete=models.SET_NULL)
    course_category = models.ForeignKey(CourseCategory, blank=True, null=True, on_delete=models.SET_NULL)
    tags = models.JSONField(default=list, blank=True, verbose_name=_("Tags"))
    is_featured = models.BooleanField(default=False, verbose_name=_("Nổi bật"))
    is_published = models.BooleanField(default=False, verbose_name=_("Đã xuất bản"))
    published_at = models.DateTimeField(blank=True, null=True, verbose_name=_("Ngày xuất bản"))
    view_count = models.IntegerField(default=0, verbose_name=_("Lượt xem"))

    slug_source_field = 'title'

    class Meta:
        db_table = 'news'
        verbose_name = _("Tin tức")
        verbose_name_plural = _("Tin tức")
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

class Newsletter(BaseModel):
    """Đăng ký nhận tin"""
    email = models.EmailField(unique=True, verbose_name=_("Email"))
    name = models.CharField(max_length=200, blank=True, verbose_name=_("Họ tên"))
    is_subscribed = models.BooleanField(default=True, verbose_name=_("Đã đăng ký"))
    subscribed_categories = models.ManyToManyField(CourseCategory, blank=True, verbose_name=_("Quan tâm"))
    unsubscribed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'newsletter'
        verbose_name = _("Đăng ký nhận tin")
        verbose_name_plural = _("Đăng ký nhận tin")
        ordering = ['-created_at']

    def __str__(self):
        return self.email