from typing import List

from fastapi import HTTPException, status
from fastapi.openapi.models import Contact
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.repository.contacts_repository import ContactRepository
from src.schemas.contacts import ContactModel


class ContactService:
    def __init__(self, db: AsyncSession):
        """
        Initializes ContactService class.

        Args:
            db (AsyncSession): SQLAlchemy database session.
        """
        self.repository = ContactRepository(db)

    async def create_contact(self, body: ContactModel, user: User) -> Contact:
        """
        Creates a new contact.

        Args:
            body (ContactModel): Contact data.
            user (User): User who owns the contact.

        Returns:
            Contact: Newly created contact.

        Raises:
            HTTPException: If contact with the same email or phone number already exists.
        """
        if await self.repository.is_contact_exists(body.email, body.phone_number, user):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Contact with '{body.email}' email or '{body.phone_number}' phone number already exists.",
            )
        return await self.repository.create_contact(body, user)

    async def get_contacts(
        self,
        first_name: str,
        last_name: str,
        email: str,
        skip: int,
        limit: int,
        user: User,
    ) -> List[Contact]:
        """
        Returns a list of contacts.

        Args:
            first_name (str): First name of the contact.
            last_name (str): Last name of the contact.
            email (str): Email of the contact.
            skip (int): Number of contacts to skip.
            limit (int): Maximum number of contacts to return.
            user (User): User who owns the contacts.

        Returns:
            List[Contact]: List of contacts.
        """
        return await self.repository.get_contacts(
            first_name, last_name, email, skip, limit, user
        )

    async def get_contact(self, contact_id: int, user: User) -> Contact | None:
        """
        Returns a contact.

        Args:
            contact_id (int): ID of the contact.
            user (User): User who owns the contact.

        Returns:
            Contact | None: Contact or None if not found.
        """
        return await self.repository.get_contact_by_id(contact_id, user)

    async def update_contact(
        self, contact_id: int, body: ContactModel, user: User
    ) -> Contact:
        """
        Updates a contact.

        Args:
            contact_id (int): ID of the contact.
            body (ContactModel): Contact data.
            user (User): User who owns the contact.

        Returns:
            Contact: Updated contact.
        """
        return await self.repository.update_contact(contact_id, body, user)

    async def remove_contact(self, contact_id: int, user: User) -> Contact:
        """
        Removes a contact.

        Args:
            contact_id (int): ID of the contact.
            user (User): User who owns the contact.

        Returns:
            Contact: Removed contact.
        """
        return await self.repository.remove_contact(contact_id, user)

    async def get_upcoming_birthdays(self, days: int, user: User) -> List[Contact]:
        """
        Returns a list of upcoming birthdays.

        Args:
            days (int): Number of days in the future.
            user (User): User who owns the contacts.

        Returns:
            List[Contact]: List of upcoming birthdays.
        """
        return await self.repository.get_upcoming_birthdays(days, user)
