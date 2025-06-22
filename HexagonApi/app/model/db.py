import enum
from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal

from sqlalchemy import Enum, ForeignKey, UniqueConstraint, Text, String, Integer, Boolean, DECIMAL, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime, Date
import uuid


class Base(DeclarativeBase):
    pass


# ================================================================
# ENUMS
# ================================================================

class LearningMethodEnum(str, enum.Enum):
    OFFLINE = "offline"
    ONLINE = "online"


class EnrollmentStatusEnum(str, enum.Enum):
    PENDING = "pending"
    ENROLLED = "enrolled"
    STUDYING = "studying"
    COMPLETED = "completed"
    DROPPED = "dropped"


class PaymentStatusEnum(str, enum.Enum):
    UNPAID = "unpaid"
    PARTIAL = "partial"
    PAID = "paid"


class EnrollmentMethodEnum(str, enum.Enum):
    ADMIN = "admin"
    CLASS_CODE = "class_code"
    ONLINE_FORM = "online_form"


# ================================================================
# USER & AUTHENTICATION
# ================================================================

class User(Base):
    __tablename__ = "user"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    username: Mapped[str] = mapped_column(String(150), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(150))
    last_name: Mapped[Optional[str]] = mapped_column(String(150))
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    password: Mapped[Optional[str]] = mapped_column(String(128))
    phone_number: Mapped[Optional[str]] = mapped_column(String(17))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_staff: Mapped[bool] = mapped_column(Boolean, default=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    date_joined: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    firebase_id: Mapped[Optional[str]] = mapped_column(String(255))
    login_method: Mapped[Optional[str]] = mapped_column(String(50))

    # Relationships
    profile: Mapped[Optional["UserProfile"]] = relationship("UserProfile", back_populates="user", uselist=False)
    student_profile: Mapped[Optional["Student"]] = relationship("Student", back_populates="user", uselist=False)
    enrollments: Mapped[List["StudentCourseEnrollment"]] = relationship("StudentCourseEnrollment", back_populates="user")


class UserProfile(Base):
    __tablename__ = "user_profile"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("user.id"), unique=True)
    bio: Mapped[Optional[str]] = mapped_column(Text)
    address: Mapped[Optional[str]] = mapped_column(String(255))
    profile_picture: Mapped[Optional[str]] = mapped_column(String(255))

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="profile")


# ================================================================
# COURSE SYSTEM
# ================================================================

class CourseCategory(Base):
    __tablename__ = "course_category"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100))
    slug: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationships
    courses: Mapped[List["Course"]] = relationship("Course", back_populates="category")


class Course(Base):
    __tablename__ = "course"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    category_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("course_category.id"))
    title: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(255), unique=True)
    short_description: Mapped[str] = mapped_column(Text)
    image_key: Mapped[Optional[str]] = mapped_column(String(255))
    order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationships
    category: Mapped["CourseCategory"] = relationship("CourseCategory", back_populates="courses")
    classes: Mapped[List["CourseClass"]] = relationship("CourseClass", back_populates="course")
    files: Mapped[List["CourseFile"]] = relationship("CourseFile", back_populates="course")
    roadmap: Mapped[Optional["CourseRoadmap"]] = relationship("CourseRoadmap", back_populates="course", uselist=False)
    outstanding_students: Mapped[List["OutstandingStudent"]] = relationship("OutstandingStudent", back_populates="course")
    additional_info: Mapped[Optional["CourseAdditionalInfo"]] = relationship("CourseAdditionalInfo", back_populates="course", uselist=False)


class CourseClass(Base):
    __tablename__ = "course_class"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("course.id"))
    title: Mapped[str] = mapped_column(String(200))
    short_description: Mapped[str] = mapped_column(Text)
    image_key: Mapped[Optional[str]] = mapped_column(String(255))
    address: Mapped[str] = mapped_column(Text)
    schedule_description: Mapped[str] = mapped_column(Text)
    learning_method: Mapped[LearningMethodEnum] = mapped_column(Enum(LearningMethodEnum), default=LearningMethodEnum.OFFLINE)
    class_code: Mapped[str] = mapped_column(String(20), unique=True)
    is_open_for_enrollment: Mapped[bool] = mapped_column(Boolean, default=True)
    max_students: Mapped[int] = mapped_column(Integer, default=30)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationships
    course: Mapped["Course"] = relationship("Course", back_populates="classes")
    content_blocks: Mapped[List["CourseContentBlock"]] = relationship("CourseContentBlock", back_populates="course_class")
    enrollments: Mapped[List["StudentCourseEnrollment"]] = relationship("StudentCourseEnrollment", back_populates="course_class")


