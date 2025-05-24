from datetime import date, datetime
from typing import List, Optional
from urllib.parse import urlparse
from decimal import Decimal

import app.model.composite as c
from app.api.shared.dependencies import URLFor
from app.config import environment
from app.ext.storage.s3 import S3Storage
from app.pdf.models import CareerData, ResumeData
from pydantic import ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic.dataclasses import dataclass
from typing_extensions import Self

s3_url = environment().settings.storage.url
if s3_url.startswith("s3://"):
    parsed_url = urlparse(s3_url)
    s3_storage = S3Storage(parsed_url)


# ----------------------------------------------------------------
# Settings
# ----------------------------------------------------------------
def to_lower_camel(name: str) -> str:
    return "".join(
        [n.capitalize() if i > 0 else n for i, n in enumerate(name.split("_"))]
    )


config = ConfigDict(
    alias_generator=to_camel,
    populate_by_name=True,
)


# ----------------------------------------------------------------
# Common responses.
# ----------------------------------------------------------------
@dataclass(config=config)
class Me:
    id: str = Field(description="Account ID.")
    created_at: datetime = Field(description="Registration date and time.")
    modified_at: datetime = Field(description="Update date and time.")

    @classmethod
    def of(cls, me: c.Me) -> Self:
        return Me(me.id, me.created_at, me.modified_at)


# ----------------------------------------------------------------
# User responses
# ----------------------------------------------------------------
@dataclass(config=config)
class UserProfile:
    id: str = Field(description="Profile ID")
    bio: Optional[str] = Field(description="User biography")
    address: Optional[str] = Field(description="User address")
    profile_picture: Optional[str] = Field(description="Profile picture URL")

    @classmethod
    def of(cls, profile: c.UserProfile) -> Self:
        return cls(
            id=profile.id,
            bio=profile.bio,
            address=profile.address,
            profile_picture=profile.profile_picture
        )


@dataclass(config=config)
class User:
    id: str = Field(description="User ID")
    username: str = Field(description="Username")
    email: str = Field(description="Email address")
    first_name: str = Field(description="First name")
    last_name: str = Field(description="Last name")
    full_name: str = Field(description="Full name")
    phone_number: Optional[str] = Field(description="Phone number")
    date_joined: datetime = Field(description="Registration date")
    last_login: Optional[datetime] = Field(description="Last login date")
    profile: Optional[UserProfile] = Field(description="User profile")

    @classmethod
    def of(cls, user: c.User) -> Self:
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=user.full_name,
            phone_number=user.phone_number,
            date_joined=user.date_joined,
            last_login=user.last_login,
            profile=UserProfile.of(user.profile) if user.profile else None
        )


# ----------------------------------------------------------------
# Course responses
# ----------------------------------------------------------------
@dataclass(config=config)
class Subject:
    id: str = Field(description="Subject ID")
    name: str = Field(description="Subject name")
    slug: str = Field(description="URL slug")
    code: str = Field(description="Subject code")
    description: Optional[str] = Field(description="Subject description")
    icon_class: Optional[str] = Field(description="Icon CSS class")
    color: str = Field(description="Subject color")
    order: int = Field(description="Display order")

    @classmethod
    def of(cls, subject: c.Subject) -> Self:
        return cls(
            id=subject.id,
            name=subject.name,
            slug=subject.slug,
            code=subject.code,
            description=subject.description,
            icon_class=subject.icon_class,
            color=subject.color,
            order=subject.order
        )


@dataclass(config=config)
class CourseCategory:
    id: str = Field(description="Category ID")
    name: str = Field(description="Category name")
    slug: str = Field(description="URL slug")
    short_name: str = Field(description="Short name")
    description: str = Field(description="Category description")
    subtitle: Optional[str] = Field(description="Category subtitle")
    age_range_min: int = Field(description="Minimum age")
    age_range_max: int = Field(description="Maximum age")
    age_range_display: str = Field(description="Age range display text")
    hero_image: Optional[str] = Field(description="Hero image URL")
    icon: Optional[str] = Field(description="Icon URL")
    color: str = Field(description="Category color")
    order: int = Field(description="Display order")

    @classmethod
    def of(cls, category: c.CourseCategory) -> Self:
        return cls(
            id=category.id,
            name=category.name,
            slug=category.slug,
            short_name=category.short_name,
            description=category.description,
            subtitle=category.subtitle,
            age_range_min=category.age_range_min,
            age_range_max=category.age_range_max,
            age_range_display=category.age_range_display,
            hero_image=category.hero_image,
            icon=category.icon,
            color=category.color,
            order=category.order
        )


