from . import db
from typing import List, Optional, TYPE_CHECKING
from decimal import Decimal
from dataclasses import dataclass, field
from datetime import datetime, date
from sqlalchemy import inspect

if TYPE_CHECKING:
    pass


# ================================================================
# User & Profile Entities
# ================================================================

@dataclass
class UserProfile:
    """User profile with additional methods"""
    id: str
    user_id: str
    bio: Optional[str] = None
    address: Optional[str] = None
    profile_picture: Optional[str] = None
    
    @classmethod
    def of(cls, profile: db.UserProfile) -> "UserProfile":
        """Create composite UserProfile from database UserProfile"""
        return cls(
            id=profile.id,
            user_id=profile.user_id,
            bio=profile.bio,
            address=profile.address,
            profile_picture=profile.profile_picture
        )


@dataclass
class StudentEnrollment:
    id: str
    user_id: str
    course_id: str
    course_class_id: str
    enrollment_date: Optional[date] = None
    enrollment_method: str = "admin"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str = "pending"
    tuition_fee: Decimal = Decimal('0')
    paid_amount: Decimal = Decimal('0')
    payment_status: str = "unpaid"
    final_grade: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    user: Optional["User"] = None
    course: Optional["Course"] = None
    course_class: Optional["CourseClass"] = None

    @classmethod
    def of(cls, enrollment: db.StudentCourseEnrollment) -> "StudentEnrollment":
        return cls(
            id=enrollment.id,
            user_id=enrollment.user_id,
            course_id=enrollment.course_id,
            course_class_id=enrollment.course_class_id,
            enrollment_date=enrollment.enrollment_date,
            enrollment_method=enrollment.enrollment_method.value if enrollment.enrollment_method else "admin",
            start_date=enrollment.start_date,
            end_date=enrollment.end_date,
            status=enrollment.status.value if enrollment.status else "pending",
            tuition_fee=enrollment.tuition_fee,
            paid_amount=enrollment.paid_amount,
            payment_status=enrollment.payment_status.value if enrollment.payment_status else "unpaid",
            final_grade=enrollment.final_grade,
            notes=enrollment.notes,
            is_active=enrollment.is_active,
            created_at=enrollment.created_at,
            updated_at=enrollment.updated_at,
            user=User.of(enrollment.user) if enrollment.user else None,
            course=Course.of(enrollment.course) if enrollment.course else None,
            course_class=CourseClass.of(enrollment.course_class) if enrollment.course_class else None
        )

    @property
    def remaining_fee(self) -> Decimal:
        """Calculate remaining fee"""
        return self.tuition_fee - self.paid_amount

    @property
    def payment_percentage(self) -> float:
        """Calculate payment percentage"""
        if self.tuition_fee == 0:
            return 100.0
        return float((self.paid_amount / self.tuition_fee) * 100)

    @property
    def status_display(self) -> str:
        """Human readable status"""
        status_map = {
            "pending": "Chờ xác nhận",
            "enrolled": "Đã đăng ký", 
            "studying": "Đang học",
            "completed": "Hoàn thành",
            "dropped": "Bỏ học"
        }
        return status_map.get(self.status, self.status)

    @property
    def payment_status_display(self) -> str:
        """Human readable payment status"""
        status_map = {
            "unpaid": "Chưa thanh toán",
            "partial": "Thanh toán một phần",
            "paid": "Đã thanh toán đủ"
        }
        return status_map.get(self.payment_status, self.payment_status)


