from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas.users import UserCreate


class UserRepository:
    def __init__(self, session: AsyncSession):
        """
        Initialize a UserRepository.

        Args:
            session (AsyncSession): An AsyncSession object connected to the database.
        """
        self.db = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Get a User by its id.

        Args:
            user_id (int): The id of the User to retrieve.

        Returns:
            A User object if found, otherwise None.
        """
        stmt = select(User).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Get a User by its username.

        Args:
            username (str): The username of the User to retrieve.

        Returns:
            A User object if found, otherwise None.
        """
        stmt = select(User).filter_by(username=username)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Get a User by its email.

        Args:
            email (str): The email of the User to retrieve.

        Returns:
            A User object if found, otherwise None.
        """
        stmt = select(User).filter_by(email=email)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def create_user(self, body: UserCreate, avatar: str = None) -> User:
        """
        Create a new User.

        Args:
            body (UserCreate): The data for the new User.
            avatar (str, optional): The avatar URL for the new User.

        Returns:
            A User object.
        """
        user = User(
            **body.model_dump(exclude_unset=True, exclude={"password"}),
            hashed_password=body.password,
            avatar=avatar
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def confirmed_email(self, email: str) -> None:
        """
        Mark an email as confirmed.

        Args:
            email (str): The email to confirm.

        Returns:
            None.
        """
        user = await self.get_user_by_email(email)
        user.confirmed = True
        await self.db.commit()

    async def update_avatar_url(self, email: str, url: str) -> User:
        """
        Update the avatar URL of a User.

        Args:
            email (str): The email of the User.
            url (str): The new avatar URL.

        Returns:
            A User object with the updated avatar URL.
        """
        user = await self.get_user_by_email(email)
        user.avatar = url
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def reset_password(self, user_id: int, password: str) -> User:
        """
        Reset the password of a User.

        Args:
            user_id (int): The id of the User.
            password (str): The new password.

        Returns:
            A User object with the updated password.
        """
        user = await self.get_user_by_id(user_id)
        if user:
            user.hashed_password = password
            await self.db.commit()
            await self.db.refresh(user)

        return user