@dataclass(config=config)
class CourseSubject:
    id: str = Field(description="Course-Subject ID")
    subject: Subject = Field(description="Subject details")
    lecture_hours: int = Field(description="Lecture hours")
    tutorial_hours: int = Field(description="Tutorial hours")
    lab_hours: int = Field(description="Lab hours")
    total_hours: int = Field(description="Total hours")
    is_required: bool = Field(description="Is required subject")

    @classmethod
    def of(cls, course_subject: c.CourseSubject) -> Self:
        return cls(
            id=course_subject.id,
            subject=Subject.of(course_subject.subject),
            lecture_hours=course_subject.lecture_hours,
            tutorial_hours=course_subject.tutorial_hours,
            lab_hours=course_subject.lab_hours,
            total_hours=course_subject.total_hours,
            is_required=course_subject.is_required
        )


@dataclass(config=config)
class Course:
    id: str = Field(description="Course ID")
    name: str = Field(description="Course name")
    slug: str = Field(description="URL slug")
    description: str = Field(description="Course description")
    content: Optional[str] = Field(description="Detailed content")
    category: CourseCategory = Field(description="Course category")
    subjects: List[CourseSubject] = Field(description="Course subjects")
    duration_months: int = Field(description="Duration in months")
    hours_per_week: str = Field(description="Hours per week")
    class_schedule: Optional[dict] = Field(description="Class schedule")
    image: Optional[str] = Field(description="Course image URL")
    price: Decimal = Field(description="Course price")
    price_display: str = Field(description="Formatted price")
    max_students: int = Field(description="Maximum students")
    total_hours: int = Field(description="Total study hours")
    order: int = Field(description="Display order")

    @classmethod
    def of(cls, course: c.Course) -> Self:
        return cls(
            id=course.id,
            name=course.name,
            slug=course.slug,
            description=course.description,
            content=course.content,
            category=CourseCategory.of(course.category),
            subjects=[CourseSubject.of(cs) for cs in course.course_subjects],
            duration_months=course.duration_months,
            hours_per_week=course.hours_per_week,
            class_schedule=course.class_schedule,
            image=course.image,
            price=course.price,
            price_display=course.price_display,
            max_students=course.max_students,
            total_hours=course.total_hours,
            order=course.order
        )


@dataclass(config=config)
class Alumni:
    id: str = Field(description="Alumni ID")
    name: str = Field(description="Alumni name")
    photo: Optional[str] = Field(description="Photo URL")
    academic_achievements: Optional[List] = Field(description="Academic achievements")
    exam_results: Optional[dict] = Field(description="Exam results")
    current_school: Optional[str] = Field(description="Current school")
    university_admitted: Optional[str] = Field(description="University admitted")
    scholarship_received: Optional[str] = Field(description="Scholarship received")
    testimonial: Optional[str] = Field(description="Testimonial")
    linkedin_url: Optional[str] = Field(description="LinkedIn URL")
    graduation_year: Optional[int] = Field(description="Graduation year")
    is_featured: bool = Field(description="Is featured")

    @classmethod
    def of(cls, alumni: c.Alumni) -> Self:
        return cls(
            id=alumni.id,
            name=alumni.name,
            photo=alumni.photo,
            academic_achievements=alumni.academic_achievements,
            exam_results=alumni.exam_results,
            current_school=alumni.current_school,
            university_admitted=alumni.university_admitted,
            scholarship_received=alumni.scholarship_received,
            testimonial=alumni.testimonial,
            linkedin_url=alumni.linkedin_url,
            graduation_year=alumni.graduation_year,
            is_featured=alumni.is_featured
        )


# ----------------------------------------------------------------
# Material responses
# ----------------------------------------------------------------
@dataclass(config=config)
class MaterialCategory:
    id: str = Field(description="Category ID")
    name: str = Field(description="Category name")
    description: Optional[str] = Field(description="Category description")
    icon: Optional[str] = Field(description="Category icon")
    is_public: bool = Field(description="Is public")
    order: int = Field(description="Display order")
    materials_count: int = Field(description="Number of materials")

    @classmethod
    def of(cls, category: c.MaterialCategory) -> Self:
        return cls(
            id=category.id,
            name=category.name,
            description=category.description,
            icon=category.icon,
            is_public=category.is_public,
            order=category.order,
            materials_count=category.get_public_materials_count()
        )


