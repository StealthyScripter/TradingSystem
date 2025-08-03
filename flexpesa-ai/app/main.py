from fastapi import FastAPI
from app.core.config import settings
from app.api.router import router

app = FastAPI(title=settings.APP_NAME)

app.include_router(router, prefix="/api")

@app.get("/")
def hello():
    return {"message": f"Hello from {settings.APP_NAME}!"}