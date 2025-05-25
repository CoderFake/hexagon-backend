from django.db import models
from django.utils.translation import gettext_lazy as _
from config.models import BaseModel


class AboutSection(BaseModel):
    """Phần giới thiệu Hexagon"""
    title = models.CharField(max_length=200, verbose_name=_("Tiêu đề"))
    short_description = models.TextField(verbose_name=_("Mô tả ngắn"))
    image_key = models.CharField(max_length=255, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'about_section'
        verbose_name = _("Phần giới thiệu")
        verbose_name_plural = _("Phần giới thiệu")
        ordering = ['order']

    def __str__(self):
        return self.title


class AboutContentBlock(BaseModel):
    """Nội dung giới thiệu"""
    about_section = models.ForeignKey(AboutSection, on_delete=models.CASCADE, related_name='content_blocks')
    title = models.CharField(max_length=200, blank=True)
    image_key = models.CharField(max_length=255, blank=True)
    descriptions = models.JSONField(default=list)
    general_description = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'about_content_block'
        ordering = ['order']
        verbose_name = _("Nội dung giới thiệu")
        verbose_name_plural = _("Nội dung giới thiệu")
