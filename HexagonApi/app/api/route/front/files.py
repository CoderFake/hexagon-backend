from typing import Optional, List
import app.service.file as fs
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
    "/course/{course_id}/files",
    responses={
        200: {"description": "List of course files."},
        404: {"description": "Course not found."},
    },
)
async def get_course_files(
    course_id: str = Path(..., description="Course ID"),
    auth: Optional[Authorized] = Depends(maybe_user)
) -> List[vr.CourseFile]:
    """Get all files for a course (both downloadable and non-downloadable)"""
    user = auth.user if auth else None
    files = (await fs.get_course_files(course_id, user)).get()
    return [vr.CourseFile.of(file, user) for file in files]


@router.get(
    "/course/{course_id}/downloadable-files",
    responses={
        200: {"description": "List of downloadable course files."},
        404: {"description": "Course not found."},
    },
)
async def get_downloadable_files(
    course_id: str = Path(..., description="Course ID"),
    auth: Optional[Authorized] = Depends(maybe_user)
) -> List[vr.CourseFile]:
    """Get only downloadable files for a course"""
    user = auth.user if auth else None
    files = (await fs.get_downloadable_files(course_id, user)).get()
    return [vr.CourseFile.of(file, user) for file in files]


@router.get(
    "/{file_id}",
    responses={
        200: {"description": "File details."},
        404: {"description": "File not found."},
    },
)
async def get_file_details(
    file_id: str = Path(..., description="File ID"),
    auth: Optional[Authorized] = Depends(maybe_user)
) -> vr.CourseFile:
    """Get file details"""
    user = auth.user if auth else None
    file = (await fs.get_file_by_id(file_id, user)).get()
    return vr.CourseFile.of(file, user)


@router.post(
    "/{file_id}/download",
    responses={
        200: {"description": "File download URL generated."},
        403: {"description": "Download not allowed."},
        404: {"description": "File not found."},
    },
)
async def download_file(
    file_id: str = Path(..., description="File ID"),
    auth: Optional[Authorized] = Depends(maybe_user)
) -> vr.FileDownloadResponse:
    """Generate download URL for a file"""
    user = auth.user if auth else None
    file, download_url = (await fs.download_file(file_id, user)).get()
    return vr.FileDownloadResponse.of(file, download_url) 