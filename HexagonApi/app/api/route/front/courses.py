from typing import Optional, List
import app.service.course as cs
from app.api.commons import (
    APIRouter,
    Authorized,
    Depends,
    Query,
    Path,
    Response,
    vr,
    maybe_user,
)

router = APIRouter()


@router.get(
    "/categories",
    responses={
        200: {"description": "List of course categories."},
    },
)
async def get_course_categories() -> List[vr.CourseCategory]:
    """Get all active course categories"""
    categories = (await cs.get_course_categories()).get()
    return [vr.CourseCategory.of(cat) for cat in categories]


@router.get(
    "/categories/{slug}",
    responses={
        200: {"description": "Course category details."},
        404: {"description": "Category not found."},
    },
)
async def get_course_category(
    slug: str = Path(..., description="Category slug")
) -> vr.CourseCategory:
    """Get course category by slug"""
    category = (await cs.get_course_category_by_slug(slug)).get()
    return vr.CourseCategory.of(category)


@router.get(
    "",
    responses={
        200: {"description": "List of courses with pagination."},
    },
)
async def get_courses(
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page")
) -> vr.CourseListResponse:
    """Get courses with pagination"""
    courses, total = (await cs.get_courses(
        category_id=category_id,
        page=page,
        per_page=per_page
    )).get()
    
    total_pages = (total + per_page - 1) // per_page
    
    return vr.CourseListResponse(
        items=[vr.CourseSummary.of(course) for course in courses],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1
    )


@router.get(
    "/{slug}",
    responses={
        200: {"description": "Course details."},
        404: {"description": "Course not found."},
    },
)
async def get_course(
    slug: str = Path(..., description="Course slug"),
    auth: Optional[Authorized] = Depends(maybe_user)
) -> vr.Course:
    """Get course details by slug"""
    user = auth.User if auth else None
    course = (await cs.get_course_by_slug(slug)).get()
    return vr.Course.of(course, user)


@router.get(
    "/{course_id}/classes",
    responses={
        200: {"description": "List of course classes."},
        404: {"description": "Course not found."},
    },
)
async def get_course_classes(
    course_id: str = Path(..., description="Course ID"),
    open_for_enrollment: Optional[bool] = Query(None, description="Filter by enrollment status")
) -> List[vr.CourseClass]:
    """Get classes for a specific course"""
    classes = (await cs.get_course_classes(
        course_id=course_id,
        open_for_enrollment=open_for_enrollment
    )).get()
    return [vr.CourseClass.of(cls) for cls in classes]


@router.get(
    "/classes/code/{class_code}",
    responses={
        200: {"description": "Course class details."},
        404: {"description": "Class not found."},
    },
)
async def get_course_class_by_code(
    class_code: str = Path(..., description="Class code")
) -> vr.CourseClass:
    """Get course class by class code"""
    course_class = (await cs.get_course_class_by_code(class_code)).get()
    return vr.CourseClass.of(course_class) 