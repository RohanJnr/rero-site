import logging
import pytz
from datetime import datetime
from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import Response
from fastapi.requests import Request
from fastapi.routing import APIRouter

from google.cloud.firestore_v1.base_query import FieldFilter

from app.models import APISubmission, Submission
from app.utils import sanity_check


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/submission"
)


@router.post("/submit")
async def submit(request: Request, sub: APISubmission) -> Response:
    """Submit code for sanity check and execution."""
    result, message = sanity_check(sub.code)

    if result is False:
        raise HTTPException(status_code=400, detail=message)

    robot = await request.state.db.collection("robots").where(filter=FieldFilter("name", "==", sub.robot)).get()
    robot = robot[0]


    if robot["running"]:
        raise HTTPException(status_code=400, detail="Robot is currently busy! Cannot submit now")
    

    team = await request.state.db.collection("teams").where(
            filter=FieldFilter("users", "array_contains", sub.submitted_by)
        ).where(
            filter=FieldFilter("robot", "==", sub.robot)
        ).get()
    
    team = team[0].to_dict()
    logger.info(f"Recieved successful submission from team `{team['name']}`, submitted by `{sub.submitted_by}`")
    
    indian_timezone = pytz.timezone('Asia/Kolkata')
    current_datetime = datetime.now(indian_timezone)


    submission = Submission(
        submitted_by=sub.submitted_by,
        code=sub.code,
        robot=sub.robot,
        team=team["name"],
        datetime_iso=current_datetime.isoformat()
    )


@router.post("/run")
async def run(request: Request, submission_id: str) -> None:
    """Run a particular submission."""
    print(f"Submission ID: {submission_id}")
    ref = request.state.db.collection("submissions").document(submission_id)

    doc = await ref.get()

    if doc.exists:
        print(f"Document data: {doc.to_dict()}")
    else:
        print("No such document!")

    return "good"
