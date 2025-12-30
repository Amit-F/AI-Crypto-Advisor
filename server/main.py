from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth_routes import router as auth_router
from preferences_routes import router as preferences_router
from me_routes import router as me_router
from votes_routes import router as votes_router
from dev_routes import router as dev_router
from dashboard_routes import router as dashboard_router
from dotenv import load_dotenv
load_dotenv()



app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(auth_router)

app.include_router(preferences_router)

app.include_router(me_router)

app.include_router(votes_router)

app.include_router(dev_router)

app.include_router(dashboard_router)
