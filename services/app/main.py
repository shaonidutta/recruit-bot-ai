from fastapi import FastAPI

app = FastAPI(title="AI Recruitment Agent - Task Service")

@app.get("/")
async def root():
    return {"message": "Hello Backend Services"}
