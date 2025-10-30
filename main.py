from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models.database import Base, engine
from app.routes.auth import router as auth_router
from app.routes.resumes import router as resumes_router
from app.routes.job_descriptions import router as jd_router
from app.routes.results import router as results_router


def create_app() -> FastAPI:
    app = FastAPI(title="Resume Screener API", version="0.2.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    Base.metadata.create_all(bind=engine)

    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    app.include_router(resumes_router, tags=["resumes"])
    app.include_router(jd_router, tags=["job_descriptions"])
    app.include_router(results_router, tags=["results"])

    return app


app = create_app() 
@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI application!"}