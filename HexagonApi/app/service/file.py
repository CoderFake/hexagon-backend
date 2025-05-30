from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload, selectinload

import app.model.db as m
import app.model.composite as c
from .commons import service, Maybe, Errors, r


@service
async def get_course_files(
    course_id: str,
    user: Optional[c.User] = None,
    active_only: bool = True
) -> Maybe[List[c.CourseFile]]:
    """Get files for a course"""
    query = select(m.CourseFile).where(
        m.CourseFile.course_id == course_id
    )
    
    if active_only:
        query = query.where(m.CourseFile.is_active == True)
    
    query = query.order_by(m.CourseFile.name)
    
    result = await r.tx.execute(query)
    files = result.scalars().all()
    
    return [c.CourseFile.of(file) for file in files]


@service
async def get_file_by_id(
    file_id: str,
    user: Optional[c.User] = None
) -> Maybe[c.CourseFile]:
    """Get file by ID"""
    query = select(m.CourseFile).options(
        joinedload(m.CourseFile.course)
    ).where(
        and_(
            m.CourseFile.id == file_id,
            m.CourseFile.is_active == True
        )
    )
    
    result = await r.tx.execute(query)
    file = result.scalar_one_or_none()
    
    if not file:
        return Errors.DATA_NOT_FOUND
    
    return c.CourseFile.of(file)


@service
async def download_file(
    file_id: str,
    user: Optional[c.User] = None
) -> Maybe[tuple[c.CourseFile, str]]:
    """Download file and return file info + download URL"""
    file_result = await get_file_by_id(file_id, user)
    if not file_result.get():
        return file_result
    
    file = file_result.get()
    
    if user and file.permission_level == "enrolled":
        user_query = select(m.User).options(
            selectinload(m.User.enrollments)
        ).where(m.User.id == user.id)
        user_result = await r.tx.execute(user_query)
        user_with_enrollments = user_result.scalar_one_or_none()
        if user_with_enrollments:
            user = c.User.of(user_with_enrollments)
    
    if not file.can_download(user):
        return Errors.FORBIDDEN
    
    try:
        download_url = r.storage.urlize(file.file_key)
    except Exception:
        return Errors.INTERNAL_ERROR
    
    file_db = await r.tx.get(m.CourseFile, file_id)
    if file_db:
        file_db.download_count += 1
        await r.tx.commit()
    
    return (file, download_url)


@service
async def get_downloadable_files(
    course_id: str,
    user: Optional[c.User] = None
) -> Maybe[List[c.CourseFile]]:
    """Get only downloadable files for a course"""
    query = select(m.CourseFile).where(
        and_(
            m.CourseFile.course_id == course_id,
            m.CourseFile.is_active == True,
            m.CourseFile.is_downloadable == True
        )
    ).order_by(m.CourseFile.name)
    
    result = await r.tx.execute(query)
    files = result.scalars().all()
    
    return [c.CourseFile.of(file) for file in files] 