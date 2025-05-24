"""
Email Service Usage Examples
Ví dụ cách sử dụng email service với HTML templates và hình ảnh embedded
"""

from app.ext.email.base import GmailEmailService, SendEmailSettings, build_user_context
from app.config import settings  # Assume config exists

# ----------------------------------------------------------------
# Initialize Email Service
# ----------------------------------------------------------------
def get_email_service() -> GmailEmailService:
    """Khởi tạo email service với config"""
    email_settings = SendEmailSettings(
        username=settings.gmail_username,
        password=settings.gmail_password,
        from_email=settings.gmail_from_email,
        from_name="Hexagon Education",
        template_dir="app/templates/email",
        static_dir="app/static/email"
    )
    
    return GmailEmailService(email_settings)


# ----------------------------------------------------------------
# Usage Examples
# ----------------------------------------------------------------

async def send_welcome_email_with_images(user_data: dict, course_data: dict = None):
    """
    Gửi email chào mừng với hình ảnh embedded
    
    Structure thư mục:
    app/static/email/
    ├── logo.png              # Logo công ty
    ├── course_default.jpg    # Hình mặc định cho khóa học
    ├── social/
    │   ├── facebook.png
    │   ├── youtube.png
    │   └── instagram.png
    """
    
    email_service = get_email_service()
    
    # Build context data
    context = build_user_context(user_data)
    context.update({
        'course': course_data,
        'website_url': 'https://hexagon-education.com',
        'address': 'Hà Nội, Việt Nam',
        'phone': '0123-456-789',
        'contact_email': 'info@hexagon-education.com',
        'social': {
            'facebook': 'https://facebook.com/hexagon-education',
            'youtube': 'https://youtube.com/hexagon-education',
            'instagram': 'https://instagram.com/hexagon-education'
        }
    })
    
    # Define embedded images
    images = {
        'logo': 'logo.png',  # app/static/email/logo.png
        'course': course_data.get('image', 'course_default.jpg'),
        'facebook': 'social/facebook.png',
        'youtube': 'social/youtube.png',
        'instagram': 'social/instagram.png'
    }
    
    try:
        success = email_service.send_template_email(
            to_emails=user_data['email'],
            subject="🎉 Chào mừng bạn đến với Hexagon Education!",
            template_name="welcome",  # welcome.html
            context=context,
            images=images
        )
        
        if success:
            print(f"✅ Email gửi thành công đến {user_data['email']}")
        else:
            print(f"❌ Gửi email thất bại")
            
    except Exception as e:
        print(f"❌ Lỗi gửi email: {e}")


