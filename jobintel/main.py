from fastapi import FastAPI

from backend.storage.database import Base
from backend.storage.database import engine

from backend.jobs.models import Job

app = FastAPI(title="JobIntel")


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"status": "JobIntel online"}