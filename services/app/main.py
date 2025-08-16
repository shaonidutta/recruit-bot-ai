from fastapi import FastAPI
from .routes import router

app = FastAPI(title="AI Recruitment Agent - Task Service")

app.include_router(router, prefix="/api", tags=["agents"])

@app.get("/")
async def root():
    return {"message": "Hello Backend Services"}
