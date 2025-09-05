from fastapi import Request, APIRouter, Depends, status, Response, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from datetime import datetime

from app.config import database
from app.services.auth_services import AuthServices
from app.schemas import admin_schema
from app.utils import auth_utils, logger

router = APIRouter()
templates = Jinja2Templates(
    directory="./frontend/templates"
)


@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    logger.logger.info("Default accessed")
    return templates.TemplateResponse("index.html", {"request": request})


@router.get('/login', response_class=HTMLResponse)
async def login_page(request: Request):
    logger.logger.info("Login accessed")
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register", response_class=HTMLResponse)
async def registration_page(request: Request):
    logger.logger.info("Registration page accessed")
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/auth/register", status_code=status.HTTP_201_CREATED)
async def user_register(request: admin_schema.CreateAdmin, db: Session = Depends(database.get_db)):
    auth_service = AuthServices(db)
    new_admin = auth_service.register_admin(request)
    logger.logger.info(f"New Admin Created: {new_admin.name}")

    return {"message": "Registration Successful"}


@router.post("/auth/login", status_code=status.HTTP_200_OK)
async def user_login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db),
                     response: Response = None):
    auth_service = AuthServices(db)
    get_admin = auth_service.authenticate_admin(request)
    access_token, expiry = auth_utils.create_access_token(data={"sub": str(get_admin.id)})
    logger.logger.info(f"Fetch Admin: {get_admin.email}")

    token_limit = int((expiry - datetime.utcnow()).total_seconds())
    response.set_cookie(key="access",
                        value=access_token,
                        max_age=token_limit,
                        httponly=True,
                        secure=True,
                        samesite="strict"
                        )

    return {"access": access_token, "token_type": "bearer"}


@router.post("/auth/logout")
async def logout(response: Response):
    response.delete_cookie("access")
    return {"message": "Logout Successful"}


