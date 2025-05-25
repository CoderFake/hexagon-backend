from datetime import date, datetime
from typing import List, Optional
from decimal import Decimal

import app.model.composite as c
from pydantic import ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic.dataclasses import dataclass
from typing_extensions import Self

# ================================================================
# Settings
# ================================================================

config = ConfigDict(
    alias_generator=to_camel,
    populate_by_name=True,
)


# ================================================================
# Authentication Responses
# ================================================================

@dataclass(config=config)
class Me:
    id: str = Field(description="Account ID")
    name: str = Field(description="User name")
    email: str = Field(description="Email address")
    created_at: datetime = Field(description="Registration date")
    last_login: Optional[datetime] = Field(description="Last login date")

    @classmethod
    def of(cls, me: c.Me) -> Self:
        return cls(
            id=me.id,
            name=me.name,
            email=me.email,
            created_at=me.created_at,
            last_login=me.last_login
        )


@dataclass(config=config)
class StudentProfile:
    id: str = Field(description="Student ID")
    name: str = Field(description="Student name")
    student_id: str = Field(description="Student code")
    age: int = Field(description="Student age")
    phone: str = Field(description="Phone number")
    address: str = Field(description="Address")

    @classmethod
    def of(cls, student: c.StudentProfile) -> Self:
        return cls(
            id=student.id,
            name=student.name,
            student_id=student.student_id,
            age=student.age,
            phone=student.phone,
            address=student.address
        )


# ================================================================
# Course Responses
# ================================================================

@dataclass(config=config)
class ContentBlock:
    id: str = Field(description="Content block ID")
    title: Optional[str] = Field(description="Block title")
    image_key: Optional[str] = Field(description="Image key")
    descriptions: List[str] = Field(description="Description list")
    general_description: Optional[str] = Field(description="General description")
    order: int = Field(description="Display order")

    @classmethod
    def from_course_content(cls, block) -> Self:
        return cls(
            id=block.id,
            title=block.title,
            image_key=block.image_key,
            descriptions=block.descriptions,
            general_description=None,
            order=block.order
        )

    @classmethod
    def from_roadmap_content(cls, block) -> Self:
        return cls(
            id=block.id,
            title=block.title,
            image_key=block.image_key,
            descriptions=block.descriptions,
            general_description=block.general_description,
            order=block.order
        )

    @classmethod
    def from_additional_content(cls, block) -> Self:
        return cls(
            id=block.id,
            title=block.title,
            image_key=block.image_key,
            descriptions=block.descriptions,
            general_description=block.general_description,
            order=block.order
        )

    @classmethod
    def from_news_content(cls, block) -> Self:
        return cls(
            id=block.id,
            title=block.title,
            image_key=block.image_key,
            descriptions=block.descriptions,
            general_description=block.general_description,
            order=block.order
        )


@dataclass(config=config)
class CourseCategory:
    id: str = Field(description="Category ID")
    name: str = Field(description="Category name")
    slug: str = Field(description="URL slug")
    description: Optional[str] = Field(description="Category description")
    order: int = Field(description="Display order")

    @classmethod
    def of(cls, category: c.CourseCategory) -> Self:
        return cls(
            id=category.id,
            name=category.name,
            slug=category.slug,
            description=category.description,
            order=category.order
        )


@dataclass(config=config)
class CourseFile:
    id: str = Field(description="File ID")
    name: str = Field(description="File name")
    description: Optional[str] = Field(description="File description")
    file_key: str = Field(description="File storage key")
    file_type: str = Field(description="File type")
    file_size_display: str = Field(description="Human readable file size")
    download_count: int = Field(description="Download count")

    @classmethod
    def of(cls, file: c.CourseFile) -> Self:
        return cls(
            id=file.id,
            name=file.name,
            description=file.description,
            file_key=file.file_key,
            file_type=file.file_type.value,
            file_size_display=file.file_size_display,
            download_count=file.download_count
        )


