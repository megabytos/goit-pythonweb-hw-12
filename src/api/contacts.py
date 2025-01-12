"""
This module provides contacts-related endpoints for contact creation, updating and deletion.

Endpoints:
- GET /api/contacts/birthdays: Gets upcoming birthdays
- GET /api/contacts: Gets all contacts
- POST /api/contacts: Creates a new contact
- GET /api/contacts/{contact_id}: Gets a contact by id
- PUT /api/contacts/{contact_id}: Updates a contact by id
- DELETE /api/contacts/{contact_id}: Deletes a contact by id
"""

from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf import messages
from src.database.db import get_db
from src.schemas.contacts import ContactModel, ContactResponse
from src.schemas.users import User
from src.services.auth_service import get_current_user
from src.services.contacts_service import ContactService

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/birthdays", response_model=list[ContactResponse])
async def get_upcoming_birthdays(
    days: int = Query(default=7, ge=1),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Gets upcoming birthdays
    """
    contact_service = ContactService(db)
    return await contact_service.get_upcoming_birthdays(days, user)


@router.get("/", response_model=List[ContactResponse])
async def get_contacts(
    first_name: str = "",
    last_name: str = "",
    email: str = "",
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Gets all contacts
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(
        first_name, last_name, email, skip, limit, user
    )
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Gets a contact by id
    """
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id, user)
    print(contact)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.CONTACT_NOT_FOUND
        )
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactModel,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Creates a new contact
    """
    contact_service = ContactService(db)
    return await contact_service.create_contact(body, user)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactModel,
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Updates a contact by id
    """
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(contact_id, body, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.CONTACT_NOT_FOUND
        )
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Deletes a contact by id
    """
    contact_service = ContactService(db)
    contact = await contact_service.remove_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.CONTACT_NOT_FOUND
        )
    return contact
