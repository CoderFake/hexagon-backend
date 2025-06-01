from typing import Optional, List
from datetime import datetime

import app.model.composite as c
from app.ext.email.base import GmailEmailService
from .commons import service, Maybe, Errors, r
from .website import get_site_setting_by_key, get_contact_info


@service
async def get_email_service() -> Maybe[GmailEmailService]:
    """Get configured email service from app resources"""
    try:
        return r.email
    except Exception as e:
        print(f"Failed to get email service: {e}")
        return Errors.CONFIGURATION_ERROR


@service 
async def send_contact_inquiry_notifications(inquiry: c.ContactInquiry) -> Maybe[bool]:
    """Send notification emails for contact inquiry - both admin and customer"""
    admin_result = await send_contact_inquiry_admin_notification(inquiry)
    customer_result = True
    if inquiry.email:
        customer_result = await send_contact_inquiry_customer_confirmation(inquiry)
    
    return admin_result


@service
async def send_contact_inquiry_admin_notification(inquiry: c.ContactInquiry) -> Maybe[bool]:
    """Send notification email to admin when new contact inquiry is received"""
    admin_email_setting = await get_site_setting_by_key("admin_notification_email")
    if not admin_email_setting.get():
        return Errors.CONFIGURATION_ERROR
    
    admin_email = admin_email_setting.get().value
    email_service_result = await get_email_service()
    if not email_service_result.get():
        return email_service_result
    
    email_service = email_service_result.get()
    
    context = {
        "full_name": inquiry.full_name,
        "phone": inquiry.phone,
        "email": inquiry.email,
        "course_title": inquiry.course.title if inquiry.course else None,
        "class_title": inquiry.course_class.title if inquiry.course_class else None,
        "inquiry_type_display": inquiry.inquiry_type_display,
        "message": inquiry.message,
        "created_at": inquiry.created_at.strftime('%d/%m/%Y %H:%M'),
        "now": datetime.now().strftime('%d/%m/%Y %H:%M')
    }
    
    try:
        success = email_service.send_template_email(
            to_emails=[admin_email],
            subject=f"Đăng ký tư vấn mới từ {inquiry.full_name}",
            template_name="contact_inquiry_admin",
            context=context
        )
        return success
    except Exception as e:
        r.logger.error(f"Failed to send admin notification email: {e}")
        return Errors.INTERNAL_ERROR


@service
async def send_contact_inquiry_customer_confirmation(inquiry: c.ContactInquiry) -> Maybe[bool]:
    """Send confirmation email to customer after contact inquiry"""
    if not inquiry.email:
        return True 
    
    email_service_result = await get_email_service()
    if not email_service_result.get():
        return email_service_result
    
    email_service = email_service_result.get()
    
    contact_info_result = await get_contact_info()
    contact_info = contact_info_result.get() if contact_info_result.get() else None
    
    context = {
        "full_name": inquiry.full_name,
        "phone": inquiry.phone,
        "email": inquiry.email,
        "course_title": inquiry.course.title if inquiry.course else None,
        "class_title": inquiry.course_class.title if inquiry.course_class else None,
        "inquiry_type_display": inquiry.inquiry_type_display,
        "message": inquiry.message,
        "created_at": inquiry.created_at.strftime('%d/%m/%Y %H:%M'),
        "contact_phone": contact_info.phone if contact_info else None,
        "contact_email": contact_info.email if contact_info else None,
        "contact_address": contact_info.address if contact_info else None,
    }
    
    try:
        success = email_service.send_template_email(
            to_emails=[inquiry.email],
            subject="Xác nhận đăng ký tư vấn - Hexagon Education",
            template_name="contact_inquiry_customer",
            context=context
        )
        return success
    except Exception as e:
        r.logger.error(f"Failed to send customer confirmation email: {e}")
        return Errors.INTERNAL_ERROR


