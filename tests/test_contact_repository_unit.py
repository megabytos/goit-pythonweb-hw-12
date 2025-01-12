import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.repository.contacts_repository import ContactRepository
from src.schemas.contacts import ContactModel


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def contact_repository(mock_session):
    return ContactRepository(mock_session)


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


@pytest.mark.asyncio
async def test_get_contacts(contact_repository, mock_session, user, contact):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [contact]
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    contacts = await contact_repository.get_contacts(
        skip=0,
        limit=10,
        user=user,
        first_name="",
        last_name="",
        email="",
    )

    # Assertions
    assert len(contacts) == 1
    assert contacts[0].first_name == "Bob"


@pytest.mark.asyncio
async def test_get_contact_by_id(contact_repository, mock_session, user, contact):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    contact_record = await contact_repository.get_contact_by_id(contact_id=1, user=user)

    # Assertions
    assert contact_record is not None
    assert contact_record.id == 1
    assert contact_record.first_name == "Bob"


@pytest.mark.asyncio
async def test_create_contact_successful(
    contact_repository, mock_session, user, contact_body
):
    # Setup
    # Call method
    result = await contact_repository.create_contact(body=contact_body, user=user)

    # Assertions
    assert isinstance(result, Contact)
    assert result.first_name == "Bob"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_create_contact_failure(
    contact_repository, mock_session, user, contact_body
):
    # Setup
    # Call method
    result = await contact_repository.create_contact(body=contact_body, user=user)

    # Assertions
    assert isinstance(result, Contact)
    assert result.first_name != "Bob2"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_update_contact(contact_repository, mock_session, user, contact):
    # Setup
    contact_data = ContactModel(**contact.__dict__)
    contact_data.first_name = "Bob2"
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.update_contact(
        contact_id=1, body=contact_data, user=user
    )

    # Assertions
    assert result is not None
    assert result.first_name == "Bob2"
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(contact)


@pytest.mark.asyncio
async def test_remove_contact(contact_repository, mock_session, user, contact):
    # Setup
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.remove_contact(contact_id=1, user=user)

    # Assertions
    assert result is not None
    assert result.first_name == "Bob"
    mock_session.delete.assert_awaited_once_with(contact)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_is_contact_exists_success(
    contact_repository, mock_session, user, contact
):
    # Setup
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    is_contact_exist = await contact_repository.is_contact_exists(
        "aassdd@example.com", "111-11-11", user=user
    )

    # Assertions
    assert is_contact_exist is True


@pytest.mark.asyncio
async def test_is_contact_exists_failure(
    contact_repository, mock_session, user, contact_none
):
    # Setup
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = contact_none
    mock_session.execute = AsyncMock(return_value=mock_result)

    is_contact_exist = await contact_repository.is_contact_exists(
        "aassdd@example.com", "111-11-11", user=user
    )

    # Assertions
    assert is_contact_exist is False
