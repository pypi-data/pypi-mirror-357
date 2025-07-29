from .schemas import (
    BaseUser,
    BaseRole,
    BaseApplication,
    BaseEndpoint)

from sqlmodel import  Field, Relationship, SQLModel, UniqueConstraint
from typing import List, Optional

from datetime import datetime


"""
Link Tables
"""

class LinkUserRoleTable(SQLModel, table=True):
    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uq_user_role"),
                      {"schema": "authentication"})

    # Fields
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="authentication.users.id")
    role_id: int = Field(foreign_key="authentication.roles.id")


class LinkUserApplicationTable(SQLModel, table=True):
    __tablename__ = "user_application"
    __table_args__ = (UniqueConstraint("user_id", "application_id", name="uq_user_application"),
                      {"schema": "authentication"},)

    # Fields
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="authentication.users.id")
    application_id: int = Field(foreign_key="authentication.applications.id")


class LinkApplicationEndpointTable(SQLModel, table=True):
    __tablename__ = "application_endpoint"
    __table_args__ = (UniqueConstraint("application_id", "endpoint_id", name="uq_application_endpoint"),
                      {"schema": "authentication"},)

    # Fields
    id: int = Field(default=None, primary_key=True)
    application_id: int = Field(foreign_key="authentication.applications.id")
    endpoint_id: int = Field(foreign_key="authentication.endpoints.id")


"""
Tables
"""

class UserTable(BaseUser, table=True):
    __tablename__ = "users"
    __table_args__ = {"schema": "authentication"}

    # Fields
    id: int = Field(nullable=False, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(nullable=True)

    # Relationships
    roles: List["RoleTable"] = Relationship(back_populates="users",
                                            link_model=LinkUserRoleTable)
    applications: List["ApplicationTable"] = Relationship(back_populates="users",
                                                          link_model=LinkUserApplicationTable)


class RoleTable(BaseRole, table=True):
    __tablename__ = "roles"
    __table_args__ = {"schema": "authentication"}

    # Fields
    id: int = Field(nullable=False, primary_key=True)

    # Relationships
    users: List["UserTable"] = Relationship(back_populates="roles",
                                            link_model=LinkUserRoleTable)


class ApplicationTable(BaseApplication, table=True):
    __tablename__ = "applications"
    __table_args__ = {"schema": "authentication"}

    # Fields
    id: int = Field(nullable=False, primary_key=True)

    # Relationships
    users: List["UserTable"] = Relationship(back_populates="applications",
                                            link_model=LinkUserApplicationTable)

    endpoints: List["EndpointTable"] = Relationship(back_populates="applications",
                                                    link_model=LinkUserApplicationTable)


class EndpointTable(BaseEndpoint, table=True):
    __tablename__ = "endpoints"
    __table_args__ = {"schema": "authentication"}

    # Fields
    id: int = Field(nullable=False, primary_key=True)

    # Relationships
    applications: List["ApplicationTable"] = Relationship(back_populates="endpoints", link_model=LinkApplicationEndpointTable)