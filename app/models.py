from typing import Optional
from enum import Enum

from pydantic import BaseModel


class StatusEnum(str, Enum):
    """Enum for indicating submissions Status."""
    queued = "queued"
    ready = "ready"
    executing = "executing"
    stopped = "stopped"
    done = "done"


class APISubmission(BaseModel):
    """Submissions receieved at API endpoint."""
    submitted_by: str
    code: str
    robot: str


class Submission(APISubmission):
    """Submissions DB model after processing API Submission."""
    team: str
    submission_id: Optional[str] = None
    datetime_iso: str
    status: StatusEnum = StatusEnum.ready
