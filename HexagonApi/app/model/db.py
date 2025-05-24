import enum
from datetime import datetime, date
from typing import Any, Optional, List
from decimal import Decimal

from sqlalchemy import Enum, ForeignKey, UniqueConstraint, Text, String, Integer, Boolean, DECIMAL, JSON
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime, Date
import uuid


class Base(DeclarativeBase):
    pass


# ----------------------------------------------------------------
# Enums
# ----------------------------------------------------------------
class FileTypeEnum(str, enum.Enum):
    PDF = "PDF"
    DOC = "DOC"
    VIDEO = "VIDEO"
    AUDIO = "AUDIO"
    IMAGE = "IMAGE"
    OTHER = "OTHER"


class AccessLevelEnum(str, enum.Enum):
    PUBLIC = "public"
    STUDENT = "student"
    PREMIUM = "premium"
    INTERNAL = "internal"


class InquiryStatusEnum(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    SCHEDULED = "scheduled"
    ENROLLED = "enrolled"
    DECLINED = "declined"


class EnrollmentStatusEnum(str, enum.Enum):
    ENROLLED = "enrolled"
    STUDYING = "studying"
    COMPLETED = "completed"
    DROPPED = "dropped"
    SUSPENDED = "suspended"


class PaymentStatusEnum(str, enum.Enum):
    UNPAID = "unpaid"
    PARTIAL = "partial"
    PAID = "paid"
    REFUNDED = "refunded"


class BannerPositionEnum(str, enum.Enum):
    HERO = "hero"
    SIDEBAR = "sidebar"
    FOOTER = "footer"
    POPUP = "popup"


# ----------------------------------------------------------------
# User & Profile
# ----------------------------------------------------------------
class User(Base):
    __tablename__ = "user"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    username: Mapped[str] = mapped_column(String(150), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    first_name: Mapped[str] = mapped_column(String(150))
    last_name: Mapped[str] = mapped_column(String(150))
    phone_number: Mapped[Optional[str]] = mapped_column(String(17))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    date_joined: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    firebase_id: Mapped[Optional[str]] = mapped_column(String(255))
    login_method: Mapped[Optional[str]] = mapped_column(String(50))

    # Relationship
    profile: Mapped[Optional["UserProfile"]] = relationship("UserProfile", back_populates="user", uselist=False)


class UserProfile(Base):
    __tablename__ = "user_profile"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("user.id"))
    bio: Mapped[Optional[str]] = mapped_column(Text)
    address: Mapped[Optional[str]] = mapped_column(String(255))
    profile_picture: Mapped[Optional[str]] = mapped_column(String(255))

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="profile")


# ----------------------------------------------------------------
# Course System
# ----------------------------------------------------------------
class Subject(Base):
    __tablename__ = "subject"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(255), unique=True)
    code: Mapped[str] = mapped_column(String(20), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    icon_class: Mapped[Optional[str]] = mapped_column(String(50))
    color: Mapped[str] = mapped_column(String(7), default="#2952bf")
    order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class CourseCategory(Base):
    __tablename__ = "course_category"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100))
    slug: Mapped[str] = mapped_column(String(255), unique=True)
    short_name: Mapped[str] = mapped_column(String(20))
    description: Mapped[str] = mapped_column(Text)
    subtitle: Mapped[Optional[str]] = mapped_column(Text)
    age_range_min: Mapped[int] = mapped_column(Integer)
    age_range_max: Mapped[int] = mapped_column(Integer)
    hero_image: Mapped[Optional[str]] = mapped_column(String(255))
    icon: Mapped[Optional[str]] = mapped_column(String(255))
    color: Mapped[str] = mapped_column(String(7), default="#2952bf")
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
    name: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[str] = mapped_column(Text)
    content: Mapped[Optional[str]] = mapped_column(Text)
    duration_months: Mapped[int] = mapped_column(Integer)
    hours_per_week: Mapped[str] = mapped_column(String(50))
    class_schedule: Mapped[Optional[dict]] = mapped_column(JSON)
    image: Mapped[Optional[str]] = mapped_column(String(255))
    price: Mapped[Decimal] = mapped_column(DECIMAL(10, 0), default=0)
    max_students: Mapped[int] = mapped_column(Integer, default=20)
    order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationships
    category: Mapped["CourseCategory"] = relationship("CourseCategory", back_populates="courses")
    course_subjects: Mapped[List["CourseSubject"]] = relationship("CourseSubject", back_populates="course")


class CourseSubject(Base):
    __tablename__ = "course_subject"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("course.id"))
    subject_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("subject.id"))
    lecture_hours: Mapped[int] = mapped_column(Integer, default=0)
    tutorial_hours: Mapped[int] = mapped_column(Integer, default=0)
    lab_hours: Mapped[int] = mapped_column(Integer, default=0)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationships
    course: Mapped["Course"] = relationship("Course", back_populates="course_subjects")
    subject: Mapped["Subject"] = relationship("Subject")

    __table_args__ = (UniqueConstraint('course_id', 'subject_id'),)


class Alumni(Base):
    __tablename__ = "alumni"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(200))
    photo: Mapped[Optional[str]] = mapped_column(String(255))
    academic_achievements: Mapped[Optional[List]] = mapped_column(JSON)
    exam_results: Mapped[Optional[dict]] = mapped_column(JSON)
    current_school: Mapped[Optional[str]] = mapped_column(String(200))
    university_admitted: Mapped[Optional[str]] = mapped_column(String(200))
    scholarship_received: Mapped[Optional[str]] = mapped_column(Text)
    testimonial: Mapped[Optional[str]] = mapped_column(Text)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(255))
    graduation_year: Mapped[Optional[int]] = mapped_column(Integer)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


