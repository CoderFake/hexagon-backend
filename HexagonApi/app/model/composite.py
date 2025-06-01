from . import db
from typing import List, Optional
from decimal import Decimal


# ================================================================
# User & Profile Entities
# ================================================================

class User(db.User):
    """User entity with enhanced functionality"""

    @classmethod
    def of(cls, user: db.User) -> "User":
        """Create composite User from database User"""
        return cls(**{c.name: getattr(user, c.name) for c in user.__table__.columns})

    def get_active_enrollments(self) -> List["StudentEnrollment"]:
        """Get active course enrollments"""
        return [
            enrollment for enrollment in self.enrollments
            if enrollment.status in [
                db.EnrollmentStatusEnum.PENDING,
                db.EnrollmentStatusEnum.ENROLLED, 
                db.EnrollmentStatusEnum.STUDYING
            ]
        ]

    def get_completed_courses_count(self) -> int:
        """Count completed courses"""
        return len([
            enrollment for enrollment in self.enrollments
            if enrollment.status == db.EnrollmentStatusEnum.COMPLETED
        ])


class UserProfile(db.UserProfile):
    """User profile with additional methods"""
    
    @classmethod
    def of(cls, profile: db.UserProfile) -> "UserProfile":
        """Create composite UserProfile from database UserProfile"""
        return cls(**{c.name: getattr(profile, c.name) for c in profile.__table__.columns})


# ================================================================
# Course Entities
# ================================================================

class CourseCategory(db.CourseCategory):
    """Course category with enhanced functionality"""

    @classmethod
    def of(cls, category: db.CourseCategory) -> "CourseCategory":
        """Create composite CourseCategory from database CourseCategory"""
        return cls(**{c.name: getattr(category, c.name) for c in category.__table__.columns})

    def get_active_courses_count(self) -> int:
        """Count active courses in this category"""
        return len([course for course in self.courses if course.is_active])


