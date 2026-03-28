from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None


class UserPublic(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}