@dataclass(config=config)
class OutstandingStudent:
    id: str = Field(description="Student ID")
    name: str = Field(description="Student name")
    image_key: Optional[str] = Field(description="Student photo key")
    awards: List[str] = Field(description="Awards list")
    awards_display: str = Field(description="Awards as string")
    current_education: str = Field(description="Current education")
    testimonial: Optional[str] = Field(description="Student testimonial")

    @classmethod
    def of(cls, student: c.OutstandingStudent) -> Self:
        return cls(
            id=student.id,
            name=student.name,
            image_key=student.image_key,
            awards=student.awards,
            awards_display=student.awards_display,
            current_education=student.current_education,
            testimonial=student.testimonial
        )


@dataclass(config=config)
class CourseRoadmap:
    id: str = Field(description="Roadmap ID")
    short_description: str = Field(description="Short description")
    image_key: Optional[str] = Field(description="Roadmap image key")
    slogan: str = Field(description="Course slogan")
    content_blocks: List[ContentBlock] = Field(description="Content blocks")

    @classmethod
    def of(cls, roadmap: c.CourseRoadmap) -> Self:
        return cls(
            id=roadmap.id,
            short_description=roadmap.short_description,
            image_key=roadmap.image_key,
            slogan=roadmap.slogan,
            content_blocks=[
                ContentBlock.from_roadmap_content(block)
                for block in roadmap.get_active_content_blocks()
            ]
        )


@dataclass(config=config)
class CourseAdditionalInfo:
    id: str = Field(description="Additional info ID")
    content_blocks: List[ContentBlock] = Field(description="Content blocks")

    @classmethod
    def of(cls, info: c.CourseAdditionalInfo) -> Self:
        return cls(
            id=info.id,
            content_blocks=[
                ContentBlock.from_additional_content(block)
                for block in info.get_active_content_blocks()
            ]
        )


@dataclass(config=config)
class CourseClass:
    id: str = Field(description="Class ID")
    title: str = Field(description="Class title")
    short_description: str = Field(description="Short description")
    image_key: Optional[str] = Field(description="Class image key")
    address: str = Field(description="Learning address")
    schedule_description: str = Field(description="Schedule description")
    learning_method: str = Field(description="Learning method")
    class_code: str = Field(description="Class code")
    current_students_count: int = Field(description="Current students count")
    max_students: int = Field(description="Maximum students")
    available_slots: int = Field(description="Available slots")
    can_enroll: bool = Field(description="Can enroll flag")
    content_blocks: List[ContentBlock] = Field(description="Class content blocks")

    @classmethod
    def of(cls, course_class: c.CourseClass) -> Self:
        return cls(
            id=course_class.id,
            title=course_class.title,
            short_description=course_class.short_description,
            image_key=course_class.image_key,
            address=course_class.address,
            schedule_description=course_class.schedule_description,
            learning_method=course_class.learning_method.value,
            class_code=course_class.class_code,
            current_students_count=course_class.current_students_count,
            max_students=course_class.max_students,
            available_slots=course_class.available_slots,
            can_enroll=course_class.can_enroll(),
            content_blocks=[
                ContentBlock.from_course_content(block)
                for block in course_class.get_active_content_blocks()
            ]
        )