@dataclass
class User:
    """User entity with enhanced functionality"""
    id: str
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: bool = True
    is_staff: bool = False
    is_superuser: bool = False
    date_joined: Optional[datetime] = None
    last_login: Optional[datetime] = None
    firebase_id: Optional[str] = None
    login_method: Optional[str] = None
    profile: Optional[UserProfile] = None
    student_profile: Optional["Student"] = None
    enrollments: List[StudentEnrollment] = field(default_factory=list)

    @classmethod
    def of(cls, user: db.User) -> "User":
        """Create composite User from database User"""
        profile = None
        if hasattr(user, 'profile') and user.profile:
            profile = UserProfile.of(user.profile)
        
        student_profile = None
        try:
            if hasattr(user, 'student_profile') and user.student_profile:
                student_profile = Student.of(user.student_profile)
        except:
            pass
            
        enrollments = []
        try:
            if hasattr(user, 'enrollments') and user.enrollments:
                enrollments = [StudentEnrollment.of(e) for e in user.enrollments]
        except:
            pass
        
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=user.full_name,
            password=user.password,
            phone_number=user.phone_number,
            is_active=user.is_active,
            is_staff=user.is_staff,
            is_superuser=user.is_superuser,
            date_joined=user.date_joined,
            last_login=user.last_login,
            firebase_id=user.firebase_id,
            login_method=user.login_method,
            profile=profile,
            student_profile=student_profile,
            enrollments=enrollments
        )

    def get_active_enrollments(self) -> List[StudentEnrollment]:
        """Get active course enrollments"""
        return [
            enrollment for enrollment in self.enrollments
            if enrollment.status in [
                db.EnrollmentStatusEnum.PENDING.value,
                db.EnrollmentStatusEnum.ENROLLED.value, 
                db.EnrollmentStatusEnum.STUDYING.value
            ]
        ]

    def get_completed_courses_count(self) -> int:
        """Count completed courses"""
        return len([
            enrollment for enrollment in self.enrollments
            if enrollment.status == db.EnrollmentStatusEnum.COMPLETED.value
        ])


# ================================================================
# Simple placeholder classes for other entities
# ================================================================

@dataclass
class CourseContentBlock:
    id: str
    course_class_id: str
    title: Optional[str] = None
    image_key: Optional[str] = None
    descriptions: List[str] = field(default_factory=list)
    order: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def of(cls, block: db.CourseContentBlock) -> "CourseContentBlock":
        return cls(
            id=block.id,
            course_class_id=block.course_class_id,
            title=block.title,
            image_key=block.image_key,
            descriptions=block.descriptions,
            order=block.order,
            is_active=block.is_active,
            created_at=block.created_at,
            updated_at=block.updated_at
        )


@dataclass
class CourseRoadmap:
    id: str
    course_id: str
    short_description: str
    image_key: Optional[str] = None
    slogan: str = ""
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    content_blocks: List["RoadmapContentBlock"] = field(default_factory=list)

    @classmethod
    def of(cls, roadmap: db.CourseRoadmap) -> "CourseRoadmap":
        return cls(
            id=roadmap.id,
            course_id=roadmap.course_id,
            short_description=roadmap.short_description,
            image_key=roadmap.image_key,
            slogan=roadmap.slogan,
            is_active=roadmap.is_active,
            created_at=roadmap.created_at,
            updated_at=roadmap.updated_at,
            content_blocks=[RoadmapContentBlock.of(b) for b in roadmap.content_blocks] if roadmap.content_blocks else []
        )

    def get_active_content_blocks(self) -> List["RoadmapContentBlock"]:
        """Get active content blocks ordered"""
        return [block for block in self.content_blocks if block.is_active]


@dataclass
class RoadmapContentBlock:
    id: str
    roadmap_id: str
    title: Optional[str] = None
    image_key: Optional[str] = None
    descriptions: List[str] = field(default_factory=list)
    general_description: Optional[str] = None
    order: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def of(cls, block: db.RoadmapContentBlock) -> "RoadmapContentBlock":
        return cls(
            id=block.id,
            roadmap_id=block.roadmap_id,
            title=block.title,
            image_key=block.image_key,
            descriptions=block.descriptions,
            general_description=block.general_description,
            order=block.order,
            is_active=block.is_active,
            created_at=block.created_at,
            updated_at=block.updated_at
        )


@dataclass
class OutstandingStudent:
    id: str
    course_id: str
    name: str
    image_key: Optional[str] = None
    awards: List[str] = field(default_factory=list)
    current_education: str = ""
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def of(cls, student: db.OutstandingStudent) -> "OutstandingStudent":
        return cls(
            id=student.id,
            course_id=student.course_id,
            name=student.name,
            image_key=student.image_key,
            awards=student.awards,
            current_education=student.current_education,
            is_active=student.is_active,
            created_at=student.created_at,
            updated_at=student.updated_at
        )

    @property
    def awards_display(self) -> str:
        """Display awards as string"""
        return ", ".join(self.awards) if self.awards else ""


