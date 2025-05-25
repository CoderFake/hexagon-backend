from django.db import models
from django.utils.translation import gettext_lazy as _
from config.models import BaseModel


class GeneralRoadmap(BaseModel):
    """Lộ trình chung của Hexagon"""
    title = models.CharField(max_length=200, verbose_name=_("Tiêu đề"))
    short_description = models.TextField(verbose_name=_("Mô tả ngắn"))
    image_key = models.CharField(max_length=255, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'general_roadmap'
        verbose_name = _("Lộ trình chung")
        verbose_name_plural = _("Lộ trình chung")
        ordering = ['order']

    def __str__(self):
        return self.title


class GeneralRoadmapContentBlock(BaseModel):
    """Nội dung lộ trình chung"""
    roadmap = models.ForeignKey(GeneralRoadmap, on_delete=models.CASCADE, related_name='content_blocks')
    title = models.CharField(max_length=200, blank=True)
    image_key = models.CharField(max_length=255, blank=True)
    descriptions = models.JSONField(default=list)
    general_description = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'general_roadmap_content_block'
        ordering = ['order']