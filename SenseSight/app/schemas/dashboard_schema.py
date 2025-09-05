from pydantic import BaseModel
from typing import Optional


class UpdateProfile(BaseModel):
    name: str
    email: str
    newPassword: Optional[str] = None