@dataclass
class CourseAdditionalInfo:
    id: str
    course_id: str
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    content_blocks: List["CourseAdditionalContentBlock"] = field(default_factory=list)

    @classmethod
    def of(cls, info: db.CourseAdditionalInfo) -> "CourseAdditionalInfo":
        return cls(
            id=info.id,
            course_id=info.course_id,
            is_active=info.is_active,
            created_at=info.created_at,
            updated_at=info.updated_at,
            content_blocks=[CourseAdditionalContentBlock.of(b) for b in info.content_blocks] if info.content_blocks else []
        )

    def get_active_content_blocks(self) -> List["CourseAdditionalContentBlock"]:
        """Get active content blocks ordered"""
        return [block for block in self.content_blocks if block.is_active]


@dataclass
class CourseAdditionalContentBlock:
    id: str
    additional_info_id: str
    title: Optional[str] = None
    image_key: Optional[str] = None
    descriptions: List[str] = field(default_factory=list)
    general_description: Optional[str] = None
    order: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def of(cls, block: db.CourseAdditionalContentBlock) -> "CourseAdditionalContentBlock":
        return cls(
            id=block.id,
            additional_info_id=block.additional_info_id,
            title=block.title,
            image_key=block.image_key,
            descriptions=block.descriptions,
            general_description=block.general_description,
            order=block.order,
            is_active=block.is_active,
            created_at=block.created_at,
            updated_at=block.updated_at
        )


@dataclass
class CourseFile:
    """Course file with display methods"""
    id: str
    course_id: str
    name: str
    description: Optional[str] = None
    file_key: str = ""
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    is_downloadable: bool = True
    permission_level: str = "public"
    download_count: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def of(cls, file: db.CourseFile) -> "CourseFile":
        """Create composite CourseFile from database CourseFile"""
        return cls(
            id=file.id,
            course_id=file.course_id,
            name=file.name,
            description=file.description,
            file_key=file.file_key,
            file_size=file.file_size,
            file_type=file.file_type,
            is_downloadable=file.is_downloadable,
            permission_level=file.permission_level,
            download_count=file.download_count,
            is_active=file.is_active,
            created_at=file.created_at,
            updated_at=file.updated_at
        )

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
        """Check if user can download this file"""
        if not self.is_downloadable or not self.is_active:
            return False
        
        if self.permission_level == "public":
            return True
        elif self.permission_level == "enrolled":
            if not user:
                return False
            
            return any(
                enrollment.course_id == self.course_id and enrollment.status in [
                    "pending", "enrolled", "studying", "completed"
                ]
                for enrollment in user.enrollments
            )
        elif self.permission_level == "admin":
            return user is not None and (user.is_staff or user.is_superuser)
        
        return False