@dataclass(config=config)
class Material:
    id: str = Field(description="Material ID")
    title: str = Field(description="Material title")
    description: Optional[str] = Field(description="Material description")
    category: MaterialCategory = Field(description="Material category")
    course_id: Optional[str] = Field(description="Related course ID")
    subject_id: Optional[str] = Field(description="Related subject ID")
    file_url: str = Field(description="File URL/key")
    file_name: str = Field(description="File name")
    file_size: Optional[int] = Field(description="File size in bytes")
    file_size_display: str = Field(description="Human readable file size")
    file_type: str = Field(description="File type")
    is_public: bool = Field(description="Is public")
    is_free: bool = Field(description="Is free")
    access_level: str = Field(description="Access level")
    access_level_display: str = Field(description="Access level display")
    download_count: int = Field(description="Download count")
    view_count: int = Field(description="View count")
    created_at: datetime = Field(description="Creation date")

    @classmethod
    def of(cls, material: c.Material) -> Self:
        return cls(
            id=material.id,
            title=material.title,
            description=material.description,
            category=MaterialCategory.of(material.category),
            course_id=material.course_id,
            subject_id=material.subject_id,
            file_url=material.file_url,
            file_name=material.file_name,
            file_size=material.file_size,
            file_size_display=material.file_size_display,
            file_type=material.file_type.value,
            is_public=material.is_public,
            is_free=material.is_free,
            access_level=material.access_level.value,
            access_level_display=material.access_level_display,
            download_count=material.download_count,
            view_count=material.view_count,
            created_at=material.created_at
        )


# ----------------------------------------------------------------
# News responses
# ----------------------------------------------------------------
@dataclass(config=config)
class NewsCategory:
    id: str = Field(description="Category ID")
    name: str = Field(description="Category name")
    slug: str = Field(description="URL slug")
    description: Optional[str] = Field(description="Category description")
    color: str = Field(description="Category color")
    news_count: int = Field(description="Number of published news")

    @classmethod
    def of(cls, category: c.NewsCategory) -> Self:
        return cls(
            id=category.id,
            name=category.name,
            slug=category.slug,
            description=category.description,
            color=category.color,
            news_count=category.get_published_news_count()
        )


@dataclass(config=config)
class News:
    id: str = Field(description="News ID")
    title: str = Field(description="News title")
    slug: str = Field(description="URL slug")
    excerpt: str = Field(description="News excerpt")
    content: str = Field(description="News content")
    image: Optional[str] = Field(description="News image URL")
    author_name: str = Field(description="Author name")
    category: Optional[NewsCategory] = Field(description="News category")
    tags: Optional[List[str]] = Field(description="News tags")
    is_featured: bool = Field(description="Is featured")
    published_at: Optional[datetime] = Field(description="Publication date")
    view_count: int = Field(description="View count")
    reading_time: int = Field(description="Estimated reading time in minutes")

    @classmethod
    def of(cls, news: c.News) -> Self:
        return cls(
            id=news.id,
            title=news.title,
            slug=news.slug,
            excerpt=news.excerpt,
            content=news.content,
            image=news.image,
            author_name=news.author_name,
            category=NewsCategory.of(news.category) if news.category else None,
            tags=news.tags,
            is_featured=news.is_featured,
            published_at=news.published_at,
            view_count=news.view_count,
            reading_time=news.reading_time
        )


# ----------------------------------------------------------------
# Config responses
# ----------------------------------------------------------------
@dataclass(config=config)
class SiteSettings:
    key: str = Field(description="Setting key")
    value: str = Field(description="Setting value")
    typed_value: any = Field(description="Typed value")
    description: Optional[str] = Field(description="Setting description")
    data_type: str = Field(description="Data type")

    @classmethod
    def of(cls, setting: c.SiteSettings) -> Self:
        return cls(
            key=setting.key,
            value=setting.value,
            typed_value=setting.get_typed_value(),
            description=setting.description,
            data_type=setting.data_type
        )


@dataclass(config=config)
class ContactInfo:
    id: str = Field(description="Contact ID")
    address: str = Field(description="Address")
    phone: str = Field(description="Phone number")
    email: str = Field(description="Email")
    maps_url: Optional[str] = Field(description="Google Maps URL")
    facebook_url: Optional[str] = Field(description="Facebook URL")
    working_hours: Optional[str] = Field(description="Working hours")

    @classmethod
    def of(cls, contact: c.ContactInfo) -> Self:
        return cls(
            id=contact.id,
            address=contact.address,
            phone=contact.phone,
            email=contact.email,
            maps_url=contact.maps_url,
            facebook_url=contact.facebook_url,
            working_hours=contact.working_hours
        )


@dataclass(config=config)
class FAQ:
    id: str = Field(description="FAQ ID")
    question: str = Field(description="Question")
    answer: str = Field(description="Answer")
    category_id: Optional[str] = Field(description="Related category ID")
    order: int = Field(description="Display order")

    @classmethod
    def of(cls, faq: c.FAQ) -> Self:
        return cls(
            id=faq.id,
            question=faq.question,
            answer=faq.answer,
            category_id=faq.category_id,
            order=faq.order
        )