class Course(db.Course):
    """Course entity with business logic"""

    @classmethod
    def of(cls, course: db.Course) -> "Course":
        """Create composite Course from database Course"""
        instance = cls(**{c.name: getattr(course, c.name) for c in course.__table__.columns})
        # Copy relationships
        if hasattr(course, 'category') and course.category:
            instance.category = course.category
        if hasattr(course, 'classes'):
            instance.classes = course.classes
        if hasattr(course, 'files'):
            instance.files = course.files
        if hasattr(course, 'outstanding_students'):
            instance.outstanding_students = course.outstanding_students
        if hasattr(course, 'roadmap'):
            instance.roadmap = course.roadmap
        if hasattr(course, 'additional_info'):
            instance.additional_info = course.additional_info
        return instance

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

    @classmethod
    def of(cls, course_class: db.CourseClass) -> "CourseClass":
        """Create composite CourseClass from database CourseClass"""
        instance = cls(**{c.name: getattr(course_class, c.name) for c in course_class.__table__.columns})
        # Copy relationships
        if hasattr(course_class, 'course') and course_class.course:
            instance.course = course_class.course
        if hasattr(course_class, 'content_blocks'):
            instance.content_blocks = course_class.content_blocks
        if hasattr(course_class, 'enrollments'):
            instance.enrollments = course_class.enrollments
        return instance

    @property
    def current_students_count(self) -> int:
        """Current number of enrolled students"""
        return len([
            enrollment for enrollment in self.enrollments
            if enrollment.status in [db.EnrollmentStatusEnum.PENDING, db.EnrollmentStatusEnum.ENROLLED, db.EnrollmentStatusEnum.STUDYING]
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
    
    @classmethod
    def of(cls, file: db.CourseFile) -> "CourseFile":
        """Create composite CourseFile from database CourseFile"""
        return cls(**{c.name: getattr(file, c.name) for c in file.__table__.columns})

    @property
    def file_size_display(self) -> str:
        """Display file size in human readable format"""
        if not self.file_size:
            return "N/A"
        
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    @property
    def file_extension(self) -> str:
        """Get file extension from file_key"""
        if '.' in self.file_key:
            return self.file_key.split('.')[-1].upper()
        return self.file_type.upper() if self.file_type else "FILE"

    def can_download(self, user: Optional["User"] = None) -> bool:
        """Check if file can be downloaded"""
        if not self.is_active:
            return False
        
        if not self.is_downloadable:
            return False
        
        if self.permission_level == "public":
            return True
        elif self.permission_level == "enrolled":
            if not user:
                return False
            return self._is_user_enrolled_in_course(user)
        elif self.permission_level == "admin":
            if not user:
                return False
            return getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False)
        
        return True

    def _is_user_enrolled_in_course(self, user: "User") -> bool:
        """Check if user is enrolled in this course"""
        if not hasattr(user, 'enrollments'):
            return False
        
        for enrollment in user.enrollments:
            if (enrollment.course_id == self.course_id and 
                enrollment.status in [db.EnrollmentStatusEnum.PENDING, db.EnrollmentStatusEnum.ENROLLED, db.EnrollmentStatusEnum.STUDYING] and
                enrollment.is_active):
                return True
        return False

    def increment_download_count(self) -> None:
        """Increment download count"""
        self.download_count += 1


class CourseRoadmap(db.CourseRoadmap):
    """Course roadmap with content management"""

    @classmethod
    def of(cls, roadmap: db.CourseRoadmap) -> "CourseRoadmap":
        """Create composite CourseRoadmap from database CourseRoadmap"""
        instance = cls(**{c.name: getattr(roadmap, c.name) for c in roadmap.__table__.columns})
        if hasattr(roadmap, 'content_blocks'):
            instance.content_blocks = roadmap.content_blocks
        return instance

    def get_active_content_blocks(self) -> List["RoadmapContentBlock"]:
        """Get active content blocks ordered"""
        return [block for block in self.content_blocks if block.is_active]


class OutstandingStudent(db.OutstandingStudent):
    """Outstanding student showcase"""

    @classmethod
    def of(cls, student: db.OutstandingStudent) -> "OutstandingStudent":
        """Create composite OutstandingStudent from database OutstandingStudent"""
        return cls(**{c.name: getattr(student, c.name) for c in student.__table__.columns})

    @property
    def awards_display(self) -> str:
        """Display awards as comma-separated string"""
        return ", ".join(self.awards) if self.awards else ""


class CourseAdditionalInfo(db.CourseAdditionalInfo):
    """Course additional information"""

    @classmethod
    def of(cls, info: db.CourseAdditionalInfo) -> "CourseAdditionalInfo":
        """Create composite CourseAdditionalInfo from database CourseAdditionalInfo"""
        instance = cls(**{c.name: getattr(info, c.name) for c in info.__table__.columns})
        if hasattr(info, 'content_blocks'):
            instance.content_blocks = info.content_blocks
        return instance

    def get_active_content_blocks(self) -> List["CourseAdditionalContentBlock"]:
        """Get active content blocks"""
        return [block for block in self.content_blocks if block.is_active]


# ================================================================
# Enrollment Entities
# ================================================================

class StudentEnrollment(db.StudentCourseEnrollment):
    """Student enrollment with payment tracking"""

    @classmethod
    def of(cls, enrollment: db.StudentCourseEnrollment) -> "StudentEnrollment":
        """Create composite StudentEnrollment from database StudentCourseEnrollment"""
        instance = cls(**{c.name: getattr(enrollment, c.name) for c in enrollment.__table__.columns})
        if hasattr(enrollment, 'course') and enrollment.course:
            instance.course = enrollment.course
        if hasattr(enrollment, 'course_class') and enrollment.course_class:
            instance.course_class = enrollment.course_class
        if hasattr(enrollment, 'user') and enrollment.user:
            instance.user = enrollment.user
        return instance

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
            db.EnrollmentStatusEnum.PENDING: 'Chờ xác nhận',
            db.EnrollmentStatusEnum.ENROLLED: 'Đã đăng ký',
            db.EnrollmentStatusEnum.STUDYING: 'Đang học',
            db.EnrollmentStatusEnum.COMPLETED: 'Hoàn thành',
            db.EnrollmentStatusEnum.DROPPED: 'Bỏ học'
        }
        return status_map.get(self.status, self.status.value)

    @property
    def payment_status_display(self) -> str:
        """Human readable payment status"""
        payment_map = {
            db.PaymentStatusEnum.UNPAID: 'Chưa thanh toán',
            db.PaymentStatusEnum.PARTIAL: 'Thanh toán một phần',
            db.PaymentStatusEnum.PAID: 'Đã thanh toán đủ'
        }
        return payment_map.get(self.payment_status, self.payment_status.value)

    def is_payment_complete(self) -> bool:
        """Check if payment is complete"""
        return self.payment_status == db.PaymentStatusEnum.PAID


# ================================================================
# News Entities
# ================================================================

