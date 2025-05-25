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


# ================================================================
# ENUMS
# ================================================================

class LearningMethodEnum(str, enum.Enum):
    OFFLINE = "offline"
    ONLINE = "online"
    HYBRID = "hybrid"


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


class FileTypeEnum(str, enum.Enum):
    PDF = "PDF"
    DOC = "DOC"
    VIDEO = "VIDEO"
    AUDIO = "AUDIO"
    IMAGE = "IMAGE"
    OTHER = "OTHER"


class NewsCategoryTypeEnum(str, enum.Enum):
    EXAM_RESULTS = "exam_results"
    UPCOMING_EVENTS = "upcoming_events"
    GENERAL = "general"


class EnrollmentMethodEnum(str, enum.Enum):
    ADMIN = "admin"
    CLASS_CODE = "class_code"
    ONLINE_FORM = "online_form"


# ================================================================
# USER & AUTHENTICATION
# ================================================================

class Account(Base):
    __tablename__ = "account"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    login_id: Mapped[str] = mapped_column(String(255), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(255))
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    modified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class Student(Base):
    __tablename__ = "student"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("account.id"), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    student_id: Mapped[str] = mapped_column(String(20), unique=True)
    date_of_birth: Mapped[date] = mapped_column(Date)
    phone: Mapped[str] = mapped_column(String(20))
    address: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationships
    account: Mapped["Account"] = relationship("Account")
    enrollments: Mapped[List["StudentCourseEnrollment"]] = relationship("StudentCourseEnrollment",
                                                                        back_populates="student")


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
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationships
    category: Mapped["CourseCategory"] = relationship("CourseCategory", back_populates="courses")
    classes: Mapped[List["CourseClass"]] = relationship("CourseClass", back_populates="course")
    files: Mapped[List["CourseFile"]] = relationship("CourseFile", back_populates="course")
    roadmap: Mapped[Optional["CourseRoadmap"]] = relationship("CourseRoadmap", back_populates="course", uselist=False)
    outstanding_students: Mapped[List["OutstandingStudent"]] = relationship("OutstandingStudent",
                                                                            back_populates="course")
    additional_info: Mapped[Optional["CourseAdditionalInfo"]] = relationship("CourseAdditionalInfo",
                                                                             back_populates="course", uselist=False)


class CourseClass(Base):
    __tablename__ = "course_class"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("course.id"))
    title: Mapped[str] = mapped_column(String(200))
    short_description: Mapped[str] = mapped_column(Text)
    image_key: Mapped[Optional[str]] = mapped_column(String(255))
    address: Mapped[str] = mapped_column(Text)
    schedule_description: Mapped[str] = mapped_column(Text)
    learning_method: Mapped[LearningMethodEnum] = mapped_column(Enum(LearningMethodEnum),
                                                                default=LearningMethodEnum.OFFLINE)
    class_code: Mapped[str] = mapped_column(String(20), unique=True)
    is_open_for_enrollment: Mapped[bool] = mapped_column(Boolean, default=True)
    max_students: Mapped[int] = mapped_column(Integer, default=30)
    order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationships
    course: Mapped["Course"] = relationship("Course", back_populates="classes")
    content_blocks: Mapped[List["CourseContentBlock"]] = relationship("CourseContentBlock",
                                                                      back_populates="course_class")
    enrollments: Mapped[List["StudentCourseEnrollment"]] = relationship("StudentCourseEnrollment",
                                                                        back_populates="course_class")


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
    file_type: Mapped[FileTypeEnum] = mapped_column(Enum(FileTypeEnum), default=FileTypeEnum.PDF)
    file_size: Mapped[Optional[int]] = mapped_column(Integer)
    download_count: Mapped[int] = mapped_column(Integer, default=0)
    order: Mapped[int] = mapped_column(Integer, default=0)
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
    testimonial: Mapped[Optional[str]] = mapped_column(Text)
    order: Mapped[int] = mapped_column(Integer, default=0)
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
    content_blocks: Mapped[List["CourseAdditionalContentBlock"]] = relationship("CourseAdditionalContentBlock",
                                                                                back_populates="additional_info")


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
    additional_info: Mapped["CourseAdditionalInfo"] = relationship("CourseAdditionalInfo",
                                                                   back_populates="content_blocks")


