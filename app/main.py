from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.routers import auth, bookings, rooms

app = FastAPI(title="Meeting Room Booking Service")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def frontend():
    return FileResponse("app/static/index.html")


app.include_router(auth.router)
app.include_router(rooms.router)
app.include_router(bookings.router)
