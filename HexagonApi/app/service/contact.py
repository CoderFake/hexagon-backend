from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, and_, func
from sqlalchemy.orm import joinedload

import app.model.db as m
import app.model.composite as c
from .commons import service, Maybe, Errors, r
from .email import send_contact_inquiry_notifications


@service
async def submit_contact_inquiry(
    full_name: str,
    phone: str,
    email: Optional[str] = None,
    course_id: Optional[str] = None,
    course_class_id: Optional[str] = None,
    message: Optional[str] = None,
    inquiry_type: str = "course_inquiry"
) -> Maybe[c.ContactInquiry]:
    """Submit a contact inquiry form"""
    
    if course_id:
        course_query = select(m.Course).where(
            and_(
                m.Course.id == course_id,
                m.Course.is_active == True
            )
        )
        course_result = await r.tx.execute(course_query)
        course = course_result.scalar_one_or_none()
        if not course:
            return Errors.DATA_NOT_FOUND
    
    if course_class_id:
        class_query = select(m.CourseClass).where(
            and_(
                m.CourseClass.id == course_class_id,
                m.CourseClass.is_active == True
            )
        )
        class_result = await r.tx.execute(class_query)
        course_class = class_result.scalar_one_or_none()
        if not course_class:
            return Errors.DATA_NOT_FOUND
    
    inquiry = m.ContactInquiry(
        full_name=full_name.strip(),
        phone=phone.strip(),
        email=email.strip() if email else None,
        course_id=course_id,
        course_class_id=course_class_id,
        message=message.strip() if message else None,
        inquiry_type=inquiry_type,
        status="new",
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    r.tx.add(inquiry)
    await r.tx.commit()
    await r.tx.refresh(inquiry)

    if inquiry.course_id:
        await r.tx.refresh(inquiry, ['course'])
    if inquiry.course_class_id:
        await r.tx.refresh(inquiry, ['course_class'])

    inquiry_composite = c.ContactInquiry.of(inquiry)

    try:
        await send_contact_inquiry_notifications(inquiry_composite)
    except Exception as e:
        r.logger.error(f"Failed to send contact inquiry emails: {e}")
    return inquiry_composite


@service
async def get_contact_inquiries(
    status: Optional[str] = None,
    inquiry_type: Optional[str] = None,
    page: int = 1,
    per_page: int = 20
) -> Maybe[tuple[List[c.ContactInquiry], int]]:
    """Get contact inquiries with pagination (admin use)"""
    query = select(m.ContactInquiry).options(
        joinedload(m.ContactInquiry.course),
        joinedload(m.ContactInquiry.course_class)
    ).where(m.ContactInquiry.is_active == True)
    
    if status:
        query = query.where(m.ContactInquiry.status == status)
    
    if inquiry_type:
        query = query.where(m.ContactInquiry.inquiry_type == inquiry_type)
    
    # Count total
    count_query = select(func.count(m.ContactInquiry.id)).where(
        m.ContactInquiry.is_active == True
    )
    if status:
        count_query = count_query.where(m.ContactInquiry.status == status)
    if inquiry_type:
        count_query = count_query.where(m.ContactInquiry.inquiry_type == inquiry_type)
    
    total_result = await r.tx.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    query = query.order_by(m.ContactInquiry.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    
    result = await r.tx.execute(query)
    inquiries = result.scalars().all()
    
    return ([c.ContactInquiry.of(inquiry) for inquiry in inquiries], total)


@service
async def get_contact_inquiry_by_id(inquiry_id: str) -> Maybe[c.ContactInquiry]:
    """Get contact inquiry by ID"""
    query = select(m.ContactInquiry).options(
        joinedload(m.ContactInquiry.course),
        joinedload(m.ContactInquiry.course_class)
    ).where(
        and_(
            m.ContactInquiry.id == inquiry_id,
            m.ContactInquiry.is_active == True
        )
    )
    
    result = await r.tx.execute(query)
    inquiry = result.scalar_one_or_none()
    
    if not inquiry:
        return Errors.DATA_NOT_FOUND
    
    return c.ContactInquiry.of(inquiry) 