@dataclass(config=config)
class Course:
    id: str = Field(description="Course ID")
    title: str = Field(description="Course title")
    slug: str = Field(description="URL slug")
    short_description: str = Field(description="Short description")
    image_key: Optional[str] = Field(description="Course image key")
    is_featured: bool = Field(description="Is featured course")
    category: CourseCategory = Field(description="Course category")
    classes: List[CourseClass] = Field(description="Course classes")
    files: List[CourseFile] = Field(description="Course files")
    outstanding_students: List[OutstandingStudent] = Field(description="Outstanding students")
    roadmap: Optional[CourseRoadmap] = Field(description="Course roadmap")
    additional_info: Optional[CourseAdditionalInfo] = Field(description="Additional information")

    # Summary fields
    total_classes_count: int = Field(description="Total classes count")
    total_files_count: int = Field(description="Total files count")

    @classmethod
    def of(cls, course: c.Course) -> Self:
        return cls(
            id=course.id,
            title=course.title,
            slug=course.slug,
            short_description=course.short_description,
            image_key=course.image_key,
            is_featured=course.is_featured,
            category=CourseCategory.of(course.category),
            classes=[CourseClass.of(cls) for cls in course.classes if cls.is_active],
            files=[CourseFile.of(file) for file in course.files if file.is_active],
            outstanding_students=[
                OutstandingStudent.of(student) for student in course.get_featured_outstanding_students()
            ],
            roadmap=CourseRoadmap.of(course.roadmap) if course.has_roadmap() else None,
            additional_info=CourseAdditionalInfo.of(course.additional_info) if course.has_additional_info() else None,
            total_classes_count=course.get_total_classes_count(),
            total_files_count=course.get_total_files_count()
        )


@dataclass(config=config)
class CourseSummary:
    """Simplified course info for listings"""
    id: str = Field(description="Course ID")
    title: str = Field(description="Course title")
    slug: str = Field(description="URL slug")
    short_description: str = Field(description="Short description")
    image_key: Optional[str] = Field(description="Course image key")
    is_featured: bool = Field(description="Is featured course")
    category: CourseCategory = Field(description="Course category")
    total_classes_count: int = Field(description="Total classes count")

    @classmethod
    def of(cls, course: c.Course) -> Self:
        return cls(
            id=course.id,
            title=course.title,
            slug=course.slug,
            short_description=course.short_description,
            image_key=course.image_key,
            is_featured=course.is_featured,
            category=CourseCategory.of(course.category),
            total_classes_count=course.get_total_classes_count()
        )


# ================================================================
# Enrollment Responses
# ================================================================

@dataclass(config=config)
class StudentEnrollment:
    id: str = Field(description="Enrollment ID")
    course_title: str = Field(description="Course title")
    class_title: str = Field(description="Class title")
    class_code: str = Field(description="Class code")
    enrollment_date: date = Field(description="Enrollment date")
    start_date: Optional[date] = Field(description="Start date")
    end_date: Optional[date] = Field(description="End date")
    status: str = Field(description="Enrollment status")
    status_display: str = Field(description="Status display text")
    tuition_fee: Decimal = Field(description="Tuition fee")
    paid_amount: Decimal = Field(description="Paid amount")
    remaining_fee: Decimal = Field(description="Remaining fee")
    payment_status: str = Field(description="Payment status")
    payment_status_display: str = Field(description="Payment status display")
    payment_percentage: float = Field(description="Payment percentage")
    final_grade: Optional[str] = Field(description="Final grade")

    @classmethod
    def of(cls, enrollment: c.StudentEnrollment) -> Self:
        return cls(
            id=enrollment.id,
            course_title=enrollment.course.title,
            class_title=enrollment.course_class.title,
            class_code=enrollment.course_class.class_code,
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
            payment_percentage=enrollment.payment_percentage,
            final_grade=enrollment.final_grade
        )


# ================================================================
# General Content Responses
# ================================================================

@dataclass(config=config)
class GeneralRoadmap:
    id: str = Field(description="Roadmap ID")
    title: str = Field(description="Roadmap title")
    short_description: str = Field(description="Short description")
    image_key: Optional[str] = Field(description="Roadmap image key")
    content_blocks: List[ContentBlock] = Field(description="Content blocks")

    @classmethod
    def of(cls, roadmap: c.GeneralRoadmap) -> Self:
        return cls(
            id=roadmap.id,
            title=roadmap.title,
            short_description=roadmap.short_description,
            image_key=roadmap.image_key,
            content_blocks=[
                ContentBlock.from_roadmap_content(block)
                for block in roadmap.get_active_content_blocks()
            ]
        )


