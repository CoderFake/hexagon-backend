import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from functools import cached_property
from jinja2 import Environment, FileSystemLoader
import logging
import mimetypes
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------
# Settings
# ----------------------------------------------------------------
class SendEmailSettings(BaseModel):
    """Gmail SMTP email configuration settings."""
    
    host: str = Field(default="smtp.gmail.com", description="SMTP server host")
    port: int = Field(default=587, description="SMTP server port")
    username: str = Field(default="", description="Gmail username/email")
    password: str = Field(default="", description="Gmail app password")
    from_email: str = Field(default="info@hexagon.edu.vn", description="Default sender email")
    from_name: str = Field(default="Hexagon Education", description="Default sender name")
    template_dir: str = Field(default="app/templates/email", description="Email templates directory")
    static_dir: str = Field(default="app/static/email", description="Email static files directory")
    timeout: int = Field(default=30, description="SMTP connection timeout")


# ----------------------------------------------------------------
# Exceptions
# ----------------------------------------------------------------
class EmailError(Exception):
    """Base email service exception"""
    pass


class EmailSendError(EmailError):
    """Email sending error"""
    pass


class EmailTemplateError(EmailError):
    """Email template rendering error"""
    pass


# ----------------------------------------------------------------
# Gmail Email Service
# ----------------------------------------------------------------
class GmailEmailService:
    """Simple Gmail SMTP email service with image support."""
    
    def __init__(self, settings: SendEmailSettings) -> None:
        """Initialize Gmail email service with settings"""
        self.settings = settings
        self.embedded_images = {}  # Cache for embedded images
        
    @cached_property
    def template_env(self) -> Environment:
        """Get Jinja2 template environment"""
        template_dir = Path(self.settings.template_dir)
        if not template_dir.exists():
            template_dir.mkdir(parents=True, exist_ok=True)
        
        return Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True
        )
    
    @cached_property
    def static_dir(self) -> Path:
        """Get static files directory"""
        static_dir = Path(self.settings.static_dir)
        if not static_dir.exists():
            static_dir.mkdir(parents=True, exist_ok=True)
        return static_dir
    
    def test_connection(self) -> bool:
        """Test Gmail SMTP connection"""
        try:
            with self._create_smtp_connection() as server:
                server.noop()
            logger.info("Gmail SMTP connection test successful")
            return True
        except Exception as e:
            logger.error(f"Gmail SMTP connection test failed: {e}")
            return False
    
    def send_template_email(
        self,
        to_emails: Union[str, List[str]],
        subject: str,
        template_name: str,
        context: Dict[str, Any],
        cc_emails: Optional[Union[str, List[str]]] = None,
        bcc_emails: Optional[Union[str, List[str]]] = None,
        images: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Send templated email using Jinja2 templates with image support
        
        Args:
            to_emails: Recipient email(s)
            subject: Email subject
            template_name: Template name (without .html extension)
            context: Template context data
            cc_emails: CC email(s)
            bcc_emails: BCC email(s)
            images: Dict of {cid: file_path} for embedded images
                   Use in template as: <img src="cid:logo">
        """
        
        # Convert to lists
        to_list = [to_emails] if isinstance(to_emails, str) else to_emails
        cc_list = []
        if cc_emails:
            cc_list = [cc_emails] if isinstance(cc_emails, str) else cc_emails
        bcc_list = []
        if bcc_emails:
            bcc_list = [bcc_emails] if isinstance(bcc_emails, str) else bcc_emails
        
        try:
            # Add image context for templates
            if images:
                context = context.copy()
                context['images'] = {cid: f"cid:{cid}" for cid in images.keys()}
            
            # Render HTML template
            html_template = self.template_env.get_template(f"{template_name}.html")
            body_html = html_template.render(**context)
            
            # Try to render text template (optional)
            body_text = None
            try:
                text_template = self.template_env.get_template(f"{template_name}.txt")
                body_text = text_template.render(**context)
            except:
                pass
            
            return self._send_email_with_images(
                to_emails=to_list,
                subject=subject,
                body_html=body_html,
                body_text=body_text,
                cc_emails=cc_list,
                bcc_emails=bcc_list,
                images=images
            )
            
        except Exception as e:
            logger.error(f"Failed to send template email: {e}")
            raise EmailSendError(f"Template email send failed: {e}")
    
    def send_simple_email(
        self,
        to_emails: Union[str, List[str]],
        subject: str,
        body: str,
        is_html: bool = False,
        cc_emails: Optional[Union[str, List[str]]] = None,
        bcc_emails: Optional[Union[str, List[str]]] = None,
        images: Optional[Dict[str, str]] = None
    ) -> bool:
        """Send simple text or HTML email with optional images"""
        
        # Convert to lists
        to_list = [to_emails] if isinstance(to_emails, str) else to_emails
        cc_list = []
        if cc_emails:
            cc_list = [cc_emails] if isinstance(cc_emails, str) else cc_emails
        bcc_list = []
        if bcc_emails:
            bcc_list = [bcc_emails] if isinstance(bcc_emails, str) else bcc_emails
        
        return self._send_email_with_images(
            to_emails=to_list,
            subject=subject,
            body_html=body if is_html else None,
            body_text=body if not is_html else None,
            cc_emails=cc_list,
            bcc_emails=bcc_list,
            images=images
        )
    
    def _send_email_with_images(
        self,
        to_emails: List[str],
        subject: str,
        body_html: Optional[str] = None,
        body_text: Optional[str] = None,
        cc_emails: Optional[List[str]] = None,
        bcc_emails: Optional[List[str]] = None,
        images: Optional[Dict[str, str]] = None
    ) -> bool:
        """Internal method to send email with embedded images"""
        try:
            # Create message structure
            if images:
                msg = MIMEMultipart('related')

                msg_alternative = MIMEMultipart('alternative')
                msg.attach(msg_alternative)

                if body_text:
                    text_part = MIMEText(body_text, 'plain', 'utf-8')
                    msg_alternative.attach(text_part)
                
                if body_html:
                    html_part = MIMEText(body_html, 'html', 'utf-8')
                    msg_alternative.attach(html_part)
                
                for cid, image_path in images.items():
                    self._attach_image(msg, cid, image_path)
            else:
                msg = MIMEMultipart('alternative')
                
                if body_text:
                    text_part = MIMEText(body_text, 'plain', 'utf-8')
                    msg.attach(text_part)
                
                if body_html:
                    html_part = MIMEText(body_html, 'html', 'utf-8')
                    msg.attach(html_part)
            
            msg['From'] = f"{self.settings.from_name} <{self.settings.from_email}>"
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject
            
            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)
            
            all_recipients = to_emails[:]
            if cc_emails:
                all_recipients.extend(cc_emails)
            if bcc_emails:
                all_recipients.extend(bcc_emails)
            
            with self._create_smtp_connection() as server:
                server.send_message(msg, to_addrs=all_recipients)
            
            logger.info(f"Email sent successfully to {len(to_emails)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise EmailSendError(f"Gmail SMTP send failed: {e}")
    
    def _attach_image(self, msg: MIMEMultipart, cid: str, image_path: str) -> None:
        """Attach image as embedded content"""
        try:
            if Path(image_path).is_absolute():
                img_path = Path(image_path)
            else:
                img_path = self.static_dir / image_path
            
            if not img_path.exists():
                logger.warning(f"Image not found: {img_path}")
                return
            
            with open(img_path, 'rb') as f:
                img_data = f.read()
            
            mime_type, _ = mimetypes.guess_type(str(img_path))
            if mime_type and mime_type.startswith('image/'):
                img_subtype = mime_type.split('/')[1]
            else:
                img_subtype = 'png'
            
            img = MIMEImage(img_data, img_subtype)
            img.add_header('Content-ID', f'<{cid}>')
            img.add_header('Content-Disposition', 'inline', filename=img_path.name)
            
            msg.attach(img)
            logger.debug(f"Attached image: {cid} -> {img_path}")
            
        except Exception as e:
            logger.error(f"Failed to attach image {cid}: {e}")
    
    def _create_smtp_connection(self):
        """Create Gmail SMTP connection with TLS"""
        try:
            server = smtplib.SMTP(
                self.settings.host,
                self.settings.port,
                timeout=self.settings.timeout
            )
            
            context = ssl.create_default_context()
            server.starttls(context=context)
            server.login(self.settings.username, self.settings.password)
            
            return server
            
        except Exception as e:
            logger.error(f"Failed to create Gmail SMTP connection: {e}")
            raise EmailSendError(f"Gmail SMTP connection failed: {e}")


# ----------------------------------------------------------------
# Helper Functions
# ----------------------------------------------------------------
def build_user_context(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Build context for user-related emails"""
    return {
        'user': user_data,
        'full_name': f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip(),
        'first_name': user_data.get('first_name', ''),
        'email': user_data.get('email', ''),
    }


def build_inquiry_context(inquiry_data: Dict[str, Any], course_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Build context for inquiry confirmation emails"""
    context = {
        'inquiry': inquiry_data,
        'student_name': inquiry_data.get('student_name', ''),
        'contact_name': inquiry_data.get('contact_name', ''),
        'student_age': inquiry_data.get('student_age', ''),
        'message': inquiry_data.get('message', ''),
        'phone': inquiry_data.get('phone', ''),
        'preferred_contact_time': inquiry_data.get('preferred_contact_time', ''),
    }
    
    if course_data:
        context.update({
            'course': course_data,
            'course_name': course_data.get('name', ''),
            'category_name': course_data.get('category', {}).get('name', ''),
            'course_price': course_data.get('price', 0),
        })
    
    return context


def build_enrollment_context(enrollment_data: Dict[str, Any]) -> Dict[str, Any]:
    """Build context for enrollment confirmation emails"""
    return {
        'enrollment': enrollment_data,
        'student_name': enrollment_data.get('student_name', ''),
        'student_id': enrollment_data.get('student_id', ''),
        'course': enrollment_data.get('course', {}),
        'course_name': enrollment_data.get('course', {}).get('name', ''),
        'tuition_fee': enrollment_data.get('tuition_fee', 0),
        'paid_amount': enrollment_data.get('paid_amount', 0),
        'remaining_fee': enrollment_data.get('remaining_fee', 0),
        'enrollment_date': enrollment_data.get('enrollment_date', ''),
        'start_date': enrollment_data.get('start_date', ''),
    }
