from pydantic import BaseModel, Field

from app.features import schemas


class User(BaseModel):
    email: str = Field(description="User email", examples=["user@example.com"])


class UserIn(User):
    password: str = Field(description="User password", examples=["userpassword"])


class UserInternal(User):
    user_id: int
    activated: bool
    password: str


class UserCreatedResponse(schemas.Success):
    user_id: int
    message: str = "User successfully created"


class TestUserResponse(schemas.Success):
    message: str = "User successfully validated"
    user_email: str
