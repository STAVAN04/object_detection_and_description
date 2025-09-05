from pydantic import BaseModel
# from typing import Optional


class TokenSchema(BaseModel):
    user_id: int
    access_token: str
    token_type: str


class CreateAdmin(BaseModel):
    name: str
    email: str
    password: str


class NewGetPassword(BaseModel):
    newPassword: str
