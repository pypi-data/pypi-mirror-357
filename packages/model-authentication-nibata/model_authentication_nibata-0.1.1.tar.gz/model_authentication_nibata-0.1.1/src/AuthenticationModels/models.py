from .schemas import BaseUser, Field


class UserTable(BaseUser, table=True):
    __tablename__ = "users"
    __table_args__ = {"schema": "authentication"}

    # Fields
    id: int = Field(nullable=False, primary_key=True)