# ================================================================
# ENROLLMENT SYSTEM
# ================================================================

class StudentCourseEnrollment(Base):
    __tablename__ = "student_course_enrollment"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("student.id"))
    course_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("course.id"))
    course_class_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("course_class.id"))

    enrollment_date: Mapped[date] = mapped_column(Date)
    enrollment_method: Mapped[EnrollmentMethodEnum] = mapped_column(Enum(EnrollmentMethodEnum),
                                                                    default=EnrollmentMethodEnum.ADMIN)
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date)

    status: Mapped[EnrollmentStatusEnum] = mapped_column(Enum(EnrollmentStatusEnum),
                                                         default=EnrollmentStatusEnum.ENROLLED)

    tuition_fee: Mapped[Decimal] = mapped_column(DECIMAL(10, 0))
    paid_amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 0), default=0)
    payment_status: Mapped[PaymentStatusEnum] = mapped_column(Enum(PaymentStatusEnum), default=PaymentStatusEnum.UNPAID)

    final_grade: Mapped[Optional[str]] = mapped_column(String(5))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationships
    student: Mapped["Student"] = relationship("Student", back_populates="enrollments")
    course: Mapped["Course"] = relationship("Course")
    course_class: Mapped["CourseClass"] = relationship("CourseClass", back_populates="enrollments")

    __table_args__ = (UniqueConstraint('student_id', 'course_class_id'),)


# ================================================================
# GENERAL CONTENT SYSTEM
# ================================================================

class GeneralRoadmap(Base):
    __tablename__ = "general_roadmap"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(200))
    short_description: Mapped[str] = mapped_column(Text)
    image_key: Mapped[Optional[str]] = mapped_column(String(255))
    order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationships
    content_blocks: Mapped[List["GeneralRoadmapContentBlock"]] = relationship("GeneralRoadmapContentBlock",
                                                                              back_populates="roadmap")


class GeneralRoadmapContentBlock(Base):
    __tablename__ = "general_roadmap_content_block"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    roadmap_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("general_roadmap.id"))
    title: Mapped[Optional[str]] = mapped_column(String(200))
    image_key: Mapped[Optional[str]] = mapped_column(String(255))
    descriptions: Mapped[List[str]] = mapped_column(JSON, default=list)
    general_description: Mapped[Optional[str]] = mapped_column(Text)
    order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationships
    roadmap: Mapped["GeneralRoadmap"] = relationship("GeneralRoadmap", back_populates="content_blocks")


class AboutSection(Base):
    __tablename__ = "about_section"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(200))
    short_description: Mapped[str] = mapped_column(Text)
    image_key: Mapped[Optional[str]] = mapped_column(String(255))
    order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationships
    content_blocks: Mapped[List["AboutContentBlock"]] = relationship("AboutContentBlock",
                                                                     back_populates="about_section")


class AboutContentBlock(Base):
    __tablename__ = "about_section_content_block"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    about_section_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("about_section.id"))
    title: Mapped[Optional[str]] = mapped_column(String(200))
    image_key: Mapped[Optional[str]] = mapped_column(String(255))
    descriptions: Mapped[List[str]] = mapped_column(JSON, default=list)
    general_description: Mapped[Optional[str]] = mapped_column(Text)
    order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationships
    about_section: Mapped["AboutSection"] = relationship("AboutSection", back_populates="content_blocks")


# ================================================================
# NEWS SYSTEM
# ================================================================

class NewsCategory(Base):
    __tablename__ = "news_category"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100))
    slug: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    course_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), ForeignKey("course.id"))
    category_type: Mapped[NewsCategoryTypeEnum] = mapped_column(Enum(NewsCategoryTypeEnum),
                                                                default=NewsCategoryTypeEnum.GENERAL)
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
