from django.apps import AppConfig
from django.contrib.admin.widgets import AdminSplitDateTime


AdminSplitDateTime.template_name = 'admin/widgets/splitdatetime.html'

class ConfigConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'config'
    verbose_name = "Cấu hình chung"
    icon = "fa fa-cog"
