from typing import List
import app.service.course as cs
import app.service.news as ns
import app.service.website as ws
from app.api.commons import (
    APIRouter,
    Depends,
    vr,
)

router = APIRouter()


@router.get(
    "/featured-courses",
    responses={
        200: {"description": "Featured courses for homepage."},
    },
)
async def get_featured_courses() -> List[vr.CourseSummary]:
    """Get featured courses for homepage"""
    courses, _ = (await cs.get_courses(
        page=1,
        per_page=6
    )).get()
    return [vr.CourseSummary.of(course) for course in courses]


@router.get(
    "/featured-outstanding-students",
    responses={
        200: {"description": "Featured outstanding students."},
    },
)
async def get_featured_outstanding_students() -> List[vr.OutstandingStudent]:
    """Get featured outstanding students from all courses"""
    courses, _ = (await cs.get_courses(
        page=1,
        per_page=50
    )).get()
    
    all_students = []
    for course in courses:
        students = course.get_featured_outstanding_students()
        all_students.extend([vr.OutstandingStudent.of(student) for student in students])
    
    return all_students[:9]


@router.get(
    "/exam-results",
    responses={
        200: {"description": "Recent exam results news."},
    },
)
async def get_exam_results() -> List[vr.NewsSummary]:
    """Get recent exam results news"""
    news_list = (await ns.get_featured_news(
        category_type="exam_results",
        limit=6
    )).get()
    return [vr.NewsSummary.of(news) for news in news_list]


@router.get(
    "/upcoming-events",
    responses={
        200: {"description": "Upcoming events news."},
    },
)
async def get_upcoming_events() -> List[vr.NewsSummary]:
    """Get upcoming events news"""
    news_list = (await ns.get_featured_news(
        category_type="upcoming_events",
        limit=6
    )).get()
    return [vr.NewsSummary.of(news) for news in news_list]


@router.get(
    "/recent-news",
    responses={
        200: {"description": "Recent general news."},
    },
)
async def get_recent_general_news() -> List[vr.NewsSummary]:
    """Get recent general news"""
    news_list = (await ns.get_featured_news(
        category_type="general",
        limit=6
    )).get()
    return [vr.NewsSummary.of(news) for news in news_list]


@router.get(
    "/course-categories",
    responses={
        200: {"description": "All course categories."},
    },
)
async def get_course_categories() -> List[vr.CourseCategory]:
    """Get all course categories for navigation"""
    categories = (await cs.get_course_categories()).get()
    return [vr.CourseCategory.of(cat) for cat in categories]


@router.get(
    "/course-roadmaps",
    responses={
        200: {"description": "Course roadmaps for featured courses."},
    },
)
async def get_course_roadmaps() -> List[vr.CourseRoadmap]:
    """Get roadmaps from featured courses"""
    courses, _ = (await cs.get_courses(
        page=1,
        per_page=10
    )).get()
    
    roadmaps = []
    for course in courses:
        if course.has_roadmap():
            roadmaps.append(vr.CourseRoadmap.of(course.roadmap))
    
    return roadmaps[:3]


@router.get(
    "/hero-banners",
    responses={
        200: {"description": "Hero banners for homepage."},
    },
)
async def get_hero_banners() -> List[vr.Banner]:
    """Get hero banners for homepage"""
    banners = (await ws.get_banners(position="hero")).get()
    return [vr.Banner.of(banner) for banner in banners]


@router.get(
    "/sidebar-banners",
    responses={
        200: {"description": "Sidebar banners."},
    },
)
async def get_sidebar_banners() -> List[vr.Banner]:
    """Get sidebar banners"""
    banners = (await ws.get_banners(position="sidebar")).get()
    return [vr.Banner.of(banner) for banner in banners]


@router.get(
    "/data",
    responses={
        200: {"description": "Complete homepage data."},
    },
)
async def get_homepage_data() -> vr.HomepageData:
    """Get all homepage data in one request"""
    courses_result = await cs.get_courses(page=1, per_page=6)
    categories_result = await cs.get_course_categories()
    exam_results_result = await ns.get_featured_news(category_type="exam_results", limit=6)
    events_result = await ns.get_featured_news(category_type="upcoming_events", limit=6)
    news_result = await ns.get_featured_news(category_type="general", limit=6)
    hero_banners_result = await ws.get_banners(position="hero")
    sidebar_banners_result = await ws.get_banners(position="sidebar")
    contact_result = await ws.get_contact_info()
    
    courses, _ = courses_result.get()
    categories = categories_result.get()
    exam_results = exam_results_result.get()
    events = events_result.get()
    news = news_result.get()
    hero_banners = hero_banners_result.get()
    sidebar_banners = sidebar_banners_result.get()
    contact = contact_result.get() if contact_result.get() else None
    
    all_students = []
    for course in courses:
        students = course.get_featured_outstanding_students()
        all_students.extend(students)
    featured_students = all_students[:9]
    
    roadmaps = []
    for course in courses:
        if course.has_roadmap():
            roadmaps.append(course.roadmap)
    featured_roadmaps = roadmaps[:3]
    
    return vr.HomepageData.of(
        courses=courses,
        students=featured_students,
        exam_results=exam_results,
        events=events,
        news=news,
        categories=categories,
        roadmaps=featured_roadmaps,
        hero_banners=hero_banners,
        sidebar_banners=sidebar_banners,
        contact=contact
    )