class CourseContentBlock(Base):
    __tablename__ = "course_content_block"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_class_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("course_class.id"))
    title: Mapped[Optional[str]] = mapped_column(String(200))
    image_key: Mapped[Optional[str]] = mapped_column(String(255))
    descriptions: Mapped[List[str]] = mapped_column(JSON, default=list)
    order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationships
    course_class: Mapped["CourseClass"] = relationship("CourseClass", back_populates="content_blocks")


class CourseFile(Base):
    __tablename__ = "course_file"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("course.id"))
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)
    file_key: Mapped[str] = mapped_column(String(255))
    file_size: Mapped[Optional[int]] = mapped_column(Integer)  # File size in bytes
    file_type: Mapped[Optional[str]] = mapped_column(String(50))  # pdf, doc, ppt, etc.
    is_downloadable: Mapped[bool] = mapped_column(Boolean, default=True)
    permission_level: Mapped[str] = mapped_column(String(20), default="public")  # public, enrolled, admin
    download_count: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationships
    course: Mapped["Course"] = relationship("Course", back_populates="files")


class CourseRoadmap(Base):
    __tablename__ = "course_roadmap"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("course.id"))
    short_description: Mapped[str] = mapped_column(Text)
    image_key: Mapped[Optional[str]] = mapped_column(String(255))
    slogan: Mapped[str] = mapped_column(String(200))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationships
    course: Mapped["Course"] = relationship("Course", back_populates="roadmap")
    content_blocks: Mapped[List["RoadmapContentBlock"]] = relationship("RoadmapContentBlock", back_populates="roadmap")


class RoadmapContentBlock(Base):
    __tablename__ = "roadmap_content_block"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    roadmap_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("course_roadmap.id"))
    title: Mapped[Optional[str]] = mapped_column(String(200))
    image_key: Mapped[Optional[str]] = mapped_column(String(255))
    descriptions: Mapped[List[str]] = mapped_column(JSON, default=list)
    general_description: Mapped[Optional[str]] = mapped_column(Text)
    order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationships
    roadmap: Mapped["CourseRoadmap"] = relationship("CourseRoadmap", back_populates="content_blocks")


class OutstandingStudent(Base):
    __tablename__ = "outstanding_student"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("course.id"))
    name: Mapped[str] = mapped_column(String(200))
    image_key: Mapped[Optional[str]] = mapped_column(String(255))
    awards: Mapped[List[str]] = mapped_column(JSON, default=list)
    current_education: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationships
    course: Mapped["Course"] = relationship("Course", back_populates="outstanding_students")


class CourseAdditionalInfo(Base):
    __tablename__ = "course_additional_info"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("course.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationships
    course: Mapped["Course"] = relationship("Course", back_populates="additional_info")
    content_blocks: Mapped[List["CourseAdditionalContentBlock"]] = relationship("CourseAdditionalContentBlock", back_populates="additional_info")


class CourseAdditionalContentBlock(Base):
    __tablename__ = "course_additional_content_block"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    additional_info_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("course_additional_info.id"))
    title: Mapped[Optional[str]] = mapped_column(String(200))
    image_key: Mapped[Optional[str]] = mapped_column(String(255))
    descriptions: Mapped[List[str]] = mapped_column(JSON, default=list)
    general_description: Mapped[Optional[str]] = mapped_column(Text)
    order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationships
    additional_info: Mapped["CourseAdditionalInfo"] = relationship("CourseAdditionalInfo", back_populates="content_blocks")


# ================================================================
# ENROLLMENT SYSTEM
# ================================================================

class Student(Base):
    __tablename__ = "student"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("user.id"), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    date_of_birth: Mapped[date] = mapped_column(Date)
    student_id: Mapped[str] = mapped_column(String(20), unique=True)
    phone: Mapped[str] = mapped_column(String(20))
    address: Mapped[str] = mapped_column(Text)
    parent_name: Mapped[str] = mapped_column(String(200))
    parent_phone: Mapped[str] = mapped_column(String(20))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="student_profile")


