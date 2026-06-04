from fastapi import FastAPI

app = FastAPI(title="Meeting Room Booking Service")


@app.get("/health")
def health_check():
    return {"status": "ok"}