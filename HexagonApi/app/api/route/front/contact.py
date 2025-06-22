from typing import Optional, List
import app.service.contact as cs
from app.api.commons import (
    APIRouter,
    Depends,
    Query,
    Path,
    Body,
    Response,
    vr,
    vq,
)

router = APIRouter()


@router.post(
    "/course-inquiry",
    status_code=201,
    responses={
        201: {"description": "Course inquiry submitted successfully."},
        400: {"description": "Invalid request data."},
        404: {"description": "Course not found."},
    },
)
async def submit_course_inquiry(
    course_id: str = Body(..., description="Course ID"),
    full_name: str = Body(..., description="Full name"),
    phone: str = Body(..., description="Phone number"),
    email: Optional[str] = Body(None, description="Email address"),
    message: Optional[str] = Body(None, description="Additional message")
) -> vr.ContactInquiryResponse:
    """Quick course inquiry form - simplified version"""
    inquiry = (await cs.submit_contact_inquiry(
        full_name=full_name,
        phone=phone,
        email=email,
        course_id=course_id,
        message=message,
        inquiry_type="course_inquiry"
    )).get()
    
    return vr.ContactInquiryResponse.success_response(inquiry.id) 