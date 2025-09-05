import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.controller import detection_controller

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

templates = Jinja2Templates(directory="../app/templates")
app.mount("/static", StaticFiles(directory="../app/static"), name="static")
app.mount("/output", StaticFiles(directory="./output"), name="output")
app.include_router(detection_controller.detection_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run(app="app.main:app", port=8080, reload=True)
