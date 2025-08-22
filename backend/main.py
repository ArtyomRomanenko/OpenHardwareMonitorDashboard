from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import metrics, insights, dashboard
from app.core.config import settings

app = FastAPI(
    title="Open Hardware Monitor Dashboard API",
    description="API for analyzing Open Hardware Monitor data with intelligent insights",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["metrics"])
app.include_router(insights.router, prefix="/api/v1/insights", tags=["insights"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])

@app.get("/")
async def root():
    return {"message": "Open Hardware Monitor Dashboard API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
