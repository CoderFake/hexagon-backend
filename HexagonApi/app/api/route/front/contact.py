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
    "/inquiry",
    status_code=201,
    responses={
        201: {"description": "Contact inquiry submitted successfully."},
        400: {"description": "Invalid request data."},
        404: {"description": "Course not found."},
    },
)
async def submit_contact_inquiry(
    request: vq.ContactInquiryRequest = Body(...),
) -> vr.ContactInquiryResponse:
    """Submit contact inquiry form"""
    inquiry = (await cs.submit_contact_inquiry(
        full_name=request.full_name,
        phone=request.phone,
        email=request.email,
        course_id=request.course_id,
        course_class_id=request.course_class_id,
        message=request.message,
        inquiry_type=request.inquiry_type
    )).get()
    
    return vr.ContactInquiryResponse.success_response(inquiry.id) 