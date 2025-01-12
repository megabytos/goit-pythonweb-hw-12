from pydantic import BaseModel, Field, ConfigDict, EmailStr

from src.database.models import UserRole


class User(BaseModel):
    """
    User model for response

    Attributes:
        id (int): ID of the user
        username (str): Username of the user
        email (str): Email of the user
        avatar (str): Avatar of the user
        role (UserRole): Role of the user
    """

    id: int
    username: str
    email: str
    avatar: str
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """
    User model for creating a new user

    Attributes:
        username (str): Username of the user
        email (str): Email of the user
        password (str): Password of the user
        role (UserRole): Role of the user (ENUM: admin, user)
    """

    username: str
    email: EmailStr
    password: str = Field(min_length=4, max_length=128)
    role: UserRole


class Token(BaseModel):
    """
    Token model for response

    Attributes:
        access_token (str): Access token
        token_type (str): Type of the token
    """

    access_token: str
    token_type: str


class RequestEmail(BaseModel):
    """
    Request email model for requesting user activation

    Attributes:
        email (str): Email of the user
    """

    email: EmailStr


class ResetPassword(BaseModel):
    """
    Reset password model for resetting user password

    Attributes:
        email (str): Email of the user
        password (str): Password of the user
    """

    email: EmailStr
    password: str = Field(min_length=4, max_length=128, description="New password")
