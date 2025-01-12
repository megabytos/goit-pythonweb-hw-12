from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.database.models import User
from src.repository.users_repository import UserRepository
from src.schemas.users import UserCreate


class UserService:
    def __init__(self, db: AsyncSession):
        """
        Initializes UserService class.

        Args:
            db (AsyncSession): SQLAlchemy database session.
        """
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate) -> User:
        """
        Create a new user

        Args:
            body (UserCreate): new user data

        Returns:
            User: Newly created user

        Raises:
            ValueError
        """
        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except ValueError as e:
            print(e)

        return await self.repository.create_user(body, avatar)

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Returns a user by ID

        Args:
            user_id (int): ID of the user

        Returns:
            User: User or None if not found
        """
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Returns a user by username

        Args:
            username (str): username of the user

        Returns:
            User: User or None if not found
        """
        return await self.repository.get_user_by_username(username)

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Returns a user by email

        Args:
            email (str): email of the user

        Returns:
            User: User or None if not found
        """
        return await self.repository.get_user_by_email(email)

    async def confirmed_email(self, email: str) -> None:
        """
        Mark an email as confirmed.

        Args:
            email (str): The email to confirm.

        Returns:
            None
        """
        return await self.repository.confirmed_email(email)

    async def update_avatar_url(self, email: str, url: str) -> User:
        """
        Update the avatar URL of a User.

        Args:
            email (str): The email of the User.
            url (str): The new avatar URL.

        Returns:
            A User object with the updated avatar URL.
        """
        return await self.repository.update_avatar_url(email, url)

    async def reset_password(self, user_id: int, password: str) -> User:
        """
        Reset the password of a User.

        Args:
            user_id (int): The id of the User.
            password (str): The new password.

        Returns:
            A User object with the updated password.
        """
        return await self.repository.reset_password(user_id, password)
