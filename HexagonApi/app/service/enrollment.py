from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload, joinedload

import app.model.db as m
import app.model.composite as c
from .commons import service, Maybe, Errors, r
from .email import send_enrollment_notifications


@service
async def get_user_enrollments(
    user: c.User,
    status: Optional[str] = None,
    page: int = 1,
    per_page: int = 20
) -> Maybe[tuple[List[c.StudentEnrollment], int]]:
    """Get user's enrollments with pagination"""
    query = select(m.StudentCourseEnrollment).options(
        joinedload(m.StudentCourseEnrollment.course).joinedload(m.Course.category),
        joinedload(m.StudentCourseEnrollment.course_class)
    ).where(
        and_(
            m.StudentCourseEnrollment.user_id == user.id,
            m.StudentCourseEnrollment.is_active == True
        )
    )
    
    if status:
        query = query.where(m.StudentCourseEnrollment.status == status)
    
    # Count total
    count_query = select(func.count(m.StudentCourseEnrollment.id)).where(
        and_(
            m.StudentCourseEnrollment.user_id == user.id,
            m.StudentCourseEnrollment.is_active == True
        )
    )
    if status:
        count_query = count_query.where(m.StudentCourseEnrollment.status == status)
    
    total_result = await r.tx.execute(count_query)
    total = total_result.scalar()
    
    query = query.order_by(m.StudentCourseEnrollment.enrollment_date.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    
    result = await r.tx.execute(query)
    enrollments = result.scalars().all()
    
    return ([c.StudentEnrollment.of(enrollment) for enrollment in enrollments], total)


@service
async def get_enrollment_by_id(enrollment_id: str, user: c.User) -> Maybe[c.StudentEnrollment]:
    """Get enrollment by ID for specific user"""
    query = select(m.StudentCourseEnrollment).options(
        joinedload(m.StudentCourseEnrollment.course).joinedload(m.Course.category),
        joinedload(m.StudentCourseEnrollment.course_class)
    ).where(
        and_(
            m.StudentCourseEnrollment.id == enrollment_id,
            m.StudentCourseEnrollment.user_id == user.id,
            m.StudentCourseEnrollment.is_active == True
        )
    )
    
    result = await r.tx.execute(query)
    enrollment = result.scalar_one_or_none()
    
    if not enrollment:
        return Errors.DATA_NOT_FOUND
    
    return c.StudentEnrollment.of(enrollment)


@service
async def check_existing_enrollment(user_id: str, course_class_id: str) -> Maybe[bool]:
    """Check if user is already enrolled in a class"""
    query = select(m.StudentCourseEnrollment).where(
        and_(
            m.StudentCourseEnrollment.user_id == user_id,
            m.StudentCourseEnrollment.course_class_id == course_class_id,
            m.StudentCourseEnrollment.is_active == True
        )
    )
    
    result = await r.tx.execute(query)
    enrollment = result.scalar_one_or_none()
    
    return enrollment is not None


@service
async def enroll_by_class_code(
    user: c.User, 
    class_code: str,
    tuition_fee: Decimal
) -> Maybe[c.StudentEnrollment]:
    """Enroll user in a class using class code"""
    class_query = select(m.CourseClass).options(
        joinedload(m.CourseClass.course)
    ).where(
        and_(
            m.CourseClass.class_code == class_code,
            m.CourseClass.is_active == True,
            m.CourseClass.is_open_for_enrollment == True
        )
    )
    
    class_result = await r.tx.execute(class_query)
    course_class = class_result.scalar_one_or_none()
    
    if not course_class:
        return Errors.DATA_NOT_FOUND
    
    existing_check = await check_existing_enrollment(user.id, course_class.id)
    if existing_check.get():
        return Errors.INVALID_REQUEST 
    
    enrolled_count_query = select(func.count(m.StudentCourseEnrollment.id)).where(
        and_(
            m.StudentCourseEnrollment.course_class_id == course_class.id,
            m.StudentCourseEnrollment.is_active == True
        )
    )
    count_result = await r.tx.execute(enrolled_count_query)
    current_count = count_result.scalar()
    
    if current_count >= course_class.max_students:
        return Errors.INVALID_REQUEST 
    
    enrollment = m.StudentCourseEnrollment(
        user_id=user.id,
        course_id=course_class.course_id,
        course_class_id=course_class.id,
        enrollment_date=date.today(),
        enrollment_method=m.EnrollmentMethodEnum.CLASS_CODE,
        status=m.EnrollmentStatusEnum.PENDING,
        tuition_fee=tuition_fee,
        paid_amount=Decimal(0),
        payment_status=m.PaymentStatusEnum.UNPAID,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    r.tx.add(enrollment)
    await r.tx.commit()
    await r.tx.refresh(enrollment)
    
    await r.tx.refresh(enrollment, ['course', 'course_class', 'user'])
    
    # Convert to composite and send emails
    enrollment_composite = c.StudentEnrollment.of(enrollment)
    
    # Send notification emails (admin + student welcome)
    try:
        await send_enrollment_notifications(enrollment_composite)
    except Exception as e:
        print(f"Failed to send enrollment emails: {e}")
        # Don't fail the enrollment if email fails
    
    return enrollment_composite


@service
async def submit_online_enrollment(
    user: c.User,
    course_class_id: str,
    tuition_fee: Decimal,
    notes: Optional[str] = None
) -> Maybe[c.StudentEnrollment]:
    """Submit online enrollment form"""
    class_query = select(m.CourseClass).options(
        joinedload(m.CourseClass.course)
    ).where(
        and_(
            m.CourseClass.id == course_class_id,
            m.CourseClass.is_active == True,
            m.CourseClass.is_open_for_enrollment == True
        )
    )
    
    class_result = await r.tx.execute(class_query)
    course_class = class_result.scalar_one_or_none()
    
    if not course_class:
        return Errors.DATA_NOT_FOUND
    
    existing_check = await check_existing_enrollment(user.id, course_class.id)
    if existing_check.get():
        return Errors.INVALID_REQUEST
    
    enrolled_count_query = select(func.count(m.StudentCourseEnrollment.id)).where(
        and_(
            m.StudentCourseEnrollment.course_class_id == course_class.id,
            m.StudentCourseEnrollment.is_active == True
        )
    )
    count_result = await r.tx.execute(enrolled_count_query)
    current_count = count_result.scalar()
    
    if current_count >= course_class.max_students:
        return Errors.INVALID_REQUEST
    
    enrollment = m.StudentCourseEnrollment(
        user_id=user.id,
        course_id=course_class.course_id,
        course_class_id=course_class.id,
        enrollment_date=date.today(),
        enrollment_method=m.EnrollmentMethodEnum.ONLINE_FORM,
        status=m.EnrollmentStatusEnum.PENDING,
        tuition_fee=tuition_fee,
        paid_amount=Decimal(0),
        payment_status=m.PaymentStatusEnum.UNPAID,
        notes=notes,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    r.tx.add(enrollment)
    await r.tx.commit()
    await r.tx.refresh(enrollment)
    
    await r.tx.refresh(enrollment, ['course', 'course_class', 'user'])
    
    # Convert to composite and send emails
    enrollment_composite = c.StudentEnrollment.of(enrollment)
    
    # Send notification emails (admin + student welcome)
    try:
        await send_enrollment_notifications(enrollment_composite)
    except Exception as e:
        print(f"Failed to send enrollment emails: {e}")
        # Don't fail the enrollment if email fails
    
    return enrollment_composite 