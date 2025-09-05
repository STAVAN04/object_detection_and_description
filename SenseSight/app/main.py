import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.controllers import auth_controller, dashboard_controller, detection_data_controller
from app.config.database import Base, engine
from app.utils import logger

app = FastAPI()

app.mount("/static", StaticFiles(directory="./frontend/static"), name="static")

Base.metadata.create_all(bind=engine)

origin = ["http://127.0.0.1:8000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_controller.router, tags=["Authentication"])
app.include_router(dashboard_controller.router, prefix='/dashboard', tags=["Dashboard"])
app.include_router(detection_data_controller.router, prefix='/dashboard', tags=["Detection Data"])

if __name__ == "__main__":
    logger.logger.info("Server Started")
    uvicorn.run("main:app", port=8000, reload=True)
