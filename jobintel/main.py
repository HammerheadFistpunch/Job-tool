from fastapi import FastAPI

from backend.storage.database import connect_database, initialize_database

app = FastAPI(title="JobIntel")


@app.on_event("startup")
def startup():
    connection = connect_database()
    try:
        initialize_database(connection)
    finally:
        connection.close()


@app.get("/")
def root():
    return {"status": "JobIntel online"}
