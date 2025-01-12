import asyncio
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from main import app
from src.database.models import Base, User, Contact
from src.database.db import get_db
from src.schemas.contacts import ContactModel
from src.services.auth_service import create_access_token, Hash

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
)

test_user = {
    "username": "deadpool",
    "email": "deadpool@example.com",
    "password": "12345678",
    "role": "user",
}

user_data = {
    "username": "agent007",
    "email": "agent007@gmail.com",
    "password": "12345678",
    "role": "user",
}

user_data_unique_email = {
    "username": "agent007",
    "email": "agent008@gmail.com",
    "password": "12345678",
    "role": "user",
}

user_data_unique = {
    "username": "agent008",
    "email": "agent008@gmail.com",
    "password": "12345678",
    "role": "user",
}


@pytest.fixture
def user():
    return User(id=1, username="testuser", role="user")


@pytest.fixture
def contact(user: User):
    return Contact(
        id=1,
        first_name="Bob",
        last_name="Smith",
        email="bD8Hj@example.com",
        phone_number="123-456-7890",
        birth_date="1990-01-01",
        user=user,
    )


@pytest.fixture
def contact_none():
    return None


@pytest.fixture
def contact_body():
    return ContactModel(
        first_name="Bob",
        last_name="Smith",
        email="bD8Hj@example.com",
        phone_number="123-456-7890",
        birth_date="1990-01-01",
    )


@pytest.fixture(scope="module", autouse=True)
def init_models_wrap():
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal() as session:
            hash_password = Hash().get_password_hash(test_user["password"])
            current_user = User(
                username=test_user["username"],
                email=test_user["email"],
                hashed_password=hash_password,
                confirmed=True,
                avatar="https://twitter.com/gravatar.jpg",
                role=test_user["role"],
            )
            session.add(current_user)
            await session.commit()
            await session.refresh(current_user)
            test_user["id"] = current_user.id

    asyncio.run(init_models())


@pytest.fixture(scope="module")
def client():
    # Dependency override

    async def override_get_db():
        async with TestingSessionLocal() as session:
            try:
                yield session
            except Exception as err:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest.fixture
def auth_headers():
    """
    Fixture for auth headers
    """
    token = "test_token"
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def fake_upload_file():
    """
    Fixture for a mock file upload.
    """
    mock_file = MagicMock()
    mock_file.file = MagicMock()
    mock_file.filename = "avatar.png"
    return mock_file


@pytest.fixture(scope="module")
def event_loop():
    """
    Використовуйте модульну область видимості для event_loop.
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture()
async def get_token():
    token = await create_access_token(data={"sub": test_user["username"]})
    return token
