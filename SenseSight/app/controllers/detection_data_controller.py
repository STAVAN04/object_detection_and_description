from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import database
from app.utils import auth_utils
from app.services.auth_services import AuthServices
from app.services.detection_data_services import DataFetchStoreHistoryService

router = APIRouter()
templates = Jinja2Templates(directory="./frontend/templates")

@router.get("/get_object_count")
async def get_object_count():
    sample_detection = {
        "object_count": {
            "person": 5,
            "car": 2,
            "pedestrian": 1
        }
    }
    return sample_detection


@router.post("/store_detection")
async def store_detection(request: Request, db: Session = Depends(database.get_db)):
    try:
        user = await auth_utils.get_current_user(request)
        if not user:
            raise HTTPException(status_code=401, detail="Unauthorized")
        service = DataFetchStoreHistoryService(db)
        json_data = await request.json()
        # print(json_data)
        detection = service.store_detection_data(user, json_data)
        return {"status": "success", "detection_id": detection.detection_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def history_page(request: Request, db: Session = Depends(database.get_db)):
    user = await auth_utils.get_current_user(request)
    if not user:
        return RedirectResponse(url="/login")

    service = DataFetchStoreHistoryService(db)
    object_counts = service.fetch_detection_history(user)

    object_names = list(object_counts.keys())
    object_values = list(object_counts.values())

    auth_service = AuthServices(db)
    user_data = auth_service.get_admin_by_id(user)

    return templates.TemplateResponse("history.html", {
        "request": request,
        "object_names": object_names,
        "object_values": object_values,
        "data": {"user_id": user_data.id, "name": user_data.name,
                 "email": user_data.email,
                 "created_at": user_data.created_at
                 }})
