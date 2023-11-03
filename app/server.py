import logging
import typing as t

import firebase_admin
from celery.result import AsyncResult
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket
from fastapi.responses import Response
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import credentials, firestore_async
from starlette.middleware import Middleware

from app.routers import submission
from app.constants import Connections
from task_manager.tasks import start_controls

load_dotenv()

SIZE_POOL_AIOHTTP = 100


origins = [
    "*"
]

installed_middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    ),
]

app = FastAPI(
    middleware=installed_middleware,
)

app.include_router(submission.router, prefix="/api")


@app.on_event("startup")
async def startup_event():

    format_string = "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s"
    date_format_string = "%Y-%m-%d %H:%M:%S %z"
    logging.basicConfig(
        format=format_string,
        datefmt=date_format_string,
        level=getattr(logging, "INFO")
    )

    cred = credentials.Certificate("ieee-ras-rero-firebase-adminsdk.json")
    firebase_app = firebase_admin.initialize_app(cred)

    app.state.db = firestore_async.client(firebase_app)

    await Connections.REDIS.ping()


@app.on_event("shutdown")
async def shutdown_event():
    pass


@app.middleware("http")
async def setup_data(request: Request, callnext: t.Callable) -> Response:
    """Get a connection from the pool and a canvas reference for this request."""
    request.state.db = app.state.db
    response = await callnext(request)
    return response


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.websocket("/controls")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    task: AsyncResult = start_controls.delay()
    try:
        while True:
            data = await websocket.receive_text()
            await Connections.REDIS.publish("controls", data)
            await websocket.send_text(f"Message text was: {data}")
    except Exception as e:
        print(f"Got error: {e}")
    finally:
        task.revoke(terminate=True, signal="SIGKILL")