@service
async def send_enrollment_notifications(enrollment: c.StudentEnrollment) -> Maybe[bool]:
    """Send notification emails for enrollment - both admin and student"""
    admin_result = await send_enrollment_admin_notification(enrollment)
    student_result = await send_enrollment_welcome_email(enrollment)
    
    return admin_result


@service
async def send_enrollment_admin_notification(enrollment: c.StudentEnrollment) -> Maybe[bool]:
    """Send notification email to admin when new enrollment is created"""
    admin_email_setting = await get_site_setting_by_key("admin_notification_email")
    if not admin_email_setting.get():
        return Errors.CONFIGURATION_ERROR
    
    admin_email = admin_email_setting.get().value
    email_service_result = await get_email_service()
    if not email_service_result.get():
        return email_service_result
    
    email_service = email_service_result.get()
    
    method_display_map = {
        "admin": "Admin đăng ký",
        "class_code": "Nhập mã lớp", 
        "online_form": "Form online"
    }
    
    context = {
        "user_name": enrollment.user.full_name if enrollment.user else "N/A",
        "user_email": enrollment.user.email if enrollment.user else "N/A",
        "user_phone": enrollment.user.phone_number if enrollment.user else "N/A",
        "course_title": enrollment.course.title if enrollment.course else "N/A",
        "class_title": enrollment.course_class.title if enrollment.course_class else "N/A",
        "class_code": enrollment.course_class.class_code if enrollment.course_class else "N/A",
        "enrollment_method_display": method_display_map.get(enrollment.enrollment_method, enrollment.enrollment_method),
        "enrollment_date": enrollment.enrollment_date.strftime('%d/%m/%Y'),
        "status_display": enrollment.status_display,
        "tuition_fee": f"{enrollment.tuition_fee:,.0f}",
        "paid_amount": f"{enrollment.paid_amount:,.0f}",
        "remaining_fee": f"{enrollment.remaining_fee:,.0f}",
        "payment_status_display": enrollment.payment_status_display,
        "notes": enrollment.notes,
        "now": datetime.now().strftime('%d/%m/%Y %H:%M')
    }
    
    try:
        success = email_service.send_template_email(
            to_emails=[admin_email],
            subject=f"Đăng ký khóa học mới từ {enrollment.user.full_name}",
            template_name="enrollment_admin",
            context=context
        )
        return success
    except Exception as e:
        r.logger.error(f"Failed to send enrollment admin notification: {e}")
        return Errors.INTERNAL_ERROR


@service
async def send_enrollment_welcome_email(enrollment: c.StudentEnrollment) -> Maybe[bool]:
    """Send welcome email to student after enrollment"""
    if not enrollment.user.email:
        return True
    
    email_service_result = await get_email_service()
    if not email_service_result.get():
        return email_service_result
    
    email_service = email_service_result.get()
    
    contact_info_result = await get_contact_info()
    contact_info = contact_info_result.get() if contact_info_result.get() else None
    
    context = {
        "user_name": enrollment.user.full_name if enrollment.user else "N/A",
        "course_title": enrollment.course.title if enrollment.course else "N/A",
        "class_title": enrollment.course_class.title if enrollment.course_class else "N/A",
        "class_code": enrollment.course_class.class_code if enrollment.course_class else "N/A",
        "tuition_fee": f"{enrollment.tuition_fee:,.0f}",
        "enrollment_date": enrollment.enrollment_date.strftime('%d/%m/%Y'),
        "status_display": enrollment.status_display,
        "contact_phone": contact_info.phone if contact_info else None,
        "contact_email": contact_info.email if contact_info else None,
        "contact_address": contact_info.address if contact_info else None,
    }
    
    try:
        success = email_service.send_template_email(
            to_emails=[enrollment.user.email],
            subject=f"Chào mừng bạn đến với {enrollment.course_title}!",
            template_name="enrollment_welcome",
            context=context
        )
        return success
    except Exception as e:
        r.logger.error(f"Failed to send welcome email: {e}")
        return Errors.INTERNAL_ERROR 