@dataclass
class CourseClass:
    """Course class with enrollment management"""
    id: str
    course_id: str
    title: str
    short_description: str
    image_key: Optional[str] = None
    address: str = ""
    schedule_description: str = ""
    learning_method: str = "offline"
    class_code: str = ""
    is_open_for_enrollment: bool = True
    max_students: int = 30
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    content_blocks: List[CourseContentBlock] = field(default_factory=list)
    enrollments: List[StudentEnrollment] = field(default_factory=list)

    @classmethod
    def of(cls, course_class: db.CourseClass) -> "CourseClass":
        """Create composite CourseClass from database CourseClass"""
        return cls(
            id=course_class.id,
            course_id=course_class.course_id,
            title=course_class.title,
            short_description=course_class.short_description,
            image_key=course_class.image_key,
            address=course_class.address,
            schedule_description=course_class.schedule_description,
            learning_method=course_class.learning_method.value if course_class.learning_method else "offline",
            class_code=course_class.class_code,
            is_open_for_enrollment=course_class.is_open_for_enrollment,
            max_students=course_class.max_students,
            is_active=course_class.is_active,
            created_at=course_class.created_at,
            updated_at=course_class.updated_at,
            content_blocks=[CourseContentBlock.of(b) for b in course_class.content_blocks] if course_class.content_blocks else [],
            enrollments=[StudentEnrollment.of(e) for e in course_class.enrollments] if course_class.enrollments else []
        )

    @property
    def current_students_count(self) -> int:
        """Current number of enrolled students"""
        return len([
            enrollment for enrollment in self.enrollments
            if enrollment.status in [
                db.EnrollmentStatusEnum.PENDING.value, 
                db.EnrollmentStatusEnum.ENROLLED.value, 
                db.EnrollmentStatusEnum.STUDYING.value
            ]
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


@dataclass
class Course:
    """Course entity with business logic"""
    id: str
    category_id: str
    title: str
    slug: str
    short_description: str
    image_key: Optional[str] = None
    order: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    category: Optional["CourseCategory"] = None
    classes: List[CourseClass] = field(default_factory=list)
    files: List[CourseFile] = field(default_factory=list)
    outstanding_students: List[OutstandingStudent] = field(default_factory=list)
    roadmap: Optional[CourseRoadmap] = None
    additional_info: Optional[CourseAdditionalInfo] = None

    @classmethod
    def of(cls, course: db.Course) -> "Course":
        """Create composite Course from database Course"""
        return cls(
            id=course.id,
            category_id=course.category_id,
            title=course.title,
            slug=course.slug,
            short_description=course.short_description,
            image_key=course.image_key,
            order=course.order,
            is_active=course.is_active,
            created_at=course.created_at,
            updated_at=course.updated_at,
            category=CourseCategory.of(course.category) if course.category else None,
            classes=[CourseClass.of(c) for c in course.classes] if course.classes else [],
            files=[CourseFile.of(f) for f in course.files] if course.files else [],
            outstanding_students=[OutstandingStudent.of(s) for s in course.outstanding_students] if course.outstanding_students else [],
            roadmap=CourseRoadmap.of(course.roadmap) if course.roadmap else None,
            additional_info=CourseAdditionalInfo.of(course.additional_info) if course.additional_info else None
        )

    def get_total_classes_count(self) -> int:
        """Get total number of classes"""
        return len([cls for cls in self.classes if cls.is_active])

    def get_total_files_count(self) -> int:
        """Get total number of files"""
        return len([file for file in self.files if file.is_active])

    def get_featured_outstanding_students(self) -> List[OutstandingStudent]:
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


@dataclass
class CourseCategory:
    """Course category with enhanced functionality"""
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    order: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    courses: List[Course] = field(default_factory=list)

    @classmethod
    def of(cls, category: db.CourseCategory) -> "CourseCategory":
        """Create composite CourseCategory from database CourseCategory"""
        return cls(
            id=category.id,
            name=category.name,
            slug=category.slug,
            description=category.description,
            order=category.order,
            is_active=category.is_active,
            created_at=category.created_at,
            updated_at=category.updated_at,
            courses=[Course.of(c) for c in category.courses] if category.courses else []
        )

    def get_active_courses_count(self) -> int:
        """Count active courses in this category"""
        return len([course for course in self.courses if course.is_active])


# ================================================================
# News Entities
# ================================================================

@dataclass
class NewsCategory:
    """News category with enhanced functionality"""
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    category_type: str = "general"
    course_id: Optional[str] = None
    order: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    course: Optional[Course] = None
    news: List["News"] = field(default_factory=list)

    @classmethod
    def of(cls, category: db.NewsCategory) -> "NewsCategory":
        """Create composite NewsCategory from database NewsCategory"""
        return cls(
            id=category.id,
            name=category.name,
            slug=category.slug,
            description=category.description,
            category_type=category.category_type.value if category.category_type else "general",
            course_id=category.course_id,
            order=category.order,
            is_active=category.is_active,
            created_at=category.created_at,
            updated_at=category.updated_at,
            course=Course.of(category.course) if category.course else None,
            news=[News.of(n) for n in category.news] if category.news else []
        )

    def get_published_news_count(self) -> int:
        """Count published news in this category"""
        return len([news for news in self.news if news.is_published and news.is_active])

    @property
    def category_type_display(self) -> str:
        """Human readable category type"""
        type_map = {
            "exam_results": 'Kết quả thi',
            "upcoming_events": 'Sắp diễn ra',
            "general": 'Tổng hợp'
        }
        return type_map.get(self.category_type, self.category_type)


@dataclass
class News:
    """News entity with business logic"""
    id: str
    category_id: str
    title: str
    slug: str
    short_description: str
    image_key: Optional[str] = None
    is_published: bool = False
    is_featured: bool = False
    view_count: int = 0
    published_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: bool = True
    category: Optional[NewsCategory] = None
    content_blocks: List["NewsContentBlock"] = field(default_factory=list)

    @classmethod
    def of(cls, news: db.News) -> "News":
        """Create composite News from database News"""
        return cls(
            id=news.id,
            category_id=news.category_id,
            title=news.title,
            slug=news.slug,
            short_description=news.short_description,
            image_key=news.image_key,
            is_published=news.is_published,
            is_featured=False,
            view_count=news.view_count,
            published_at=news.published_at,
            created_at=news.created_at,
            updated_at=news.updated_at,
            is_active=news.is_active,
            category=NewsCategory.of(news.category) if news.category else None,
            content_blocks=[NewsContentBlock.of(b) for b in news.content_blocks] if news.content_blocks else []
        )

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
        from datetime import timedelta
        return self.published_at >= datetime.now() - timedelta(days=7)


@dataclass
class NewsContentBlock:
    """News content block"""
    id: str
    news_id: str
    title: Optional[str] = None
    image_key: Optional[str] = None
    descriptions: List[str] = field(default_factory=list)
    general_description: Optional[str] = None
    order: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    news: Optional[News] = None

    @classmethod
    def of(cls, block: db.NewsContentBlock) -> "NewsContentBlock":
        """Create composite NewsContentBlock from database NewsContentBlock"""
        return cls(
            id=block.id,
            news_id=block.news_id,
            title=block.title,
            image_key=block.image_key,
            descriptions=block.descriptions,
            general_description=block.general_description,
            order=block.order,
            is_active=block.is_active,
            created_at=block.created_at,
            updated_at=block.updated_at,
            news=News.of(block.news) if block.news else None
        )


# ================================================================
# Website Settings & Configuration Entities
# ================================================================

@dataclass
class SiteSettings:
    """Site settings with enhanced functionality"""
    id: str
    key: str
    value: str
    data_type: str = "text"
    description: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def of(cls, settings: db.SiteSettings) -> "SiteSettings":
        """Create composite SiteSettings from database SiteSettings"""
        return cls(
            id=settings.id,
            key=settings.key,
            value=settings.value,
            data_type=settings.data_type,
            description=settings.description,
            is_active=settings.is_active,
            created_at=settings.created_at,
            updated_at=settings.updated_at
        )

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


@dataclass
class ContactInfo:
    """Contact information"""
    id: str
    address: str
    phone: str
    email: str
    maps_url: Optional[str] = None
    facebook_url: Optional[str] = None
    working_hours: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def of(cls, contact: db.ContactInfo) -> "ContactInfo":
        """Create composite ContactInfo from database ContactInfo"""
        return cls(
            id=contact.id,
            address=contact.address,
            phone=contact.phone,
            email=contact.email,
            maps_url=contact.maps_url,
            facebook_url=contact.facebook_url,
            working_hours=contact.working_hours,
            is_active=contact.is_active,
            created_at=contact.created_at,
            updated_at=contact.updated_at
        )


@dataclass
class FAQ:
    """FAQ with enhanced functionality"""
    id: str
    question: str
    answer: str
    category_id: Optional[str] = None
    order: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    category: Optional[CourseCategory] = None

    @classmethod
    def of(cls, faq: db.FAQ) -> "FAQ":
        """Create composite FAQ from database FAQ"""
        return cls(
            id=faq.id,
            question=faq.question,
            answer=faq.answer,
            category_id=faq.category_id,
            order=faq.order,
            is_active=faq.is_active,
            created_at=faq.created_at,
            updated_at=faq.updated_at,
            category=CourseCategory.of(faq.category) if faq.category else None
        )


@dataclass
class Banner:
    """Banner with enhanced functionality"""
    id: str
    title: str
    description: Optional[str] = None
    image: str = ""
    link: Optional[str] = None
    position: str = "hero"
    order: int = 0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def of(cls, banner: db.Banner) -> "Banner":
        """Create composite Banner from database Banner"""
        return cls(
            id=banner.id,
            title=banner.title,
            description=banner.description,
            image=banner.image,
            link=banner.link,
            position=banner.position,
            order=banner.order,
            start_date=banner.start_date,
            end_date=banner.end_date,
            is_active=banner.is_active,
            created_at=banner.created_at,
            updated_at=banner.updated_at
        )

    def is_active_now(self) -> bool:
        """Check if banner is currently active"""
        now = datetime.now()
        
        if not self.is_active:
            return False
            
        if self.start_date and now < self.start_date:
            return False
            
        if self.end_date and now > self.end_date:
            return False
            
        return True


@dataclass
class ContactInquiry:
    """Contact inquiry with enhanced functionality"""
    id: str
    full_name: str
    phone: str
    email: Optional[str] = None
    inquiry_type: str = "course_inquiry"
    course_id: Optional[str] = None
    course_class_id: Optional[str] = None
    message: Optional[str] = None
    status: str = "new"
    notes: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    course: Optional[Course] = None
    course_class: Optional[CourseClass] = None

    @classmethod
    def of(cls, inquiry: db.ContactInquiry) -> "ContactInquiry":
        """Create composite ContactInquiry from database ContactInquiry"""
        return cls(
            id=inquiry.id,
            full_name=inquiry.full_name,
            phone=inquiry.phone,
            email=inquiry.email,
            inquiry_type=inquiry.inquiry_type,
            course_id=inquiry.course_id,
            course_class_id=inquiry.course_class_id,
            message=inquiry.message,
            status=inquiry.status,
            notes=inquiry.notes,
            is_active=inquiry.is_active,
            created_at=inquiry.created_at,
            updated_at=inquiry.updated_at,
            course=Course.of(inquiry.course) if inquiry.course else None,
            course_class=CourseClass.of(inquiry.course_class) if inquiry.course_class else None
        )

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


@dataclass
class Student:
    """Student profile for officially enrolled students"""
    id: str
    user_id: str
    name: str
    date_of_birth: Optional[date] = None
    student_id: str = ""
    phone: str = ""
    address: str = ""
    parent_name: str = ""
    parent_phone: str = ""
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def of(cls, student: db.Student) -> "Student":
        return cls(
            id=student.id,
            user_id=student.user_id,
            name=student.name,
            date_of_birth=student.date_of_birth,
            student_id=student.student_id,
            phone=student.phone,
            address=student.address,
            parent_name=student.parent_name,
            parent_phone=student.parent_phone,
            is_active=student.is_active,
            created_at=student.created_at,
            updated_at=student.updated_at
        )


@dataclass
class StudentInquiry:
    """Student inquiry for consultation requests"""
    id: str
    student_name: str
    student_age: int
    contact_name: str
    email: str
    phone: str
    message: Optional[str] = None
    status: str = "new"
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def of(cls, inquiry: db.StudentInquiry) -> "StudentInquiry":
        return cls(
            id=inquiry.id,
            student_name=inquiry.student_name,
            student_age=inquiry.student_age,
            contact_name=inquiry.contact_name,
            email=inquiry.email,
            phone=inquiry.phone,
            message=inquiry.message,
            status=inquiry.status,
            is_active=inquiry.is_active,
            created_at=inquiry.created_at,
            updated_at=inquiry.updated_at
        )

    @property
    def status_display(self) -> str:
        """Human readable status"""
        status_map = {
            "new": "Mới",
            "contacted": "Đã liên hệ", 
            "converted": "Đã chuyển đổi thành học sinh"
        }
        return status_map.get(self.status, self.status)