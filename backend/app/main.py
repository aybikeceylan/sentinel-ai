from fastapi import FastAPI
from routers import incidents

app = FastAPI(
    title="SentinelAI API",
    description="AI-powered production incident investigation",
    version="0.1.0",
)

app.include_router(incidents.router)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "sentinel-ai",
    }