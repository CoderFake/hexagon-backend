from . import db
from .db import CategoryEnum as DbCategory  # noqa: F401
from typing import List, Optional
from decimal import Decimal


# ----------------------------------------------------------------
# Entities
# ----------------------------------------------------------------
class Me(db.Account):
    pass


# ----------------------------------------------------------------
# User Entities
# ----------------------------------------------------------------
class User(db.User):
    """User entity with profile information"""
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def has_profile_picture(self) -> bool:
        return bool(self.profile and self.profile.profile_picture)


class UserProfile(db.UserProfile):
    """User profile entity with additional methods"""
    pass


# ----------------------------------------------------------------
# Course Entities  
# ----------------------------------------------------------------
class Subject(db.Subject):
    """Subject entity for course curriculum"""
    pass


class CourseCategory(db.CourseCategory):
    """Course category with enhanced functionality"""
    
    @property
    def age_range_display(self) -> str:
        return f"{self.age_range_min}-{self.age_range_max} tuổi"

    def is_suitable_for_age(self, age: int) -> bool:
        return self.age_range_min <= age <= self.age_range_max


class Course(db.Course):
    """Course entity with business logic"""
    
    @property
    def price_display(self) -> str:
        if self.price == 0:
            return "Miễn phí"
        return f"{self.price:,.0f} VNĐ"

    @property
    def total_hours(self) -> int:
        """Calculate total study hours from all subjects"""
        total = 0
        for cs in self.course_subjects:
            total += cs.lecture_hours + cs.tutorial_hours + cs.lab_hours
        return total

    def get_subjects_list(self) -> List[str]:
        """Get list of subject names in this course"""
        return [cs.subject.name for cs in self.course_subjects if cs.subject]


class CourseSubject(db.CourseSubject):
    """Course-Subject relationship with hour calculations"""
    
    @property
    def total_hours(self) -> int:
        return self.lecture_hours + self.tutorial_hours + self.lab_hours

    @property
    def hours_breakdown(self) -> dict:
        return {
            'lecture': self.lecture_hours,
            'tutorial': self.tutorial_hours,
            'lab': self.lab_hours,
            'total': self.total_hours
        }


class Alumni(db.Alumni):
    """Alumni showcase entity"""
    
    @property
    def display_name(self) -> str:
        return self.name

    def get_courses_attended_names(self) -> List[str]:
        """Get names of courses this alumni attended"""
        # Note: This would need proper relationship loading
        return []


# ----------------------------------------------------------------
# Material Entities
# ----------------------------------------------------------------
class MaterialCategory(db.MaterialCategory):
    """Material category for organizing learning resources"""
    
    def get_public_materials_count(self) -> int:
        """Count public materials in this category"""
        return len([m for m in self.materials if m.is_public and m.is_active])


class Material(db.Material):
    """Learning material entity"""
    
    @property
    def file_size_display(self) -> str:
        if not self.file_size:
            return "N/A"
        
        # Convert bytes to human readable format
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024.0:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024.0
        return f"{self.file_size:.1f} TB"

    @property
    def access_level_display(self) -> str:
        access_map = {
            'public': 'Công khai',
            'student': 'Học viên',
            'premium': 'Premium',
            'internal': 'Nội bộ'
        }
        return access_map.get(self.access_level.value, self.access_level.value)

    def can_access(self, user: Optional[User] = None) -> bool:
        """Check if user can access this material"""
        if not self.is_active or not self.is_public:
            return False
            
        if self.access_level == db.AccessLevelEnum.PUBLIC:
            return True
        elif self.access_level == db.AccessLevelEnum.STUDENT:
            return user is not None
        elif self.access_level == db.AccessLevelEnum.PREMIUM:
            # Would need premium check logic
            return user is not None
        elif self.access_level == db.AccessLevelEnum.INTERNAL:
            return False
        
        return False


# ----------------------------------------------------------------
# News Entities
# ----------------------------------------------------------------
class NewsCategory(db.NewsCategory):
    """News category for content organization"""
    
    def get_published_news_count(self) -> int:
        """Count published news in this category"""
        return len([n for n in self.news if n.is_published and n.is_active])


