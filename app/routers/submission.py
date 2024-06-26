import logging
import json
import pytz
from datetime import datetime
from pathlib import Path

from celery.result import AsyncResult
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.routing import APIRouter

from google.cloud.firestore_v1.base_query import FieldFilter

from task_manager.tasks import app, start_exec

from app.constants import SUBMISSIONS_PATH, Connections, CELERY_SUBMISSIONS_PATH
from app.models import APISubmission, Submission, APIRunSubmission, APITaskFinished
from app.utils import sanity_check, write_to_path


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

    write_to_path(submission_path, submission.code)

    return JSONResponse(submission.model_dump_json())


@router.post("/run")
async def run(request: Request, run_sub: APIRunSubmission) -> JSONResponse:
    """Run a particular submission."""

    robot = await request.state.db.collection("robots").where(filter=FieldFilter("name", "==", "ESPLF")).get()
    robot = robot[0].to_dict()

    if run_sub.user_email not in robot["codeAccess"]:
        return JSONResponse({"detail": "Not permitted to run."}, status_code=400)

    ref = request.state.db.collection("submissions").document(run_sub.submission_id)

    doc = await ref.get()

    if not doc.exists:
        raise HTTPException(status_code=400, detail="No document found with that ID.")
    
    doc_dict = doc.to_dict()

    submission = Submission(**doc_dict)
    submission.submission_id = doc.id

    submission_path = Path(
        CELERY_SUBMISSIONS_PATH,
        submission.robot,
        submission.team,
        submission.submission_id,
        f"{submission.submission_id}.py"
    )

    log_path = Path(
        CELERY_SUBMISSIONS_PATH,
        submission.robot,
        submission.team,
        submission.submission_id,
        f"{submission.submission_id}.log"
    )


    task = start_exec.delay(
        code=submission.code,
        module_path=str(submission_path),
        log_path=str(log_path),
        metadata={"submission_id": submission.submission_id}
    )

    print(task.id)

    task_data = {
        "task_id": task.id,
        "submission_id": run_sub.submission_id
    }

    await Connections.REDIS.set("current-task", json.dumps(task_data))

    return JSONResponse(content=task_data, status_code=200)


@router.post("/stop")
async def stop(request: Request, data: APIRunSubmission) -> JSONResponse:
    """Stop a celery task."""

    robot = await request.state.db.collection("robots").where(filter=FieldFilter("name", "==", "ESPLF")).get()
    robot = robot[0].to_dict()

    if data.user_email not in robot["codeAccess"]:
        return JSONResponse({"detail": "Not permitted to run."}, status_code=400)
    

    data = await Connections.REDIS.get("current-task")
    if not data:
        return JSONResponse(content={}, status_code=200)
    data = json.loads(data.decode())

    task: AsyncResult = app.AsyncResult(data["task_id"])
    task.revoke(terminate=True)
    print("DONE")
    data = {
        "task_id": task.id  
    }

    await Connections.REDIS.delete("current-task")

    return JSONResponse(content=data, status_code=200)


@router.post("/task_finished")
async def task_finished(request: Request, data: APITaskFinished) -> JSONResponse:
    """Handle task finish state."""
    ref = request.state.db.collection("submissions").document(data.submission_id)
    await ref.update({"logs": data.logs})

    store_data = await Connections.REDIS.get("current-task")
    if store_data:
        store_data = json.loads(store_data.decode())

        if store_data["submission_id"] == data.submission_id:
            await Connections.REDIS.delete("current-task")

    return JSONResponse('{"key": "value"}')


@router.get("/task_status")
async def task_status(request: Request) -> JSONResponse:
    """Check task status."""

    data = await Connections.REDIS.get("current-task")
    if not data:
        return JSONResponse({
            "status": "Bot is currently not running any task"
        })

    data = json.loads(data.decode())
    return JSONResponse({
        "status": f"Task Running with id: {data['submission_id']}"
    })