# ----------------------------------------------------------------
# Materials
# ----------------------------------------------------------------
class MaterialCategory(Base):
    __tablename__ = "material_category"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    icon: Mapped[Optional[str]] = mapped_column(String(50))
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationships
    materials: Mapped[List["Material"]] = relationship("Material", back_populates="category")


class Material(Base):
    __tablename__ = "material"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)
    category_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("material_category.id"))
    course_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), ForeignKey("course.id"))
    subject_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), ForeignKey("subject.id"))

    # File information
    file_url: Mapped[str] = mapped_column(String(255))
    file_name: Mapped[str] = mapped_column(String(255))
    file_size: Mapped[Optional[int]] = mapped_column(Integer)
    file_type: Mapped[FileTypeEnum] = mapped_column(Enum(FileTypeEnum), default=FileTypeEnum.PDF)

    # Access control
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    is_free: Mapped[bool] = mapped_column(Boolean, default=True)
    access_level: Mapped[AccessLevelEnum] = mapped_column(Enum(AccessLevelEnum), default=AccessLevelEnum.PUBLIC)

    # Statistics
    download_count: Mapped[int] = mapped_column(Integer, default=0)
    view_count: Mapped[int] = mapped_column(Integer, default=0)

    uploaded_by_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), ForeignKey("user.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationships
    category: Mapped["MaterialCategory"] = relationship("MaterialCategory", back_populates="materials")
    course: Mapped[Optional["Course"]] = relationship("Course")
    subject: Mapped[Optional["Subject"]] = relationship("Subject")
    uploaded_by: Mapped[Optional["User"]] = relationship("User")


# ----------------------------------------------------------------
# News
# ----------------------------------------------------------------
class NewsCategory(Base):
    __tablename__ = "news_category"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100))
    slug: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    color: Mapped[str] = mapped_column(String(7), default="#2952bf")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationships
    news: Mapped[List["News"]] = relationship("News", back_populates="category")


class News(Base):
    __tablename__ = "news"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(255), unique=True)
    excerpt: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text)
    image: Mapped[Optional[str]] = mapped_column(String(255))
    author_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("user.id"))
    category_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), ForeignKey("news_category.id"))
    course_category_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), ForeignKey("course_category.id"))
    tags: Mapped[Optional[List]] = mapped_column(JSON)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationships
    author: Mapped["User"] = relationship("User")
    category: Mapped[Optional["NewsCategory"]] = relationship("NewsCategory", back_populates="news")
    course_category: Mapped[Optional["CourseCategory"]] = relationship("CourseCategory")


# ----------------------------------------------------------------
# Config & Settings
# ----------------------------------------------------------------
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
    maps_url: Mapped[Optional[str]] = mapped_column(String(255))
    facebook_url: Mapped[Optional[str]] = mapped_column(String(255))
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
    link: Mapped[Optional[str]] = mapped_column(String(255))
    position: Mapped[BannerPositionEnum] = mapped_column(Enum(BannerPositionEnum), default=BannerPositionEnum.HERO)
    order: Mapped[int] = mapped_column(Integer, default=0)
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


# ----------------------------------------------------------------
# Enrollment
# ----------------------------------------------------------------
class StudentInquiry(Base):
    __tablename__ = "student_inquiry"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Student info
    student_name: Mapped[str] = mapped_column(String(200))
    student_age: Mapped[int] = mapped_column(Integer)
    current_grade: Mapped[Optional[str]] = mapped_column(String(50))
    current_school: Mapped[Optional[str]] = mapped_column(String(200))

    # Contact info
    contact_name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(20))

    # Interest
    message: Mapped[Optional[str]] = mapped_column(Text)
    preferred_contact_time: Mapped[Optional[str]] = mapped_column(String(100))

    # Processing
    status: Mapped[InquiryStatusEnum] = mapped_column(Enum(InquiryStatusEnum), default=InquiryStatusEnum.NEW)
    is_contacted: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    assigned_to_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), ForeignKey("user.id"))
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationships
    assigned_to: Mapped[Optional["User"]] = relationship("User")


class CourseEnrollment(Base):
    __tablename__ = "course_enrollment"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Student info
    student_name: Mapped[str] = mapped_column(String(200))
    date_of_birth: Mapped[date] = mapped_column(Date)
    student_id: Mapped[str] = mapped_column(String(20), unique=True)
    current_school: Mapped[Optional[str]] = mapped_column(String(200))
    address: Mapped[str] = mapped_column(Text)

    # Course
    course_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("course.id"))
    enrollment_date: Mapped[date] = mapped_column(Date)
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date)

    # Status
    status: Mapped[EnrollmentStatusEnum] = mapped_column(Enum(EnrollmentStatusEnum), default=EnrollmentStatusEnum.ENROLLED)

    # Payment
    tuition_fee: Mapped[Decimal] = mapped_column(DECIMAL(10, 0))
    paid_amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 0), default=0)
    payment_status: Mapped[PaymentStatusEnum] = mapped_column(Enum(PaymentStatusEnum), default=PaymentStatusEnum.UNPAID)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationships
    course: Mapped["Course"] = relationship("Course")

