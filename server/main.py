from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from auth_routes import router as auth_router
from preferences_routes import router as preferences_router
from me_routes import router as me_router
from votes_routes import router as votes_router
from dev_routes import router as dev_router
from dashboard_routes import router as dashboard_router

# Load environment variables (.env locally, Render env vars in prod)
load_dotenv()

app = FastAPI(title="AI Crypto Advisor API")

# ---------------------------------------------------------
# CORS CONFIG
# ---------------------------------------------------------
# Expected format (comma-separated):
# CORS_ORIGINS=http://localhost:5173,https://your-app.vercel.app
cors_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
)

allowed_origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# HEALTH & ROOT
# ---------------------------------------------------------
@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Backend is running. See /docs for API.",
    }

@app.get("/health")
def health():
    return {"status": "ok"}

# ---------------------------------------------------------
# ROUTERS
# ---------------------------------------------------------
app.include_router(auth_router)
app.include_router(preferences_router)
app.include_router(me_router)
app.include_router(votes_router)
app.include_router(dev_router)
app.include_router(dashboard_router)