async def send_course_inquiry_confirmation(inquiry_data: dict):
    """Gửi email xác nhận yêu cầu tư vấn khóa học"""
    
    email_service = get_email_service()
    
    context = {
        'student_name': inquiry_data['student_name'],
        'contact_name': inquiry_data['contact_name'],
        'course_name': inquiry_data['course_name'],
        'message': inquiry_data['message'],
        'phone': inquiry_data['phone']
    }
    
    images = {
        'logo': 'logo.png'
    }
    
    # Tạo template đơn giản trong code
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="text-align: center; padding: 20px;">
            <img src="cid:logo" style="max-width: 200px;" alt="Logo">
            <h2>Cảm ơn bạn đã quan tâm!</h2>
        </div>
        
        <div style="padding: 20px; background-color: #f8f9fa; border-radius: 8px;">
            <p>Xin chào <strong>{context['contact_name']}</strong>,</p>
            
            <p>Chúng tôi đã nhận được yêu cầu tư vấn của bạn về khóa học <strong>{context['course_name']}</strong>.</p>
            
            <div style="background-color: white; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h4>Thông tin yêu cầu:</h4>
                <p><strong>Tên học viên:</strong> {context['student_name']}</p>
                <p><strong>Người liên hệ:</strong> {context['contact_name']}</p>
                <p><strong>Số điện thoại:</strong> {context['phone']}</p>
                <p><strong>Tin nhắn:</strong> {context['message']}</p>
            </div>
            
            <p>Đội ngũ tư vấn của chúng tôi sẽ liên hệ với bạn trong vòng 24h.</p>
            
            <p>Trân trọng,<br>
            <strong>Hexagon Education</strong></p>
        </div>
    </div>
    """
    
    try:
        success = email_service.send_simple_email(
            to_emails=inquiry_data['email'],
            subject=f"Xác nhận yêu cầu tư vấn - {inquiry_data['course_name']}",
            body=html_content,
            is_html=True,
            images=images
        )
        
        if success:
            print(f"✅ Email xác nhận gửi đến {inquiry_data['email']}")
            
    except Exception as e:
        print(f"❌ Lỗi gửi email xác nhận: {e}")


async def send_enrollment_notification(enrollment_data: dict):
    """Gửi email thông báo đăng ký thành công"""
    
    email_service = get_email_service()
    
    # Sử dụng absolute path cho hình ảnh
    images = {
        'logo': '/absolute/path/to/logo.png',  # Có thể dùng absolute path
        'certificate': 'certificates/sample.png'  # Hoặc relative path
    }
    
    context = {
        'student_name': enrollment_data['student_name'],
        'course_name': enrollment_data['course_name'],
        'enrollment_date': enrollment_data['enrollment_date'],
        'start_date': enrollment_data['start_date'],
        'tuition_fee': enrollment_data['tuition_fee'],
        'student_id': enrollment_data['student_id']
    }
    
    # Template content
    template_content = """
    <h2>🎉 Đăng ký thành công!</h2>
    <img src="cid:logo" style="max-width: 150px;">
    
    <p>Xin chào {{ student_name }},</p>
    
    <div style="background: #e8f5e8; padding: 20px; border-radius: 8px;">
        <h3>✅ Thông tin đăng ký</h3>
        <p><strong>Khóa học:</strong> {{ course_name }}</p>
        <p><strong>Mã học viên:</strong> {{ student_id }}</p>
        <p><strong>Ngày đăng ký:</strong> {{ enrollment_date }}</p>
        <p><strong>Ngày bắt đầu:</strong> {{ start_date }}</p>
        <p><strong>Học phí:</strong> {{ tuition_fee | number_format }}đ</p>
    </div>
    
    <img src="cid:certificate" style="max-width: 100%; margin: 20px 0;">
    
    <p>Chúc bạn học tập hiệu quả! 📚</p>
    """
    
    # Render template string trực tiếp
    from jinja2 import Template
    template = Template(template_content)
    html_body = template.render(**context)
    
    try:
        success = email_service.send_simple_email(
            to_emails=enrollment_data['email'],
            subject="🎓 Đăng ký khóa học thành công",
            body=html_body,
            is_html=True,
            images=images
        )
        
        if success:
            print(f"✅ Email đăng ký gửi đến {enrollment_data['email']}")
            
    except Exception as e:
        print(f"❌ Lỗi gửi email đăng ký: {e}")


# ----------------------------------------------------------------
# FastAPI Integration Example
# ----------------------------------------------------------------

from fastapi import APIRouter

router = APIRouter()

@router.post("/send-welcome")
async def api_send_welcome_email(request_data: dict):
    """API endpoint để gửi welcome email"""
    
    user_data = {
        'email': request_data['email'],
        'first_name': request_data['first_name'],
        'last_name': request_data.get('last_name', ''),
        'created_at': request_data.get('created_at')
    }
    
    course_data = request_data.get('course')
    
    await send_welcome_email_with_images(user_data, course_data)
    
    return {"message": "Email sent successfully"}


@router.post("/send-inquiry-confirmation") 
async def api_send_inquiry_confirmation(request_data: dict):
    """API endpoint để gửi email xác nhận tư vấn"""
    
    await send_course_inquiry_confirmation(request_data)
    
    return {"message": "Confirmation email sent"}


# ----------------------------------------------------------------
# Test Function
# ----------------------------------------------------------------

async def test_email_service():
    """Test email service với dữ liệu mẫu"""
    
    # Test data
    test_user = {
        'email': 'test@example.com',
        'first_name': 'Nguyễn',
        'last_name': 'Văn A',
        'created_at': '2024-01-15'
    }
    
    test_course = {
        'name': 'Lập trình Python cơ bản',
        'description': 'Khóa học Python dành cho người mới bắt đầu',
        'price': 2500000,
        'image': 'courses/python.jpg'
    }
    
    # Test welcome email
    print("🧪 Testing welcome email...")
    await send_welcome_email_with_images(test_user, test_course)
    
    # Test inquiry confirmation
    print("🧪 Testing inquiry confirmation...")
    inquiry_data = {
        'email': 'test@example.com',
        'student_name': 'Nguyễn Thị B',
        'contact_name': 'Nguyễn Văn A', 
        'course_name': 'Lập trình Python cơ bản',
        'message': 'Tôi muốn tìm hiểu thêm về khóa học này',
        'phone': '0987654321'
    }
    await send_course_inquiry_confirmation(inquiry_data)


if __name__ == "__main__":
    import asyncio
    
    # Chạy test
    asyncio.run(test_email_service()) 