from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from .metrics import MetricsMiddleware, active_users, posts_created, likes_total, comments_total, error_count
from .config import settings

app = FastAPI(title="Analytics Service")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add metrics middleware
app.middleware("http")(MetricsMiddleware())

@app.get("/metrics")
async def get_metrics():
    """Endpoint for Prometheus to scrape metrics"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/events/user-activity")
async def track_user_activity(request: Request):
    """Track user activity events"""
    data = await request.json()
    event_type = data.get("event_type")
    
    if event_type == "login":
        active_users.inc()
    elif event_type == "logout":
        active_users.dec()
    
    return {"status": "success"}

@app.post("/events/content")
async def track_content_events(request: Request):
    """Track content-related events"""
    data = await request.json()
    event_type = data.get("event_type")
    content_type = data.get("content_type")
    
    if event_type == "post_created":
        posts_created.labels(post_type=content_type).inc()
    elif event_type == "like":
        likes_total.labels(content_type=content_type).inc()
    elif event_type == "comment":
        comments_total.inc()
    
    return {"status": "success"}

@app.post("/events/error")
async def track_error_events(request: Request):
    """Track error events"""
    data = await request.json()
    service = data.get("service")
    error_type = data.get("error_type")
    
    error_count.labels(service=service, error_type=error_type).inc()
    return {"status": "success"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"} 