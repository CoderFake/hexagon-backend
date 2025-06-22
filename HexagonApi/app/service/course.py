from typing import List, Optional
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload, joinedload

import app.model.db as m
import app.model.composite as c
from .commons import service, Maybe, Errors, r


@service
async def get_course_categories(active_only: bool = True) -> Maybe[List[c.CourseCategory]]:
    """Get all course categories"""
    query = select(m.CourseCategory)
    if active_only:
        query = query.where(m.CourseCategory.is_active == True)
    query = query.order_by(m.CourseCategory.order, m.CourseCategory.name)
    
    result = await r.tx.execute(query)
    categories = result.scalars().all()
    return [c.CourseCategory.of(cat) for cat in categories]


@service
async def get_course_category_by_slug(slug: str) -> Maybe[c.CourseCategory]:
    """Get course category by slug"""
    query = select(m.CourseCategory).where(
        and_(
            m.CourseCategory.slug == slug,
            m.CourseCategory.is_active == True
        )
    )
    
    result = await r.tx.execute(query)
    category = result.scalar_one_or_none()
    
    if not category:
        return Errors.DATA_NOT_FOUND
    
    return c.CourseCategory.of(category)


@service
async def get_courses(
    category_id: Optional[str] = None,
    active_only: bool = True,
    page: int = 1,
    per_page: int = 20
) -> Maybe[tuple[List[c.Course], int]]:
    """Get courses with pagination"""
    query = select(m.Course).options(
        joinedload(m.Course.category),
        selectinload(m.Course.classes),
        selectinload(m.Course.files),
        selectinload(m.Course.outstanding_students),
        selectinload(m.Course.roadmap).selectinload(m.CourseRoadmap.content_blocks),
        selectinload(m.Course.additional_info).selectinload(m.CourseAdditionalInfo.content_blocks)
    )
    
    if active_only:
        query = query.where(m.Course.is_active == True)
    
    if category_id:
        query = query.where(m.Course.category_id == category_id)
    
    count_query = select(func.count(m.Course.id))
    if active_only:
        count_query = count_query.where(m.Course.is_active == True)
    if category_id:
        count_query = count_query.where(m.Course.category_id == category_id)
    
    total_result = await r.tx.execute(count_query)
    total = total_result.scalar()
    
    query = query.order_by(m.Course.order, m.Course.title)
    query = query.offset((page - 1) * per_page).limit(per_page)
    
    result = await r.tx.execute(query)
    courses = result.scalars().all()
    
    return ([c.Course.of(course) for course in courses], total)


@service
async def get_course_by_slug(slug: str) -> Maybe[c.Course]:
    """Get course by slug with all related data"""
    query = select(m.Course).options(
        joinedload(m.Course.category),
        selectinload(m.Course.classes).selectinload(m.CourseClass.content_blocks),
        selectinload(m.Course.files),
        selectinload(m.Course.outstanding_students),
        selectinload(m.Course.roadmap).selectinload(m.CourseRoadmap.content_blocks),
        selectinload(m.Course.additional_info).selectinload(m.CourseAdditionalInfo.content_blocks)
    ).where(
        and_(
            m.Course.slug == slug,
            m.Course.is_active == True
        )
    )
    
    result = await r.tx.execute(query)
    course = result.scalar_one_or_none()
    
    if not course:
        return Errors.DATA_NOT_FOUND
    
    return c.Course.of(course)


@service
async def get_course_by_id(course_id: str) -> Maybe[c.Course]:
    """Get course by ID with all related data"""
    query = select(m.Course).options(
        joinedload(m.Course.category),
        selectinload(m.Course.classes).selectinload(m.CourseClass.content_blocks),
        selectinload(m.Course.files),
        selectinload(m.Course.outstanding_students),
        selectinload(m.Course.roadmap).selectinload(m.CourseRoadmap.content_blocks),
        selectinload(m.Course.additional_info).selectinload(m.CourseAdditionalInfo.content_blocks)
    ).where(
        and_(
            m.Course.id == course_id,
            m.Course.is_active == True
        )
    )
    
    result = await r.tx.execute(query)
    course = result.scalar_one_or_none()
    
    if not course:
        return Errors.DATA_NOT_FOUND
    
    return c.Course.of(course)


@service
async def get_course_class_by_code(class_code: str) -> Maybe[c.CourseClass]:
    """Get course class by class code"""
    query = select(m.CourseClass).options(
        joinedload(m.CourseClass.course).joinedload(m.Course.category),
        selectinload(m.CourseClass.content_blocks)
    ).where(
        and_(
            m.CourseClass.class_code == class_code,
            m.CourseClass.is_active == True
        )
    )
    
    result = await r.tx.execute(query)
    course_class = result.scalar_one_or_none()
    
    if not course_class:
        return Errors.DATA_NOT_FOUND
    
    return c.CourseClass.of(course_class)


@service
async def get_course_classes(
    course_id: Optional[str] = None,
    active_only: bool = True,
    open_for_enrollment: Optional[bool] = None
) -> Maybe[List[c.CourseClass]]:
    """Get course classes"""
    query = select(m.CourseClass).options(
        joinedload(m.CourseClass.course).joinedload(m.Course.category),
        selectinload(m.CourseClass.content_blocks)
    )
    
    if active_only:
        query = query.where(m.CourseClass.is_active == True)
    
    if course_id:
        query = query.where(m.CourseClass.course_id == course_id)
    
    if open_for_enrollment is not None:
        query = query.where(m.CourseClass.is_open_for_enrollment == open_for_enrollment)
    
    query = query.order_by(m.CourseClass.title)
    
    result = await r.tx.execute(query)
    classes = result.scalars().all()
    
    return [c.CourseClass.of(cls) for cls in classes] 