from enum import Enum
from datetime import datetime, date

from sqlalchemy import Integer, String, func, Column, ForeignKey, Enum as SqlEnum
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, relationship
from sqlalchemy.sql.sqltypes import DateTime, Date, Boolean


class Base(DeclarativeBase):
    """
    Base model from declarative base SQLAlchemy
    """

    pass


class UserRole(str, Enum):
    """
    Enum for user roles
    """

    USER = "user"
    ADMIN = "admin"


class Contact(Base):
    """
    Contact model to represent a contact in the database

    Inherits Base (DeclarativeBase): Base model from declarative base SQLAlchemy

    Attributes:
        id (int): The primary key of the contact
        first_name (str): The first name of the contact
        last_name (str): The last name of the contact
        email (str): The email address of the contact
        phone_number (str): The phone number of the contact
        birth_date (date): The birthdate of the contact
        created_at (datetime): The timestamp when the contact was created
        updated_at (datetime): The timestamp when the contact was updated
        user_id (int): The foreign key referencing the user who owns the contact
        user (User): The user who owns the contact
        info (str): Additional information about the contact
    """

    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    birth_date: Mapped[date] = mapped_column("birth_date", Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column("created_at", DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column("updated_at", DateTime, default=func.now(), onupdate=func.now())
    user_id = Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", backref="contacts")
    info: Mapped[str] = mapped_column(String(500), nullable=True)


class User(Base):
    """
    User model to represent users in the database

    Inherits Base (DeclarativeBase): Base model from declarative base SQLAlchemy

    Attributes:
        id (int): The primary key of the user
        username (str): The username of the user
        email (str): The email address of the user
        hashed_password (str): The hashed password of the user
        created_at (datetime): The timestamp when the user was created
        avatar (str): The URL of the user's avatar
        confirmed (bool): Whether the user has confirmed their email
        role (UserRole): The role of the user
    """

    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    role = Column(SqlEnum(UserRole), default=UserRole.USER, nullable=False)
