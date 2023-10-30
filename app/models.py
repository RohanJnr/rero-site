import typing as t
from enum import Enum
from datetime import datetime

from pydantic import BaseModel, Field


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
    submitted_by_email: str
    code: str
    robot: str


class Submission(APISubmission):
    """Submissions DB model after processing API Submission."""
    team: str
    submission_id: t.Optional[str] = None
    timestamp: datetime
    status: StatusEnum = StatusEnum.ready


class APIRunSubmission(BaseModel):
    """Submission to run received by API."""
    submission_id: str
    user_email: str


class APITaskFinished(BaseModel):
    """Task finished data received by webhook."""
    submission_id: str
    task_id: str
    log_path: str
    logs: str