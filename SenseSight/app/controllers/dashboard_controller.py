from fastapi import Request, APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from app.config import database
from app.services.auth_services import AuthServices
from app.services.dashboard_services import DashboardServices
from app.schemas import dashboard_schema
from app.utils import auth_utils, logger

router = APIRouter()

templates = Jinja2Templates(
    directory="./frontend/templates"
)


@router.get("/home")
async def home_page(request: Request, db: Session = Depends(database.get_db)):
    get_access = await auth_utils.get_current_user(request)
    if get_access is None:
        return RedirectResponse(url="/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    auth_service = AuthServices(db)
    user_data = auth_service.get_admin_by_id(get_access)
    logger.logger.info(f"Admin Accessed Home {user_data.email}")

    return templates.TemplateResponse("dashboard.html", {"request": request,
                                                         "data": {"user_id": user_data.id, "name": user_data.name,
                                                                  "email": user_data.email,
                                                                  "created_at": user_data.created_at
                                                                  }})


@router.get("/profile/edit")
async def edit_profile(request: Request, db: Session = Depends(database.get_db)):
    get_access = await auth_utils.get_current_user(request)
    if get_access is None:
        return RedirectResponse(url="/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    auth_service = AuthServices(db)
    user_data = auth_service.get_admin_by_id(get_access)
    logger.logger.info(f"Admin Accessed Profile Edit {user_data.email}")

    return templates.TemplateResponse("editProfile.html", {"request": request,
                                                           "data": {"user_id": user_data.id, "name": user_data.name,
                                                                    "email": user_data.email
                                                                    }})


@router.put("/profile/edit/{user_id}")
async def update_profile(user_id: int, request: dashboard_schema.UpdateProfile, db: Session = Depends(database.get_db)):
    print()
    dashboard_service = DashboardServices(db)
    get_admin = dashboard_service.admin_update_profile(user_id, request)
    logger.logger.info(f"User updated profile: {get_admin.name}, {get_admin.email}")

    return {"Profile Updated"}

@router.get("/aboutus")
async def about_us(request: Request, db: Session = Depends(database.get_db)):
    get_access = await auth_utils.get_current_user(request)
    if get_access is None:
        return RedirectResponse(url="/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    auth_service = AuthServices(db)
    user_data = auth_service.get_admin_by_id(get_access)
    logger.logger.info(f"Admin Accessed About Us {user_data.email}")

    return templates.TemplateResponse("about.html", {"request": request,
                                                         "data": {"user_id": user_data.id, "name": user_data.name,
                                                                  "email": user_data.email,
                                                                  "created_at": user_data.created_at
                                                                  }})
