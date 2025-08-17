# services/app/main.py

from fastapi import FastAPI
from . import routes

# This creates your main application instance
app = FastAPI(title="AI Recruitment Services")

# This tells your app to use the "menu" you created in routes.py
app.include_router(routes.router, prefix="/api")


@app.get("/")
def read_root():
    return {"message": "AI Services are running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

