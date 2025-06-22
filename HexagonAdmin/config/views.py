from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Site, SiteSettings, ContactInfo, FAQ, Banner
import json
from django.contrib.auth import logout
# Create your views here.

@staff_member_required
def site_config_view(request):
    if request.method == 'POST':
        try:
            if 'new_key' in request.POST:
                new_key = request.POST.get('new_key')
                new_value = request.POST.get('new_value')
                new_data_type = request.POST.get('new_data_type', 'text')
                
                if new_key and new_value:
                    setting, created = SiteSettings.objects.get_or_create(key=new_key)
                    setting.value = new_value
                    setting.data_type = new_data_type
                    setting.save()
                    
                    action = 'tạo mới' if created else 'cập nhật'
                    messages.success(request, f'Đã {action} cấu hình "{new_key}" thành công!')
                else:
                    messages.error(request, 'Key và Value không được để trống!')
            else:
                # Xử lý cập nhật site settings
                for key, value in request.POST.items():
                    if key.startswith('setting_'):
                        setting_key = key.replace('setting_', '')
                        setting, created = SiteSettings.objects.get_or_create(key=setting_key)
                        setting.value = value
                        setting.save()
                
                messages.success(request, 'Cấu hình đã được cập nhật thành công!')
            
            return redirect('admin:site_config')
        except Exception as e:
            messages.error(request, f'Có lỗi xảy ra: {str(e)}')
    
    # Lấy tất cả settings
    settings = SiteSettings.objects.all().order_by('key')
    contact_info = ContactInfo.objects.first()
    current_site = Site.objects.get_current()
    all_sites = Site.objects.all()
    
    # Tạo dict cho template
    settings_dict = {setting.key: setting.value for setting in settings}
    
    context = {
        'title': 'Cấu hình tổng hợp',
        'settings': settings,
        'settings_dict': settings_dict,
        'contact_info': contact_info,
        'current_site': current_site,
        'all_sites': all_sites,
        'opts': SiteSettings._meta,
    }
    
    return render(request, 'admin/config/site_config.html', context)

@staff_member_required
def quick_settings_api(request):
    """API để cập nhật nhanh các settings"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            key = data.get('key')
            value = data.get('value')
            
            if not key:
                return JsonResponse({'success': False, 'error': 'Key không được để trống'})
            
            setting, created = SiteSettings.objects.get_or_create(key=key)
            setting.value = value
            setting.save()
            
            return JsonResponse({
                'success': True, 
                'message': f'Đã cập nhật {key}',
                'created': created
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})


@staff_member_required
def logout_view(request):
    logout(request)
    return redirect('admin:login')