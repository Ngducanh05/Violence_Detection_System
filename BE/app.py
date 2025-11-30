from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.dashboard import router as dashboard_router
from routes.detect import router as detect_router
from routes.health import router as health_router
from routes.users import router as users_router
from routes.auth import router as auth_router
from routes.projects import router as projects_router
from routes.videos import router as videos_router
from routes.segments import router as segments_router
from routes.annotations import router as annotations_router
from routes.model_runs import router as model_runs_router
from routes.results import router as results_router
from routes.events import router as events_router
from routes.live import router as live_router
from routes.audit import router as audit_router
app = FastAPI(
    title="Violence Detection API",
    version="1.0.0",
    description="Backend API for Video Violence Detection System"
)

# -----------------------------------
# CORS CHO FRONTEND (React)
# -----------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Nếu FE có domain cố định thì thay * bằng domain FE
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------
# ROOT ROUTE — tránh 404
# -----------------------------------
@app.get("/")
def root():
    return {"message": "Violence Detection API is running!"}


# -----------------------------------
# REGISTER ROUTES
# -----------------------------------
app.include_router(health_router)
app.include_router(detect_router)
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(videos_router)
app.include_router(segments_router)
app.include_router(annotations_router)
app.include_router(model_runs_router)
app.include_router(results_router)
app.include_router(events_router)
app.include_router(dashboard_router)
app.include_router(live_router)
app.include_router(audit_router)