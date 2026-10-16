from fastapi import FastAPI
from app.routers.incidents import router as incidents_router

app = FastAPI(
    title="SentinelAI API",
    description="AI-powered production incident investigation",
    version="0.1.0",
)

app.include_router(incidents_router)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "sentinel-ai",
    }