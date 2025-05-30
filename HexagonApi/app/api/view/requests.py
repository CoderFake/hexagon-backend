import io
import json
from typing import Optional
from decimal import Decimal
from app.api.shared.errors import abort
from app.model.errors import Errors
from fastapi import HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from typing_extensions import Self
from http import HTTPStatus


class UpdateProfileRequest(BaseModel):
    """Update profile request"""
    bio: Optional[str] = None
    address: Optional[str] = None


# ================================================================
# Enrollment Requests
# ================================================================

class EnrollByClassCodeRequest(BaseModel):
    """Enroll by class code request"""
    class_code: str = Field(description="Class code to enroll in")
    tuition_fee: Decimal = Field(description="Tuition fee amount")


class OnlineEnrollmentRequest(BaseModel):
    """Online enrollment form request"""
    course_class_id: str = Field(description="Course class ID")
    tuition_fee: Decimal = Field(description="Tuition fee amount")
    notes: Optional[str] = Field(None, description="Additional notes")


# ================================================================
# Contact Inquiry Requests
# ================================================================

class ContactInquiryRequest(BaseModel):
    """Contact inquiry form request"""
    full_name: str = Field(description="Full name", min_length=2, max_length=255)
    phone: str = Field(description="Phone number", min_length=10, max_length=20)
    email: Optional[str] = Field(None, description="Email address")
    course_id: Optional[str] = Field(None, description="Interested course ID")
    course_class_id: Optional[str] = Field(None, description="Interested course class ID")
    message: Optional[str] = Field(None, description="Additional message", max_length=1000)
    inquiry_type: str = Field(default="course_inquiry", description="Type of inquiry")

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )