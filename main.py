from fastapi import FastAPI

app = FastAPI(title="JobIntel")


@app.get("/")
def root():
    return {"status": "JobIntel online"}