class StudentCourseEnrollment(Base):
    __tablename__ = "student_course_enrollment"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("user.id"))
    course_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("course.id"))
    course_class_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("course_class.id"))

    enrollment_date: Mapped[date] = mapped_column(Date)
    enrollment_method: Mapped[EnrollmentMethodEnum] = mapped_column(Enum(EnrollmentMethodEnum), default=EnrollmentMethodEnum.ADMIN)
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date)

    status: Mapped[EnrollmentStatusEnum] = mapped_column(Enum(EnrollmentStatusEnum), default=EnrollmentStatusEnum.PENDING)

    tuition_fee: Mapped[Decimal] = mapped_column(DECIMAL(10, 0))
    paid_amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 0), default=0)
    payment_status: Mapped[PaymentStatusEnum] = mapped_column(Enum(PaymentStatusEnum), default=PaymentStatusEnum.UNPAID)

    final_grade: Mapped[Optional[str]] = mapped_column(String(5))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="enrollments")
    course: Mapped["Course"] = relationship("Course")
    course_class: Mapped["CourseClass"] = relationship("CourseClass", back_populates="enrollments")

    __table_args__ = (UniqueConstraint('user_id', 'course_class_id'),)


class StudentInquiry(Base):
    __tablename__ = "student_inquiry"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_name: Mapped[str] = mapped_column(String(200))
    student_age: Mapped[int] = mapped_column(Integer)
    contact_name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(20))
    message: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="new")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Note: interested_courses is ManyToMany in Django, handle separately if needed


# ================================================================
# NEWS SYSTEM
# ================================================================

class NewsCategoryTypeEnum(str, enum.Enum):
    EXAM_RESULTS = "exam_results"
    UPCOMING_EVENTS = "upcoming_events"
    GENERAL = "general"


class NewsCategory(Base):
    __tablename__ = "news_category"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100))
    slug: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    course_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), ForeignKey("course.id"))
    category_type: Mapped[NewsCategoryTypeEnum] = mapped_column(Enum(NewsCategoryTypeEnum), default=NewsCategoryTypeEnum.GENERAL)
    order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationships
    course: Mapped[Optional["Course"]] = relationship("Course")
    news: Mapped[List["News"]] = relationship("News", back_populates="category")


class News(Base):
    __tablename__ = "news"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    category_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("news_category.id"))
    title: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(255), unique=True)
    short_description: Mapped[str] = mapped_column(Text)
    image_key: Mapped[Optional[str]] = mapped_column(String(255))
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationships
    category: Mapped["NewsCategory"] = relationship("NewsCategory", back_populates="news")
    content_blocks: Mapped[List["NewsContentBlock"]] = relationship("NewsContentBlock", back_populates="news")


class NewsContentBlock(Base):
    __tablename__ = "news_content_block"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    news_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("news.id"))
    title: Mapped[Optional[str]] = mapped_column(String(200))
    image_key: Mapped[Optional[str]] = mapped_column(String(255))
    descriptions: Mapped[List[str]] = mapped_column(JSON, default=list)
    general_description: Mapped[Optional[str]] = mapped_column(Text)
    order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationships
    news: Mapped["News"] = relationship("News", back_populates="content_blocks")


# ================================================================
# WEBSITE SETTINGS & CONFIGURATION
# ================================================================

class SiteSettings(Base):
    __tablename__ = "site_settings"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    key: Mapped[str] = mapped_column(String(100), unique=True)
    value: Mapped[str] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)
    data_type: Mapped[str] = mapped_column(String(20), default="text")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ContactInfo(Base):
    __tablename__ = "contact_info"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    address: Mapped[str] = mapped_column(Text)
    phone: Mapped[str] = mapped_column(String(20))
    email: Mapped[str] = mapped_column(String(255))
    maps_url: Mapped[Optional[str]] = mapped_column(String(500))
    facebook_url: Mapped[Optional[str]] = mapped_column(String(500))
    working_hours: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class FAQ(Base):
    __tablename__ = "faq"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    category_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), ForeignKey("course_category.id"))
    order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationships
    category: Mapped[Optional["CourseCategory"]] = relationship("CourseCategory")


class Banner(Base):
    __tablename__ = "banner"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)
    image: Mapped[str] = mapped_column(String(255))
    link: Mapped[Optional[str]] = mapped_column(String(500))
    position: Mapped[str] = mapped_column(String(50), default="hero")
    order: Mapped[int] = mapped_column(Integer, default=0)
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ContactInquiry(Base):
    __tablename__ = "contact_inquiry"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(20))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    course_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), ForeignKey("course.id"))
    course_class_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), ForeignKey("course_class.id"))
    message: Mapped[Optional[str]] = mapped_column(Text)
    inquiry_type: Mapped[str] = mapped_column(String(50), default="course_inquiry")
    status: Mapped[str] = mapped_column(String(20), default="new")
    notes: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationships
    course: Mapped[Optional["Course"]] = relationship("Course")
    course_class: Mapped[Optional["CourseClass"]] = relationship("CourseClass")
