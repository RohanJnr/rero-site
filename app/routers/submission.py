import logging
import json
import pytz
from datetime import datetime
from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.routing import APIRouter

from google.cloud.firestore_v1.base_query import FieldFilter

from task_manager.tasks import app, start_exec

from app.constants import SUBMISSIONS_PATH, Connections
from app.models import APISubmission, Submission, APIRunSubmission
from app.utils import sanity_check


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/submission"
)


@router.post("/submit")
async def submit(request: Request, sub: APISubmission) -> JSONResponse:
    """Submit code for sanity check and execution."""
    result, message = sanity_check(sub.code)

    if result is False:
        raise HTTPException(status_code=400, detail=message)

    robot = await request.state.db.collection("robots").where(filter=FieldFilter("name", "==", sub.robot)).get()
    robot = robot[0].to_dict()

    if robot["running"]:
        raise HTTPException(status_code=400, detail="Robot is currently busy! Cannot submit now")
    
    team = await request.state.db.collection("teams").where(
            filter=FieldFilter("users", "array_contains", sub.submitted_by_email)
        ).where(
            filter=FieldFilter("robot", "==", sub.robot)
        ).get()
    
    team = team[0].to_dict()
    logger.info(f"Recieved successful submission from team `{team['name']}`, submitted by `{sub.submitted_by}`")
    
    indian_timezone = pytz.timezone('Asia/Kolkata')
    current_datetime = datetime.now(indian_timezone)

    submission = Submission(
        submitted_by=sub.submitted_by,
        submitted_by_email=sub.submitted_by_email,
        code=sub.code,
        robot=sub.robot,
        team=team["name"],
        timestamp=current_datetime
    )

    _, doc = await request.state.db.collection("submissions").add(
        submission.model_dump(exclude={"submission_id"})
    )

    submission.submission_id = doc.id

    submission_path = Path(
        SUBMISSIONS_PATH,
        submission.robot,
        submission.team,
        submission.submission_id,
        f"{submission.submission_id}.py"
    )
    submission_path.parent.mkdir(parents=True, exist_ok=True)
    submission_path.touch(exist_ok=True)

    submission_path.write_text(submission.code)

    return JSONResponse(submission.model_dump_json())


@router.post("/run")
async def run(request: Request, run_sub: APIRunSubmission) -> JSONResponse:
    """Run a particular submission."""
    ref = request.state.db.collection("submissions").document(run_sub.submission_id)

    doc = await ref.get()

    if not doc.exists:
        raise HTTPException(status_code=400, detail="No document found with that ID.")
    
    doc_dict = doc.to_dict()

    submission = Submission(**doc_dict)
    submission.submission_id = doc.id

    submission_path = Path(
        SUBMISSIONS_PATH,
        submission.robot,
        submission.team,
        submission.submission_id,
        f"{submission.submission_id}.py"
    )

    log_path = Path(
        SUBMISSIONS_PATH,
        submission.robot,
        submission.team,
        submission.submission_id,
        f"{submission.submission_id}.log"
    )

    task = start_exec.delay(str(submission_path.absolute()), str(log_path.absolute()))
    print(task.id)
    print(task.get())

    task_data = {
        "task_id": task.id,
        "submission_id": run_sub.submission_id
    }

    await Connections.REDIS.set("current-task", json.dumps(task_data))

    return JSONResponse('{"key": "value"}')


@router.post("/stop")
async def stop(request: Request, stop_sub: APIRunSubmission) -> JSONResponse:
    """Stop a celery task."""

    data = await Connections.REDIS.get("current-task")
    data = json.loads(data.decode())

    task = app.AsyncResult(data["task_id"])
    print(task.id, task.result)

    return JSONResponse('{"key": "value"}')
