from . import db
from typing import List, Optional
from decimal import Decimal


# ================================================================
# Account & Student Entities
# ================================================================

class Me(db.Account):
    """Authenticated user account"""
    pass


class StudentProfile(db.Student):
    """Student profile with additional methods"""

    @property
    def age(self) -> int:
        """Calculate age from date of birth"""
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    def get_active_enrollments(self) -> List["StudentEnrollment"]:
        """Get active course enrollments"""
        return [
            enrollment for enrollment in self.enrollments
            if enrollment.status in [db.EnrollmentStatusEnum.ENROLLED, db.EnrollmentStatusEnum.STUDYING]
        ]

    def get_completed_courses_count(self) -> int:
        """Count completed courses"""
        return len([
            enrollment for enrollment in self.enrollments
            if enrollment.status == db.EnrollmentStatusEnum.COMPLETED
        ])


# ================================================================
# Course Entities
# ================================================================

class CourseCategory(db.CourseCategory):
    """Course category with enhanced functionality"""

    def get_active_courses_count(self) -> int:
        """Count active courses in this category"""
        return len([course for course in self.courses if course.is_active])


class Course(db.Course):
    """Course entity with business logic"""

    def get_total_classes_count(self) -> int:
        """Get total number of classes"""
        return len([cls for cls in self.classes if cls.is_active])

    def get_total_files_count(self) -> int:
        """Get total number of files"""
        return len([file for file in self.files if file.is_active])

    def get_featured_outstanding_students(self) -> List["OutstandingStudent"]:
        """Get featured outstanding students"""
        return [
           student for student in self.outstanding_students
           if student.is_active
        ][:3]

    def has_roadmap(self) -> bool:
        """Check if course has roadmap"""
        return self.roadmap is not None and self.roadmap.is_active

    def has_additional_info(self) -> bool:
        """Check if course has additional info"""
        return self.additional_info is not None and self.additional_info.is_active


class CourseClass(db.CourseClass):
    """Course class with enrollment management"""

    @property
    def current_students_count(self) -> int:
        """Current number of enrolled students"""
        return len([
            enrollment for enrollment in self.enrollments
            if enrollment.status in [db.EnrollmentStatusEnum.ENROLLED, db.EnrollmentStatusEnum.STUDYING]
        ])

    @property
    def available_slots(self) -> int:
        """Available enrollment slots"""
        return max(0, self.max_students - self.current_students_count)

    @property
    def is_full(self) -> bool:
        """Check if class is full"""
        return self.available_slots == 0

    def can_enroll(self) -> bool:
        """Check if enrollment is possible"""
        return self.is_open_for_enrollment and not self.is_full and self.is_active

    def get_active_content_blocks(self) -> List["CourseContentBlock"]:
        """Get active content blocks"""
        return [block for block in self.content_blocks if block.is_active]


class CourseFile(db.CourseFile):
    """Course file with display methods"""

    @property
    def file_size_display(self) -> str:
        """Human readable file size"""
        if not self.file_size:
            return "N/A"

        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024.0:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024.0
        return f"{self.file_size:.1f} TB"


class CourseRoadmap(db.CourseRoadmap):
    """Course roadmap with content management"""

    def get_active_content_blocks(self) -> List["RoadmapContentBlock"]:
        """Get active content blocks ordered"""
        return [block for block in self.content_blocks if block.is_active]


class OutstandingStudent(db.OutstandingStudent):
    """Outstanding student showcase"""

    @property
    def awards_display(self) -> str:
        """Display awards as comma-separated string"""
        return ", ".join(self.awards) if self.awards else ""


class CourseAdditionalInfo(db.CourseAdditionalInfo):
    """Course additional information"""

    def get_active_content_blocks(self) -> List["CourseAdditionalContentBlock"]:
        """Get active content blocks"""
        return [block for block in self.content_blocks if block.is_active]


# ================================================================
# Enrollment Entities
# ================================================================

class StudentEnrollment(db.StudentCourseEnrollment):
    """Student enrollment with payment tracking"""

    @property
    def remaining_fee(self) -> Decimal:
        """Remaining tuition fee"""
        return self.tuition_fee - self.paid_amount

    @property
    def payment_percentage(self) -> float:
        """Payment completion percentage"""
        if self.tuition_fee == 0:
            return 100.0
        return float(self.paid_amount / self.tuition_fee * 100)

    @property
    def status_display(self) -> str:
        """Human readable status"""
        status_map = {
            db.EnrollmentStatusEnum.ENROLLED: 'Đã đăng ký',
            db.EnrollmentStatusEnum.STUDYING: 'Đang học',
            db.EnrollmentStatusEnum.COMPLETED: 'Hoàn thành',
            db.EnrollmentStatusEnum.DROPPED: 'Bỏ học',
            db.EnrollmentStatusEnum.SUSPENDED: 'Tạm ngừng'
        }
        return status_map.get(self.status, self.status.value)

    @property
    def payment_status_display(self) -> str:
        """Human readable payment status"""
        payment_map = {
            db.PaymentStatusEnum.UNPAID: 'Chưa thanh toán',
            db.PaymentStatusEnum.PARTIAL: 'Thanh toán một phần',
            db.PaymentStatusEnum.PAID: 'Đã thanh toán đủ',
            db.PaymentStatusEnum.REFUNDED: 'Đã hoàn tiền'
        }
        return payment_map.get(self.payment_status, self.payment_status.value)

    def is_payment_complete(self) -> bool:
        """Check if payment is complete"""
        return self.payment_status == db.PaymentStatusEnum.PAID


# ================================================================
# General Content Entities
# ================================================================

class GeneralRoadmap(db.GeneralRoadmap):
    """General roadmap for Hexagon"""

    def get_active_content_blocks(self) -> List["GeneralRoadmapContentBlock"]:
        """Get active content blocks"""
        return [block for block in self.content_blocks if block.is_active]


class AboutSection(db.AboutSection):
    """About section with content management"""

    def get_active_content_blocks(self) -> List["AboutContentBlock"]:
        """Get active content blocks"""
        return [block for block in self.content_blocks if block.is_active]


# ================================================================
# News Entities
# ================================================================

class NewsCategory(db.NewsCategory):
    """News category with filtering"""

    def get_published_news_count(self) -> int:
        """Count published news in this category"""
        return len([
            news for news in self.news
            if news.is_published and news.is_active
        ])

    @property
    def category_type_display(self) -> str:
        """Human readable category type"""
        type_map = {
            db.NewsCategoryTypeEnum.EXAM_RESULTS: 'Kết quả thi',
            db.NewsCategoryTypeEnum.UPCOMING_EVENTS: 'Sắp diễn ra',
            db.NewsCategoryTypeEnum.GENERAL: 'Tổng hợp'
        }
        return type_map.get(self.category_type, self.category_type.value)


class News(db.News):
    """News article with content management"""

    @property
    def reading_time(self) -> int:
        """Estimated reading time in minutes"""
        total_words = len(self.short_description.split())
        for block in self.content_blocks:
            if block.general_description:
                total_words += len(block.general_description.split())
            for desc in block.descriptions:
                total_words += len(desc.split())

        return max(1, total_words // 200)  # 200 words per minute

    def get_active_content_blocks(self) -> List["NewsContentBlock"]:
        """Get active content blocks"""
        return [block for block in self.content_blocks if block.is_active]

    def is_recently_published(self, days: int = 7) -> bool:
        """Check if recently published"""
        if not self.published_at:
            return False

        from datetime import datetime, timedelta
        cutoff = datetime.now() - timedelta(days=days)
        return self.published_at >= cutoff