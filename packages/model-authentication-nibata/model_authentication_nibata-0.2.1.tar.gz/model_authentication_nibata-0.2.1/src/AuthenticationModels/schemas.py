from sqlmodel import SQLModel, Field
from pydantic import EmailStr


class BaseUser(SQLModel):
    full_name: str = Field(nullable=False, regex="^[a-zA-Z0-9äöüÄÖÜáéíóúÁÉÍÓÚ ]*$")
    email: EmailStr = Field(nullable=False, unique=True)
    is_active: bool = Field(nullable=False, default=False)


class FormDeleteUser(SQLModel):
    email: EmailStr = Field(nullable=False)


class FormUpdateUser(BaseUser):
    pass


class ReadUser(BaseUser):
    pass


class BaseRole(SQLModel):
    name: str = Field(nullable=False, unique=True)
    description: str = Field(nullable=False)


class FormDeleteRole(SQLModel):
    name: str = Field(nullable=False)


class FormUpdateRole(BaseRole):
    pass


class ReadRole(BaseRole):
    pass


class BaseApplication(SQLModel):
    name: str = Field(nullable=False, unique=True)
    description: str = Field(nullable=False)
    url: str = Field(nullable=False, unique=True)

class FormDeleteApplication(SQLModel):
    name: str = Field(nullable=False)


class FormUpdateApplication(BaseApplication):
    pass


class ReadApplication(BaseApplication):
    pass


class BaseEndpoint(SQLModel):
    name: str = Field(nullable=False, unique=True)
    route: str = Field(nullable=False, unique=True)
    description: str = Field(nullable=False)


class FormDeleteEndpoint(SQLModel):
    name: str = Field(nullable=False)


class FormUpdateEndpoint(BaseEndpoint):
    pass


class ReadEndpoint(BaseEndpoint):
    pass
