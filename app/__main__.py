import uvicorn


if __name__ == "__main__":
    uvicorn.run("app.server:app", reload=True, host="0.0.0.0")
