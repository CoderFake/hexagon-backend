from typing import Optional
import app.service.enrollment as es
from app.api.commons import (
    APIRouter,
    Authorized,
    Depends,
    Query,
    Path,
    Body,
    Response,
    vr,
    vq,
    with_user,
)

router = APIRouter()


@router.get(
    "",
    responses={
        200: {"description": "List of user enrollments with pagination."},
    },
)
async def get_my_enrollments(
    auth: Authorized = Depends(with_user),
    status: Optional[str] = Query(None, description="Filter by enrollment status"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page")
) -> vr.EnrollmentListResponse:
    """Get current user's enrollments"""
    enrollments, total = (await es.get_user_enrollments(
        user=auth.User,
        status=status,
        page=page,
        per_page=per_page
    )).get()
    
    total_pages = (total + per_page - 1) // per_page
    
    return vr.EnrollmentListResponse(
        items=[vr.StudentEnrollment.of(enrollment) for enrollment in enrollments],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1
    )


@router.get(
    "/{enrollment_id}",
    responses={
        200: {"description": "Enrollment details."},
        404: {"description": "Enrollment not found."},
    },
)
async def get_enrollment(
    enrollment_id: str = Path(..., description="Enrollment ID"),
    auth: Authorized = Depends(with_user)
) -> vr.StudentEnrollment:
    """Get enrollment details by ID"""
    enrollment = (await es.get_enrollment_by_id(enrollment_id, auth.User)).get()
    return vr.StudentEnrollment.of(enrollment)


@router.post(
    "/enroll-by-code",
    status_code=201,
    responses={
        201: {"description": "Successfully enrolled in class."},
        400: {"description": "Invalid request or already enrolled."},
        404: {"description": "Class not found."},
    },
)
async def enroll_by_class_code(
    request: vq.EnrollByClassCodeRequest = Body(...),
    auth: Authorized = Depends(with_user)
) -> vr.StudentEnrollment:
    """Enroll in a class using class code"""
    enrollment = (await es.enroll_by_class_code(
        user=auth.User,
        class_code=request.class_code,
        tuition_fee=request.tuition_fee
    )).get()
    return vr.StudentEnrollment.of(enrollment)


@router.post(
    "/online-enrollment",
    status_code=201,
    responses={
        201: {"description": "Successfully submitted enrollment form."},
        400: {"description": "Invalid request or already enrolled."},
        404: {"description": "Class not found."},
    },
)
async def submit_online_enrollment(
    request: vq.OnlineEnrollmentRequest = Body(...),
    auth: Authorized = Depends(with_user)
) -> vr.StudentEnrollment:
    """Submit online enrollment form"""
    enrollment = (await es.submit_online_enrollment(
        user=auth.User,
        course_class_id=request.course_class_id,
        tuition_fee=request.tuition_fee,
        notes=request.notes
    )).get()
    return vr.StudentEnrollment.of(enrollment) 