from sqlmodel import SQLModel, Field
from pydantic import EmailStr


class BaseUser(SQLModel):
    full_name: str = Field(nullable=False, regex="^[a-zA-Z0-9äöüÄÖÜáéíóúÁÉÍÓÚ ]*$")
    email: EmailStr = Field(nullable=False, unique=True)
    is_active: bool = Field(nullable=False, default=False)
