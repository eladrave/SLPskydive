from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from db.session import init_db, SessionLocal
from db.seed import seed_data
from api import auth, users, availability, sessions, mentee, progression, admin, badges

@asynccontextmanager
async def lifespan(app: FastAPI):
    # on startup
    print("Initializing database...")
    init_db()
    print("Database initialized.")

    # Seed data
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()

    yield
    # on shutdown
    print("Application shutting down.")

app = FastAPI(
    title="Skydiving Mentor–Mentee Scheduler",
    description="A full-stack web app for a skydiving training center.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(availability.router, prefix="/availability", tags=["availability"])
app.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
app.include_router(mentee.router, tags=["mentee_actions"])
app.include_router(progression.progression_router, prefix="/progression", tags=["progression"])
app.include_router(progression.jumps_awards_router, tags=["progression"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(badges.router, tags=["badges"])


@app.get("/")
def read_root():
    return {"message": "Welcome to the Skydiving Scheduler API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
