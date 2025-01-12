from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr


class ContactModel(BaseModel):
    """
    Contact model for creating and updating contacts

    Attributes:
        first_name (str): First name of the contact
        last_name (str): Last name of the contact
        email (str): Email of the contact
        phone_number (str): Phone number of the contact
        birth_date (date): Birth date of the contact
        info (str): Additional information about the contact
    """

    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    email: EmailStr = Field(min_length=7, max_length=100)
    phone_number: str = Field(min_length=7, max_length=20)
    birth_date: date | None = Field(None, description='Date of birth (YYYY-MM-DD)')
    info: Optional[str] = None


class ContactResponse(ContactModel):
    """
    Contact model for response extends ContactModel

    Attributes:
        id (int): ID of the contact
        created_at (datetime): Creation date of the contact
        updated_at (datetime): Last update date of the contact
    """

    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)