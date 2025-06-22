import uuid
from django.db import models
from django.contrib.sites.models import Site as DjangoSite
from django.utils.translation import gettext_lazy as _

class Site(DjangoSite):
    """Proxy model cho Site để hiển thị trong config app"""
    class Meta:
        proxy = True
        verbose_name = _("Site")
        verbose_name_plural = _("Sites")
        app_label = 'config'

class BaseModel(models.Model):
    """Base model với các trường chung"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Ngày tạo"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Ngày cập nhật"))
    is_active = models.BooleanField(default=True, verbose_name=_("Trạng thái"))

    class Meta:
        abstract = True

class SiteSettings(BaseModel):
    """Cấu hình website"""
    key = models.CharField(max_length=100, unique=True, verbose_name=_("Khóa"))
    value = models.TextField(verbose_name=_("Giá trị"))
    description = models.TextField(blank=True, verbose_name=_("Mô tả"))
    data_type = models.CharField(max_length=20, default='text', choices=[
        ('text', 'Text'),
        ('number', 'Number'),
        ('boolean', 'Boolean'),
        ('json', 'JSON'),
        ('url', 'URL'),
        ('email', 'Email'),
    ])

    class Meta:
        db_table = 'site_settings'
        verbose_name = _("Cấu hình")
        verbose_name_plural = _("Cấu hình")

    def __str__(self):
        return f"{self.key}: {self.value[:50]}"

class ContactInfo(BaseModel):
    """Thông tin liên hệ"""
    address = models.TextField(verbose_name=_("Địa chỉ"))
    phone = models.CharField(max_length=20, verbose_name=_("Số điện thoại"))
    email = models.EmailField(verbose_name=_("Email"))
    maps_url = models.URLField(blank=True, verbose_name=_("Google Maps"))
    facebook_url = models.URLField(blank=True, verbose_name=_("Facebook"))
    working_hours = models.TextField(blank=True, verbose_name=_("Giờ làm việc"))

    class Meta:
        db_table = 'contact_info'
        verbose_name = _("Thông tin liên hệ")
        verbose_name_plural = _("Thông tin liên hệ")

    def __str__(self):
        return f"Liên hệ - {self.email}"

class FAQ(BaseModel):
    """Câu hỏi thường gặp"""
    question = models.TextField(verbose_name=_("Câu hỏi"))
    answer = models.TextField(verbose_name=_("Câu trả lời"))
    category = models.ForeignKey('course.CourseCategory', blank=True, null=True, on_delete=models.CASCADE)
    order = models.IntegerField(default=0, verbose_name=_("Thứ tự"))

    class Meta:
        db_table = 'faq'
        verbose_name = _("FAQ")
        verbose_name_plural = _("FAQ")
        ordering = ['category', 'order']

    def __str__(self):
        return self.question[:100]

class Banner(BaseModel):
    """Banner quảng cáo"""
    title = models.CharField(max_length=200, verbose_name=_("Tiêu đề"))
    description = models.TextField(blank=True, verbose_name=_("Mô tả"))
    image = models.CharField(max_length=255, verbose_name=_("Ảnh banner"))
    link = models.URLField(blank=True, verbose_name=_("Liên kết"))
    position = models.CharField(max_length=50, choices=[
        ('hero', 'Hero Section'),
        ('sidebar', 'Sidebar'),
        ('footer', 'Footer'),
        ('popup', 'Popup'),
    ], default='hero')
    order = models.IntegerField(default=0, verbose_name=_("Thứ tự"))
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'banner'
        verbose_name = _("Banner")
        verbose_name_plural = _("Banner")
        ordering = ['position', 'order']

    def __str__(self):
        return self.title

class ContactInquiry(BaseModel):
    """Liên hệ tư vấn"""
    full_name = models.CharField(max_length=255, verbose_name=_("Họ tên"))
    phone = models.CharField(max_length=20, verbose_name=_("Số điện thoại"))
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    course = models.ForeignKey('course.Course', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("Khóa học quan tâm"))
    course_class = models.ForeignKey('course.CourseClass', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("Lớp học quan tâm"))
    message = models.TextField(blank=True, verbose_name=_("Tin nhắn"))
    inquiry_type = models.CharField(max_length=50, default='course_inquiry', choices=[
        ('course_inquiry', 'Tư vấn khóa học'),
        ('general_contact', 'Liên hệ chung'),
    ], verbose_name=_("Loại liên hệ"))
    status = models.CharField(max_length=20, default='new', choices=[
        ('new', 'Mới'),
        ('contacted', 'Đã liên hệ'),
        ('converted', 'Đã chuyển đổi'),
        ('closed', 'Đã đóng'),
    ], verbose_name=_("Trạng thái"))
    notes = models.TextField(blank=True, verbose_name=_("Ghi chú admin"))

    class Meta:
        db_table = 'contact_inquiry'
        verbose_name = _("Liên hệ tư vấn")
        verbose_name_plural = _("Liên hệ tư vấn")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.phone}"