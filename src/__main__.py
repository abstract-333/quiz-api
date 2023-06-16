import uvicorn

uvicorn.run("src.app:app", log_level="info", host="127.0.0.1")
