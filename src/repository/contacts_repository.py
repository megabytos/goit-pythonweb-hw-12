from datetime import date, timedelta
from typing import List

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas.contacts import ContactModel


class ContactRepository:
    """
    A repository class for Contacts.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize a ContactRepository.

        Args:
            session (AsyncSession): An AsyncSession object connected to the database.
        """
        self.db = session

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
        Get a list of Contacts owned by `user` with pagination.

        Args:
            first_name (str): The first name of the Contacts to retrieve.
            last_name (str): The last name of the Contacts to retrieve.
            email (str): The email of the Contacts to retrieve.
            skip (int): The number of Notes to skip.
            limit (int): The maximum number of Notes to return.
            user (User): The owner of the Notes to retrieve.

        Returns:
            A list of Contacts.
        """
        stmt = (
            select(Contact)
            .filter_by(user=user)
            .where(Contact.first_name.contains(first_name))
            .where(Contact.last_name.contains(last_name))
            .where(Contact.email.contains(email))
            .offset(skip)
            .limit(limit)
        )
        contacts = await self.db.execute(stmt)
        return list(contacts.scalars().all())

    async def get_contact_by_id(self, contact_id: int, user: User) -> Contact | None:
        """
        Get a Contact by its id.

        Args:
            contact_id (int): The id of the Note to retrieve.
            user (User): The owner of the Contact to retrieve.

        Returns:
            The Contact with the specified id, or None if no such Contact exists.
        """
        stmt = select(Contact).filter_by(id=contact_id, user=user)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactModel, user: User) -> Contact:
        """
        Create a new Contact with the given attributes.

        Args:
            body (ContactModel): A ContactModel with the attributes to assign to the Contact.
            user (User): The User who owns the Contact.

        Returns:
            A Contact with the assigned attributes.
        """
        contact = Contact(**body.model_dump(exclude_unset=True), user=user)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactModel, user: User
    ) -> Contact | None:
        """
        Update a Contact with the given attributes.

        Args:
            contact_id (int): The id of the Contact to update.
            body (ContactModel): A ContactModel with the attributes to assign to the Contact.
            user (User): The User who owns the Contact.

        Returns:
            The updated Contact, or None if no Contact with the given id exists.
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            for key, value in body.dict(exclude_unset=True).items():
                setattr(contact, key, value)
            await self.db.commit()
            await self.db.refresh(contact)
        return contact

    async def remove_contact(self, contact_id: int, user: User) -> Contact | None:
        """
        Delete a Contact by its id.

        Args:
            contact_id (int): The id of the Contact to delete.
            user (User): The owner of the Contact to delete.

        Returns:
            The deleted Contact, or None if no Contact with the given id exists.
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def is_contact_exists(self, email: str, phone_number: str, user: User) -> bool:
        """
        Check if a Contact with the given email or phone number exists.

        Args:
            email (str): The email of the Contact to check.
            phone_number (str): The phone number of the Contact to check.
            user (User): The owner of the Contact to check.

        Returns:
            True if the Contact exists, False otherwise.
        """
        stmt = select(Contact).where(or_(Contact.email == email, Contact.phone_number == phone_number))
        result = await self.db.execute(stmt)
        return result.scalars().first() is not None

    async def get_upcoming_birthdays(self, days: int, user: User) -> list[Contact]:
        """
        Get a list of Contacts with upcoming birthdays.

        Args:
            days (int): The number of days in the future to check.
            user (User): The owner of the Contacts to check.

        Returns:
            A list of Contacts with upcoming birthdays.
        """
        today = date.today()
        upcoming_date = today + timedelta(days=days)
        stmt = select(Contact).where(
            Contact.birth_date.is_not(None),
            Contact.birth_date >= today,
            Contact.birth_date <= upcoming_date
        ).order_by(Contact.birth_date.asc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