@dataclass(config=config)
class AboutSection:
    id: str = Field(description="About section ID")
    title: str = Field(description="Section title")
    short_description: str = Field(description="Short description")
    image_key: Optional[str] = Field(description="Section image key")
    content_blocks: List[ContentBlock] = Field(description="Content blocks")

    @classmethod
    def of(cls, section: c.AboutSection) -> Self:
        return cls(
            id=section.id,
            title=section.title,
            short_description=section.short_description,
            image_key=section.image_key,
            content_blocks=[
                ContentBlock.from_additional_content(block)
                for block in section.get_active_content_blocks()
            ]
        )


# ================================================================
# News Responses
# ================================================================

@dataclass(config=config)
class NewsCategory:
    id: str = Field(description="Category ID")
    name: str = Field(description="Category name")
    slug: str = Field(description="URL slug")
    description: Optional[str] = Field(description="Category description")
    category_type: str = Field(description="Category type")
    category_type_display: str = Field(description="Category type display")
    course_title: Optional[str] = Field(description="Related course title")

    @classmethod
    def of(cls, category: c.NewsCategory) -> Self:
        return cls(
            id=category.id,
            name=category.name,
            slug=category.slug,
            description=category.description,
            category_type=category.category_type.value,
            category_type_display=category.category_type_display,
            course_title=category.course.title if category.course else None
        )


@dataclass(config=config)
class News:
    id: str = Field(description="News ID")
    title: str = Field(description="News title")
    slug: str = Field(description="URL slug")
    short_description: str = Field(description="Short description")
    image_key: Optional[str] = Field(description="News image key")
    category: NewsCategory = Field(description="News category")
    published_at: Optional[datetime] = Field(description="Publication date")
    view_count: int = Field(description="View count")
    reading_time: int = Field(description="Estimated reading time")
    content_blocks: List[ContentBlock] = Field(description="News content blocks")

    @classmethod
    def of(cls, news: c.News) -> Self:
        return cls(
            id=news.id,
            title=news.title,
            slug=news.slug,
            short_description=news.short_description,
            image_key=news.image_key,
            category=NewsCategory.of(news.category),
            published_at=news.published_at,
            view_count=news.view_count,
            reading_time=news.reading_time,
            content_blocks=[
                ContentBlock.from_news_content(block)
                for block in news.get_active_content_blocks()
            ]
        )


@dataclass(config=config)
class NewsSummary:
    """Simplified news info for listings"""
    id: str = Field(description="News ID")
    title: str = Field(description="News title")
    slug: str = Field(description="URL slug")
    short_description: str = Field(description="Short description")
    image_key: Optional[str] = Field(description="News image key")
    category: NewsCategory = Field(description="News category")
    published_at: Optional[datetime] = Field(description="Publication date")
    reading_time: int = Field(description="Estimated reading time")

    @classmethod
    def of(cls, news: c.News) -> Self:
        return cls(
            id=news.id,
            title=news.title,
            slug=news.slug,
            short_description=news.short_description,
            image_key=news.image_key,
            category=NewsCategory.of(news.category),
            published_at=news.published_at,
            reading_time=news.reading_time
        )


# ================================================================
# Pagination Responses
# ================================================================

@dataclass(config=config)
class PaginatedResponse:
    total: int = Field(description="Total items count")
    page: int = Field(description="Current page number")
    per_page: int = Field(description="Items per page")
    total_pages: int = Field(description="Total pages count")
    has_next: bool = Field(description="Has next page")
    has_prev: bool = Field(description="Has previous page")


@dataclass(config=config)
class CourseListResponse(PaginatedResponse):
    items: List[CourseSummary] = Field(description="Course items")


@dataclass(config=config)
class NewsListResponse(PaginatedResponse):
    items: List[NewsSummary] = Field(description="News items")


@dataclass(config=config)
class EnrollmentListResponse(PaginatedResponse):
    items: List[StudentEnrollment] = Field(description="Enrollment items")