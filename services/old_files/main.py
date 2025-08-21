# services/app/main.py

from fastapi import FastAPI
from .routes import router

app = FastAPI(title="AI Recruitment Agent - Task Service")

app.include_router(router, prefix="/api", tags=["agents"])

@app.get("/")
def read_root():
    return {"message": "AI Services are running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

