from datetime import date, datetime
from typing import List, Optional
from decimal import Decimal

import app.model.composite as c
from pydantic import ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic.dataclasses import dataclass
from typing_extensions import Self
from app.resources import context as r

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
class User:
    id: str = Field(description="User ID")
    username: str = Field(description="Username")
    date_joined: datetime = Field(description="Registration date")
    last_login: Optional[datetime] = Field(description="Last login date")
    login_method: Optional[str] = Field(description="Login method")
    profile_picture: Optional[str] = Field(description="Profile picture URL")

    @classmethod
    def of(cls, user: c.User) -> Self:
        from app.resources import context as r
        
        profile_picture_url = None
        if user.profile and user.profile.profile_picture:
            try:
                if user.profile.profile_picture.startswith('http'):
                    profile_picture_url = user.profile.profile_picture
                else:
                    profile_picture_url = r.storage.urlize(user.profile.profile_picture)
            except Exception:
                profile_picture_url = user.profile.profile_picture
        
        return cls(
            id=user.id,
            username=user.username,
            date_joined=user.date_joined,
            last_login=user.last_login,
            login_method=user.login_method,
            profile_picture=profile_picture_url
        )


@dataclass(config=config)
class UserProfile:
    id: str = Field(description="Profile ID")
    full_name: str = Field(description="Full name")
    bio: Optional[str] = Field(description="Biography")
    address: Optional[str] = Field(description="Address")
    profile_picture: Optional[str] = Field(description="Profile picture URL")

    @classmethod
    def of(cls, profile: c.UserProfile) -> Self:
        
        profile_picture_url = None
        if profile.profile_picture:
            try:
                if profile.profile_picture.startswith('http'):
                    profile_picture_url = profile.profile_picture
                else:
                    profile_picture_url = r.storage.urlize(profile.profile_picture)
            except Exception:
                profile_picture_url = profile.profile_picture
        
        return cls(
            id=profile.id,
            full_name=profile.full_name,
            bio=profile.bio,
            address=profile.address,
            profile_picture=profile_picture_url
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
    file_size: Optional[int] = Field(description="File size in bytes")
    file_size_display: str = Field(description="Human readable file size")
    file_type: Optional[str] = Field(description="File type")
    file_extension: str = Field(description="File extension")
    is_downloadable: bool = Field(description="Can be downloaded")
    permission_level: str = Field(description="Permission level")
    download_count: int = Field(description="Download count")
    can_download: bool = Field(description="User can download this file")

    @classmethod
    def of(cls, file: c.CourseFile, user: Optional[c.User] = None) -> Self:
        return cls(
            id=file.id,
            name=file.name,
            description=file.description,
            file_key=file.file_key,
            file_size=file.file_size,
            file_size_display=file.file_size_display,
            file_type=file.file_type,
            file_extension=file.file_extension,
            is_downloadable=file.is_downloadable,
            permission_level=file.permission_level,
            download_count=file.download_count,
            can_download=file.can_download(user)
        )


@dataclass(config=config)
class OutstandingStudent:
    id: str = Field(description="Student ID")
    name: str = Field(description="Student name")
    image_key: Optional[str] = Field(description="Student photo key")
    awards: List[str] = Field(description="Awards list")
    awards_display: str = Field(description="Awards as string")
    current_education: str = Field(description="Current education")

    @classmethod
    def of(cls, student: c.OutstandingStudent) -> Self:
        return cls(
            id=student.id,
            name=student.name,
            image_key=student.image_key,
            awards=student.awards,
            awards_display=student.awards_display,
            current_education=student.current_education
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
    def of(cls, course: c.Course, user: Optional[c.User] = None) -> Self:
        return cls(
            id=course.id,
            title=course.title,
            slug=course.slug,
            short_description=course.short_description,
            image_key=course.image_key,
            category=CourseCategory.of(course.category),
            classes=[CourseClass.of(cls) for cls in course.classes if cls.is_active],
            files=[CourseFile.of(file, user) for file in course.files if file.is_active],
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
class EnrollmentListResponse(PaginatedResponse):
    items: List[StudentEnrollment] = Field(description="Enrollment items")


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
    order: int = Field(description="Display order")
    published_news_count: int = Field(description="Published news count")

    @classmethod
    def of(cls, category: c.NewsCategory) -> Self:
        return cls(
            id=category.id,
            name=category.name,
            slug=category.slug,
            description=category.description,
            category_type=category.category_type.value,
            category_type_display=category.category_type_display,
            order=category.order,
            published_news_count=category.get_published_news_count()
        )


@dataclass(config=config)
class NewsContentBlock:
    id: str = Field(description="Content block ID")
    title: Optional[str] = Field(description="Block title")
    image_key: Optional[str] = Field(description="Image key")
    descriptions: List[str] = Field(description="Description list")
    general_description: Optional[str] = Field(description="General description")
    order: int = Field(description="Display order")

    @classmethod
    def of(cls, block: c.NewsContentBlock) -> Self:
        return cls(
            id=block.id,
            title=block.title,
            image_key=block.image_key,
            descriptions=block.descriptions,
            general_description=block.general_description,
            order=block.order
        )


@dataclass(config=config)
class News:
    id: str = Field(description="News ID")
    title: str = Field(description="News title")
    slug: str = Field(description="URL slug")
    short_description: str = Field(description="Short description")
    image_key: Optional[str] = Field(description="News image key")
    published_at: Optional[datetime] = Field(description="Published date")
    view_count: int = Field(description="View count")
    is_recently_published: bool = Field(description="Recently published flag")
    category: NewsCategory = Field(description="News category")
    content_blocks: List[NewsContentBlock] = Field(description="Content blocks")

    @classmethod
    def of(cls, news: c.News) -> Self:
        return cls(
            id=news.id,
            title=news.title,
            slug=news.slug,
            short_description=news.short_description,
            image_key=news.image_key,
            published_at=news.published_at,
            view_count=news.view_count,
            is_recently_published=news.is_recently_published,
            category=NewsCategory.of(news.category),
            content_blocks=[
                NewsContentBlock.of(block)
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
    published_at: Optional[datetime] = Field(description="Published date")
    view_count: int = Field(description="View count")
    is_recently_published: bool = Field(description="Recently published flag")
    category: NewsCategory = Field(description="News category")

    @classmethod
    def of(cls, news: c.News) -> Self:
        return cls(
            id=news.id,
            title=news.title,
            slug=news.slug,
            short_description=news.short_description,
            image_key=news.image_key,
            published_at=news.published_at,
            view_count=news.view_count,
            is_recently_published=news.is_recently_published,
            category=NewsCategory.of(news.category)
        )


@dataclass(config=config)
class NewsListResponse(PaginatedResponse):
    items: List[NewsSummary] = Field(description="News items")


# ================================================================
# Website Settings & Configuration Responses
# ================================================================

@dataclass(config=config)
class SiteSettings:
    key: str = Field(description="Setting key")
    value: str = Field(description="Setting value")
    description: Optional[str] = Field(description="Setting description")
    data_type: str = Field(description="Data type")

    @classmethod
    def of(cls, settings: c.SiteSettings) -> "SiteSettings":
        return cls(
            key=settings.key,
            value=settings.value,
            description=settings.description,
            data_type=settings.data_type
        )


@dataclass(config=config)
class ContactInfo:
    address: str = Field(description="Address")
    phone: str = Field(description="Phone number")
    email: str = Field(description="Email address")
    maps_url: Optional[str] = Field(description="Google Maps URL")
    facebook_url: Optional[str] = Field(description="Facebook URL")
    working_hours: Optional[str] = Field(description="Working hours")

    @classmethod
    def of(cls, contact: c.ContactInfo) -> "ContactInfo":
        return cls(
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
    category: Optional[CourseCategory] = Field(description="Related course category")
    order: int = Field(description="Display order")

    @classmethod
    def of(cls, faq: c.FAQ) -> "FAQ":
        return cls(
            id=faq.id,
            question=faq.question,
            answer=faq.answer,
            category=CourseCategory.of(faq.category) if faq.category else None,
            order=faq.order
        )


@dataclass(config=config)
class Banner:
    id: str = Field(description="Banner ID")
    title: str = Field(description="Banner title")
    description: Optional[str] = Field(description="Banner description")
    image: str = Field(description="Banner image")
    link: Optional[str] = Field(description="Banner link")
    position: str = Field(description="Banner position")
    order: int = Field(description="Display order")

    @classmethod
    def of(cls, banner: c.Banner) -> "Banner":
        return cls(
            id=banner.id,
            title=banner.title,
            description=banner.description,
            image=banner.image,
            link=banner.link,
            position=banner.position,
            order=banner.order
        )


@dataclass(config=config)
class WebsiteConfig:
    site_settings: List[SiteSettings] = Field(description="Site settings")
    contact_info: Optional[ContactInfo] = Field(description="Contact information")
    banners: List[Banner] = Field(description="Active banners")

    @classmethod
    def of(cls, settings: List[c.SiteSettings], contact: Optional[c.ContactInfo], banners: List[c.Banner]) -> "WebsiteConfig":
        return cls(
            site_settings=[SiteSettings.of(s) for s in settings],
            contact_info=ContactInfo.of(contact) if contact else None,
            banners=[Banner.of(b) for b in banners]
        )


@dataclass(config=config)
class HomepageData:
    featured_courses: List[CourseSummary] = Field(description="Featured courses")
    featured_students: List[OutstandingStudent] = Field(description="Featured outstanding students")
    exam_results: List[NewsSummary] = Field(description="Recent exam results")
    upcoming_events: List[NewsSummary] = Field(description="Upcoming events")
    recent_news: List[NewsSummary] = Field(description="Recent general news")
    course_categories: List[CourseCategory] = Field(description="Course categories")
    course_roadmaps: List[CourseRoadmap] = Field(description="Course roadmaps")
    hero_banners: List[Banner] = Field(description="Hero banners")
    sidebar_banners: List[Banner] = Field(description="Sidebar banners")
    contact_info: Optional[ContactInfo] = Field(description="Contact information")

    @classmethod
    def of(cls, 
           courses: List[c.Course],
           students: List[c.OutstandingStudent], 
           exam_results: List[c.News],
           events: List[c.News],
           news: List[c.News],
           categories: List[c.CourseCategory],
           roadmaps: List[c.CourseRoadmap],
           hero_banners: List[c.Banner],
           sidebar_banners: List[c.Banner],
           contact: Optional[c.ContactInfo]) -> "HomepageData":
        return cls(
            featured_courses=[CourseSummary.of(course) for course in courses],
            featured_students=[OutstandingStudent.of(student) for student in students],
            exam_results=[NewsSummary.of(news) for news in exam_results],
            upcoming_events=[NewsSummary.of(news) for news in events],
            recent_news=[NewsSummary.of(news) for news in news],
            course_categories=[CourseCategory.of(cat) for cat in categories],
            course_roadmaps=[CourseRoadmap.of(roadmap) for roadmap in roadmaps],
            hero_banners=[Banner.of(banner) for banner in hero_banners],
            sidebar_banners=[Banner.of(banner) for banner in sidebar_banners],
            contact_info=ContactInfo.of(contact) if contact else None
        )


# ================================================================
# Contact Inquiry Responses
# ================================================================

@dataclass(config=config)
class ContactInquiry:
    id: str = Field(description="Inquiry ID")
    full_name: str = Field(description="Full name")
    phone: str = Field(description="Phone number")
    email: Optional[str] = Field(description="Email address")
    course_title: Optional[str] = Field(description="Interested course title")
    class_title: Optional[str] = Field(description="Interested class title")
    message: Optional[str] = Field(description="Message")
    inquiry_type: str = Field(description="Inquiry type")
    inquiry_type_display: str = Field(description="Inquiry type display")
    status: str = Field(description="Status")
    status_display: str = Field(description="Status display")
    created_at: datetime = Field(description="Created date")

    @classmethod
    def of(cls, inquiry: c.ContactInquiry) -> "ContactInquiry":
        return cls(
            id=inquiry.id,
            full_name=inquiry.full_name,
            phone=inquiry.phone,
            email=inquiry.email,
            course_title=inquiry.course.title if inquiry.course else None,
            class_title=inquiry.course_class.title if inquiry.course_class else None,
            message=inquiry.message,
            inquiry_type=inquiry.inquiry_type,
            inquiry_type_display=inquiry.inquiry_type_display,
            status=inquiry.status,
            status_display=inquiry.status_display,
            created_at=inquiry.created_at
        )


@dataclass(config=config)
class ContactInquiryResponse:
    success: bool = Field(description="Success status")
    message: str = Field(description="Response message")
    inquiry_id: str = Field(description="Created inquiry ID")

    @classmethod
    def success_response(cls, inquiry_id: str) -> "ContactInquiryResponse":
        return cls(
            success=True,
            message="Cảm ơn bạn đã liên hệ! Chúng tôi sẽ phản hồi trong thời gian sớm nhất.",
            inquiry_id=inquiry_id
        )


# ================================================================
# File Download Responses
# ================================================================

@dataclass(config=config)
class FileDownloadResponse:
    file_id: str = Field(description="File ID")
    file_name: str = Field(description="File name")
    download_url: str = Field(description="Download URL")
    file_size: Optional[int] = Field(description="File size in bytes")
    file_type: Optional[str] = Field(description="File type")
    expires_in: int = Field(description="URL expires in seconds", default=3600)

    @classmethod
    def of(cls, file: c.CourseFile, download_url: str) -> "FileDownloadResponse":
        return cls(
            file_id=file.id,
            file_name=file.name,
            download_url=download_url,
            file_size=file.file_size,
            file_type=file.file_type,
            expires_in=3600
        )