class NewsCategory(db.NewsCategory):
    """News category with enhanced functionality"""

    @classmethod
    def of(cls, category: db.NewsCategory) -> "NewsCategory":
        """Create composite NewsCategory from database NewsCategory"""
        instance = cls(**{c.name: getattr(category, c.name) for c in category.__table__.columns})
        if hasattr(category, 'course') and category.course:
            instance.course = category.course
        if hasattr(category, 'news'):
            instance.news = category.news
        return instance

    def get_published_news_count(self) -> int:
        """Count published news in this category"""
        return len([news for news in self.news if news.is_published and news.is_active])

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
    """News entity with business logic"""

    @classmethod
    def of(cls, news: db.News) -> "News":
        """Create composite News from database News"""
        instance = cls(**{c.name: getattr(news, c.name) for c in news.__table__.columns})
        if hasattr(news, 'category') and news.category:
            instance.category = news.category
        if hasattr(news, 'content_blocks'):
            instance.content_blocks = news.content_blocks
        return instance

    def get_active_content_blocks(self) -> List["NewsContentBlock"]:
        """Get active content blocks ordered"""
        return [block for block in self.content_blocks if block.is_active]

    def increment_view_count(self) -> None:
        """Increment view count"""
        self.view_count += 1

    @property
    def is_recently_published(self) -> bool:
        """Check if news was published recently (within 7 days)"""
        if not self.published_at:
            return False
        from datetime import datetime, timedelta
        return self.published_at >= datetime.now() - timedelta(days=7)


class NewsContentBlock(db.NewsContentBlock):
    """News content block"""

    @classmethod
    def of(cls, block: db.NewsContentBlock) -> "NewsContentBlock":
        """Create composite NewsContentBlock from database NewsContentBlock"""
        instance = cls(**{c.name: getattr(block, c.name) for c in block.__table__.columns})
        if hasattr(block, 'news') and block.news:
            instance.news = block.news
        return instance


# ================================================================
# Website Settings & Configuration Entities
# ================================================================

class SiteSettings(db.SiteSettings):
    """Site settings with enhanced functionality"""

    @classmethod
    def of(cls, settings: db.SiteSettings) -> "SiteSettings":
        """Create composite SiteSettings from database SiteSettings"""
        return cls(**{c.name: getattr(settings, c.name) for c in settings.__table__.columns})

    def get_typed_value(self):
        """Get value converted to appropriate type"""
        if self.data_type == "boolean":
            return self.value.lower() in ("true", "1", "yes")
        elif self.data_type == "number":
            try:
                return float(self.value)
            except ValueError:
                return 0
        elif self.data_type == "json":
            import json
            try:
                return json.loads(self.value)
            except json.JSONDecodeError:
                return {}
        return self.value


class ContactInfo(db.ContactInfo):
    """Contact information"""

    @classmethod
    def of(cls, contact: db.ContactInfo) -> "ContactInfo":
        """Create composite ContactInfo from database ContactInfo"""
        return cls(**{c.name: getattr(contact, c.name) for c in contact.__table__.columns})


class FAQ(db.FAQ):
    """FAQ with enhanced functionality"""

    @classmethod
    def of(cls, faq: db.FAQ) -> "FAQ":
        """Create composite FAQ from database FAQ"""
        instance = cls(**{c.name: getattr(faq, c.name) for c in faq.__table__.columns})
        if hasattr(faq, 'category') and faq.category:
            instance.category = CourseCategory.of(faq.category)
        return instance


class Banner(db.Banner):
    """Banner with enhanced functionality"""

    @classmethod
    def of(cls, banner: db.Banner) -> "Banner":
        """Create composite Banner from database Banner"""
        return cls(**{c.name: getattr(banner, c.name) for c in banner.__table__.columns})

    def is_active_now(self) -> bool:
        """Check if banner is currently active"""
        from datetime import datetime
        now = datetime.now()
        
        if not self.is_active:
            return False
            
        if self.start_date and now < self.start_date:
            return False
            
        if self.end_date and now > self.end_date:
            return False
            
        return True


class ContactInquiry(db.ContactInquiry):
    """Contact inquiry with enhanced functionality"""

    @classmethod
    def of(cls, inquiry: db.ContactInquiry) -> "ContactInquiry":
        """Create composite ContactInquiry from database ContactInquiry"""
        instance = cls(**{c.name: getattr(inquiry, c.name) for c in inquiry.__table__.columns})
        if hasattr(inquiry, 'course') and inquiry.course:
            instance.course = Course.of(inquiry.course)
        if hasattr(inquiry, 'course_class') and inquiry.course_class:
            instance.course_class = CourseClass.of(inquiry.course_class)
        return instance

    @property
    def status_display(self) -> str:
        """Human readable status"""
        status_map = {
            "new": "Mới",
            "contacted": "Đã liên hệ",
            "converted": "Đã chuyển đổi",
            "closed": "Đã đóng"
        }
        return status_map.get(self.status, self.status)

    @property
    def inquiry_type_display(self) -> str:
        """Human readable inquiry type"""
        type_map = {
            "course_inquiry": "Tư vấn khóa học",
            "general_contact": "Liên hệ chung"
        }
        return type_map.get(self.inquiry_type, self.inquiry_type)