@dataclass(config=config)
class Banner:
    id: str = Field(description="Banner ID")
    title: str = Field(description="Banner title")
    description: Optional[str] = Field(description="Banner description")
    image: str = Field(description="Banner image URL")
    link: Optional[str] = Field(description="Banner link")
    position: str = Field(description="Banner position")
    order: int = Field(description="Display order")
    is_currently_active: bool = Field(description="Is currently active")

    @classmethod
    def of(cls, banner: c.Banner) -> Self:
        return cls(
            id=banner.id,
            title=banner.title,
            description=banner.description,
            image=banner.image,
            link=banner.link,
            position=banner.position.value,
            order=banner.order,
            is_currently_active=banner.is_currently_active()
        )


# ----------------------------------------------------------------
# Enrollment responses
# ----------------------------------------------------------------
@dataclass(config=config)
class StudentInquiry:
    id: str = Field(description="Inquiry ID")
    student_name: str = Field(description="Student name")
    student_age: int = Field(description="Student age")
    current_grade: Optional[str] = Field(description="Current grade")
    current_school: Optional[str] = Field(description="Current school")
    contact_name: str = Field(description="Contact person name")
    email: str = Field(description="Email")
    phone: str = Field(description="Phone number")
    message: Optional[str] = Field(description="Message")
    preferred_contact_time: Optional[str] = Field(description="Preferred contact time")
    status: str = Field(description="Inquiry status")
    status_display: str = Field(description="Status display text")
    is_contacted: bool = Field(description="Has been contacted")
    created_at: datetime = Field(description="Creation date")

    @classmethod
    def of(cls, inquiry: c.StudentInquiry) -> Self:
        return cls(
            id=inquiry.id,
            student_name=inquiry.student_name,
            student_age=inquiry.student_age,
            current_grade=inquiry.current_grade,
            current_school=inquiry.current_school,
            contact_name=inquiry.contact_name,
            email=inquiry.email,
            phone=inquiry.phone,
            message=inquiry.message,
            preferred_contact_time=inquiry.preferred_contact_time,
            status=inquiry.status.value,
            status_display=inquiry.status_display,
            is_contacted=inquiry.is_contacted,
            created_at=inquiry.created_at
        )


@dataclass(config=config)
class CourseEnrollment:
    id: str = Field(description="Enrollment ID")
    student_name: str = Field(description="Student name")
    student_id: str = Field(description="Student ID")
    course: Course = Field(description="Enrolled course")
    enrollment_date: date = Field(description="Enrollment date")
    start_date: Optional[date] = Field(description="Course start date")
    end_date: Optional[date] = Field(description="Course end date")
    status: str = Field(description="Enrollment status")
    status_display: str = Field(description="Status display text")
    tuition_fee: Decimal = Field(description="Tuition fee")
    paid_amount: Decimal = Field(description="Paid amount")
    remaining_fee: Decimal = Field(description="Remaining fee")
    payment_status: str = Field(description="Payment status")
    payment_status_display: str = Field(description="Payment status display")
    payment_percentage: float = Field(description="Payment percentage")

    @classmethod
    def of(cls, enrollment: c.CourseEnrollment) -> Self:
        return cls(
            id=enrollment.id,
            student_name=enrollment.student_name,
            student_id=enrollment.student_id,
            course=Course.of(enrollment.course),
            enrollment_date=enrollment.enrollment_date,
            start_date=enrollment.start_date,
            end_date=enrollment.end_date,
            status=enrollment.status.value,
            status_display=enrollment.status_display,
            tuition_fee=enrollment.tuition_fee,
            paid_amount=enrollment.paid_amount,
            remaining_fee=enrollment.remaining_fee,
            payment_status=enrollment.payment_status.value,
            payment_status_display=enrollment.payment_status_display,
            payment_percentage=enrollment.payment_percentage
        )


# ----------------------------------------------------------------
# Common list responses
# ----------------------------------------------------------------
@dataclass(config=config)
class PaginatedResponse:
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number")
    per_page: int = Field(description="Items per page")
    total_pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Has next page")
    has_prev: bool = Field(description="Has previous page")


@dataclass(config=config)
class CourseListResponse(PaginatedResponse):
    items: List[Course] = Field(description="List of courses")


@dataclass(config=config)
class NewsListResponse(PaginatedResponse):
    items: List[News] = Field(description="List of news")


@dataclass(config=config)
class MaterialListResponse(PaginatedResponse):
    items: List[Material] = Field(description="List of materials")


@dataclass(config=config)
class AlumniListResponse(PaginatedResponse):
    items: List[Alumni] = Field(description="List of alumni")