class News(db.News):
    """News/Blog post entity"""
    
    @property
    def author_name(self) -> str:
        if self.author:
            return self.author.full_name
        return "Unknown"

    @property
    def reading_time(self) -> int:
        """Estimate reading time in minutes based on content length"""
        word_count = len(self.content.split())
        return max(1, word_count // 200)  # Assume 200 words per minute

    def is_recently_published(self, days: int = 7) -> bool:
        """Check if news was published within given days"""
        if not self.published_at:
            return False
        
        from datetime import datetime, timedelta
        cutoff = datetime.now() - timedelta(days=days)
        return self.published_at >= cutoff


# ----------------------------------------------------------------
# Config Entities
# ----------------------------------------------------------------
class SiteSettings(db.SiteSettings):
    """Site configuration settings"""
    
    def get_typed_value(self):
        """Return value converted to appropriate type"""
        if self.data_type == 'number':
            try:
                return float(self.value)
            except ValueError:
                return 0
        elif self.data_type == 'boolean':
            return self.value.lower() in ('true', '1', 'yes')
        elif self.data_type == 'json':
            import json
            try:
                return json.loads(self.value)
            except json.JSONDecodeError:
                return {}
        return self.value


class ContactInfo(db.ContactInfo):
    """Contact information entity"""
    
    @property
    def display_address(self) -> str:
        return self.address

    @property
    def has_social_links(self) -> bool:
        return bool(self.facebook_url)


class FAQ(db.FAQ):
    """Frequently Asked Questions"""
    
    @property
    def question_preview(self) -> str:
        return self.question[:100] + "..." if len(self.question) > 100 else self.question


class Banner(db.Banner):
    """Website banner/advertisement"""
    
    def is_currently_active(self) -> bool:
        """Check if banner is currently active based on date range"""
        from datetime import datetime
        now = datetime.now()
        
        if not self.is_active:
            return False
            
        if self.start_date and now < self.start_date:
            return False
            
        if self.end_date and now > self.end_date:
            return False
            
        return True


# ----------------------------------------------------------------
# Enrollment Entities
# ----------------------------------------------------------------
class StudentInquiry(db.StudentInquiry):
    """Student inquiry for course consultation"""
    
    @property
    def contact_info(self) -> str:
        return f"{self.contact_name} - {self.email} - {self.phone}"

    @property
    def status_display(self) -> str:
        status_map = {
            'new': 'Mới',
            'contacted': 'Đã liên hệ',
            'scheduled': 'Đã hẹn',
            'enrolled': 'Đã ghi danh',
            'declined': 'Từ chối'
        }
        return status_map.get(self.status.value, self.status.value)


class CourseEnrollment(db.CourseEnrollment):
    """Course enrollment with payment tracking"""
    
    @property
    def remaining_fee(self) -> Decimal:
        return self.tuition_fee - self.paid_amount

    @property
    def payment_percentage(self) -> float:
        if self.tuition_fee == 0:
            return 100.0
        return float(self.paid_amount / self.tuition_fee * 100)

    @property
    def status_display(self) -> str:
        status_map = {
            'enrolled': 'Đã ghi danh',
            'studying': 'Đang học',
            'completed': 'Hoàn thành',
            'dropped': 'Bỏ học',
            'suspended': 'Tạm ngừng'
        }
        return status_map.get(self.status.value, self.status.value)

    @property
    def payment_status_display(self) -> str:
        payment_map = {
            'unpaid': 'Chưa thanh toán',
            'partial': 'Thanh toán một phần',
            'paid': 'Đã thanh toán đủ',
            'refunded': 'Đã hoàn tiền'
        }
        return payment_map.get(self.payment_status.value, self.payment_status.value)

    def is_payment_overdue(self) -> bool:
        """Check if payment is overdue (business logic would be added here)"""
        # This would need business rules for payment deadlines
        return self.payment_status in [db.PaymentStatusEnum.UNPAID, db.PaymentStatusEnum.PARTIAL]


