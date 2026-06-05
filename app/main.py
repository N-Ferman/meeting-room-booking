from fastapi import FastAPI
from app.routers import auth, rooms

app = FastAPI(title="Meeting Room Booking Service")


@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(auth.router)
app.include_router(rooms.router)