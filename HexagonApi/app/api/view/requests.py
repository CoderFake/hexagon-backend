import io
import json
from typing import Optional

from app.api.shared.errors import abort
from app.job.models import Applicant, ApplyJobData, JobQueryParams
from app.model.errors import Errors
from app.pdf.models import ResumeData
from fastapi import HTTPException, Request
from multipart import MultipartParser, parse_options_header
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from typing_extensions import Self
from http import HTTPStatus