import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException, status
from src.conf import messages
from src.schemas.contacts import ContactModel

user_data = {
    "id": 1,
    "username": "agent007",
    "email": "agent007@gmail.com",
    "password": "12345678",
    "role": "user",
    "confirmed": True,
}

contacts = [
    {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "birth_date": "1990-12-15",
        "email": "john.doe@example.com",
        "phone_number": "123-456-7890",
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00",
        "info": "This is a test contact.",
    },
    {
        "id": 2,
        "first_name": "Jane",
        "last_name": "Doe",
        "birth_date": "1995-12-20",
        "email": "jane.doe@example.com",
        "phone_number": "987-654-3210",
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00",
        "info": None,
    },
]

payload = {
    "first_name": "John",
    "last_name": "Doe",
    "birth_date": "1990-12-15",
    "email": "john.doe@example.com",
    "phone_number": "123-456-7890",
}


@pytest.mark.asyncio
async def test_get_upcoming_birthdays(client, monkeypatch, auth_headers):
    # Mock jwt.decode to bypass token validation
    mock_jwt_decode = MagicMock(return_value={"sub": user_data["username"]})
    monkeypatch.setattr("src.services.auth_service.jwt.decode", mock_jwt_decode)

    # Mock get_user_from_db to return a test user
    mock_get_user_from_db = AsyncMock(return_value=user_data)
    monkeypatch.setattr(
        "src.services.auth_service.get_user_from_db", mock_get_user_from_db
    )

    # Mock ContactService to return contacts with upcoming birthdays
    mock_get_upcoming_birthdays = AsyncMock(return_value=contacts)
    monkeypatch.setattr(
        "src.services.contacts_service.ContactService.get_upcoming_birthdays",
        mock_get_upcoming_birthdays,
    )

    # API call
    response = client.get("/api/contacts/birthdays?days=7", headers=auth_headers)

    # Assertions
    assert response.status_code == 200
    assert len(response.json()) == len(contacts)
    assert response.json()[0]["first_name"] == contacts[0]["first_name"]
    mock_get_upcoming_birthdays.assert_called_once_with(7, user_data)


@pytest.mark.asyncio
async def test_get_upcoming_birthdays_unauthenticated(client, monkeypatch):
    # Mock get_current_user to raise HTTPException for unauthorized access
    mock_get_current_user = AsyncMock(
        side_effect=HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.UNAUTHORIZED,
        )
    )
    monkeypatch.setattr(
        "src.services.auth_service.get_current_user", mock_get_current_user
    )

    # API call without authentication headers
    response = client.get("/api/contacts/birthdays?days=7")

    # Assertions
    assert response.status_code == 401
    assert response.json()["detail"] == messages.UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_contacts_no_filters(client, monkeypatch, auth_headers):
    # Mock jwt.decode to bypass token validation
    mock_jwt_decode = MagicMock(return_value={"sub": user_data["username"]})
    monkeypatch.setattr("src.services.auth_service.jwt.decode", mock_jwt_decode)

    # Mock get_user_from_db to return a test user
    mock_get_user_from_db = AsyncMock(return_value=user_data)
    monkeypatch.setattr(
        "src.services.auth_service.get_user_from_db", mock_get_user_from_db
    )

    # Mock ContactService to return all contacts
    mock_get_contacts = AsyncMock(return_value=contacts)
    monkeypatch.setattr(
        "src.services.contacts_service.ContactService.get_contacts", mock_get_contacts
    )

    # API call
    response = client.get("/api/contacts/", headers=auth_headers)

    # Assertions
    assert response.status_code == 200
    assert len(response.json()) == len(contacts)
    assert response.json()[0]["email"] == contacts[0]["email"]
    mock_get_contacts.assert_called_once_with("", "", "", 0, 100, user_data)


@pytest.mark.asyncio
async def test_get_contacts_with_filters(client, monkeypatch, auth_headers):
    # Mock jwt.decode and user retrieval as before
    mock_jwt_decode = MagicMock(return_value={"sub": user_data["username"]})
    monkeypatch.setattr("src.services.auth_service.jwt.decode", mock_jwt_decode)
    mock_get_user_from_db = AsyncMock(return_value=user_data)
    monkeypatch.setattr(
        "src.services.auth_service.get_user_from_db", mock_get_user_from_db
    )

    # Mock ContactService to return filtered contacts
    filtered_contacts = [contacts[0]]
    mock_get_contacts = AsyncMock(return_value=filtered_contacts)
    monkeypatch.setattr(
        "src.services.contacts_service.ContactService.get_contacts", mock_get_contacts
    )

    # API call with filters
    response = client.get(
        "/api/contacts/?first_name=John&last_name=Doe", headers=auth_headers
    )

    # Assertions
    assert response.status_code == 200
    assert len(response.json()) == len(filtered_contacts)
    assert response.json()[0]["first_name"] == "John"
    mock_get_contacts.assert_called_once_with("John", "Doe", "", 0, 100, user_data)


@pytest.mark.asyncio
async def test_get_contacts_pagination(client, monkeypatch, auth_headers):
    # Mock jwt.decode and user retrieval as before
    mock_jwt_decode = MagicMock(return_value={"sub": user_data["username"]})
    monkeypatch.setattr("src.services.auth_service.jwt.decode", mock_jwt_decode)
    mock_get_user_from_db = AsyncMock(return_value=user_data)
    monkeypatch.setattr(
        "src.services.auth_service.get_user_from_db", mock_get_user_from_db
    )

    # Mock ContactService to return paginated contacts
    paginated_contacts = [
        {
            "id": 3,
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice.smith@example.com",
            "phone_number": "987-654-3210",
            "birth_date": "1995-05-15",
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00",
        }
    ]
    mock_get_contacts = AsyncMock(return_value=paginated_contacts)
    monkeypatch.setattr(
        "src.services.contacts_service.ContactService.get_contacts", mock_get_contacts
    )

    # API call with pagination parameters
    response = client.get("/api/contacts/?skip=2&limit=1", headers=auth_headers)

    # Assertions
    assert response.status_code == 200
    assert len(response.json()) == len(paginated_contacts)
    assert response.json()[0]["id"] == 3
    mock_get_contacts.assert_called_once_with("", "", "", 2, 1, user_data)


@pytest.mark.asyncio
async def test_get_contacts_unauthenticated(client, monkeypatch):
    # Mock get_current_user to raise HTTPException for unauthorized access
    mock_get_current_user = AsyncMock(
        side_effect=HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.UNAUTHORIZED,
        )
    )
    monkeypatch.setattr(
        "src.services.auth_service.get_current_user", mock_get_current_user
    )

    # API call without authentication headers
    response = client.get("/api/contacts/")

    # Assertions
    assert response.status_code == 401
    assert response.json()["detail"] == messages.UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_contact_success(client, monkeypatch, auth_headers):
    # Mock jwt.decode to bypass token validation
    mock_jwt_decode = MagicMock(return_value={"sub": user_data["username"]})
    monkeypatch.setattr("src.services.auth_service.jwt.decode", mock_jwt_decode)

    # Mock get_user_from_db to return a test user
    mock_get_user_from_db = AsyncMock(return_value=user_data)
    monkeypatch.setattr(
        "src.services.auth_service.get_user_from_db", mock_get_user_from_db
    )

    # Mock ContactService to return a contact
    contact = contacts[0]
    mock_get_contact = AsyncMock(return_value=contact)
    monkeypatch.setattr(
        "src.services.contacts_service.ContactService.get_contact", mock_get_contact
    )

    # API call
    response = client.get("/api/contacts/1", headers=auth_headers)

    # Assertions
    assert response.status_code == 200
    assert response.json()["id"] == contact["id"]
    assert response.json()["first_name"] == contact["first_name"]
    mock_get_contact.assert_called_once_with(1, user_data)


@pytest.mark.asyncio
async def test_get_contact_not_found(client, monkeypatch, auth_headers):
    # Mock jwt.decode and user retrieval as before
    mock_jwt_decode = MagicMock(return_value={"sub": user_data["username"]})
    monkeypatch.setattr("src.services.auth_service.jwt.decode", mock_jwt_decode)
    mock_get_user_from_db = AsyncMock(return_value=user_data)
    monkeypatch.setattr(
        "src.services.auth_service.get_user_from_db", mock_get_user_from_db
    )

    # Mock ContactService to return None for a missing contact
    mock_get_contact = AsyncMock(return_value=None)
    monkeypatch.setattr(
        "src.services.contacts_service.ContactService.get_contact", mock_get_contact
    )

    # API call to a non-existent contact
    response = client.get("/api/contacts/999", headers=auth_headers)

    # Assertions
    assert response.status_code == 404
    assert response.json()["detail"] == messages.CONTACT_NOT_FOUND
    mock_get_contact.assert_called_once_with(999, user_data)


@pytest.mark.asyncio
async def test_get_contact_unauthenticated(client, monkeypatch):
    # Mock get_current_user to raise HTTPException for unauthorized access
    mock_get_current_user = AsyncMock(
        side_effect=HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.UNAUTHORIZED,
        )
    )
    monkeypatch.setattr(
        "src.services.auth_service.get_current_user", mock_get_current_user
    )

    # API call without authentication headers
    response = client.get("/api/contacts/1")

    # Assertions
    assert response.status_code == 401
    assert response.json()["detail"] == messages.UNAUTHORIZED


@pytest.mark.asyncio
async def test_create_contact_success(client, monkeypatch, auth_headers):
    # Mock jwt.decode to bypass token validation
    mock_jwt_decode = MagicMock(return_value={"sub": user_data["username"]})
    monkeypatch.setattr("src.services.auth_service.jwt.decode", mock_jwt_decode)

    # Mock get_user_from_db to return a test user
    mock_get_user_from_db = AsyncMock(return_value=user_data)
    monkeypatch.setattr(
        "src.services.auth_service.get_user_from_db", mock_get_user_from_db
    )

    # Mock ContactService to simulate contact creation
    new_contact = contacts[0]
    mock_create_contact = AsyncMock(return_value=new_contact)
    monkeypatch.setattr(
        "src.services.contacts_service.ContactService.create_contact",
        mock_create_contact,
    )

    # API call
    response = client.post("/api/contacts/", json=payload, headers=auth_headers)

    expected_contact = ContactModel(**payload)

    # Assertions
    assert response.status_code == 201
    assert response.json()["id"] == new_contact["id"]
    assert response.json()["first_name"] == new_contact["first_name"]
    mock_create_contact.assert_called_once_with(expected_contact, user_data)


@pytest.mark.asyncio
async def test_create_contact_invalid_data(client, monkeypatch, auth_headers):
    # Mock jwt.decode and user retrieval as before
    mock_jwt_decode = MagicMock(return_value={"sub": user_data["username"]})
    monkeypatch.setattr("src.services.auth_service.jwt.decode", mock_jwt_decode)
    mock_get_user_from_db = AsyncMock(return_value=user_data)
    monkeypatch.setattr(
        "src.services.auth_service.get_user_from_db", mock_get_user_from_db
    )

    # Payload with invalid data
    invalid_payload = {
        "first_name": "",  # Missing required fields or invalid data
    }

    # API call
    response = client.post("/api/contacts/", json=invalid_payload, headers=auth_headers)

    # Assertions
    assert response.status_code == 422
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_create_contact_unauthenticated(client, monkeypatch):
    # Mock get_current_user to raise HTTPException for unauthorized access
    mock_get_current_user = AsyncMock(
        side_effect=HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.UNAUTHORIZED,
        )
    )
    monkeypatch.setattr(
        "src.services.auth_service.get_current_user", mock_get_current_user
    )

    # API call without authentication headers
    response = client.post("/api/contacts/", json=payload)

    # Assertions
    assert response.status_code == 401
    assert response.json()["detail"] == messages.UNAUTHORIZED


@pytest.mark.asyncio
async def test_update_contact_success(client, monkeypatch, auth_headers):
    # Mock jwt.decode to bypass token validation
    mock_jwt_decode = MagicMock(return_value={"sub": user_data["username"]})
    monkeypatch.setattr("src.services.auth_service.jwt.decode", mock_jwt_decode)

    # Mock get_user_from_db to return a test user
    mock_get_user_from_db = AsyncMock(return_value=user_data)
    monkeypatch.setattr(
        "src.services.auth_service.get_user_from_db", mock_get_user_from_db
    )

    # Mock ContactService to simulate contact update
    updated_contact = {
        **contacts[0],
        "first_name": "UpdatedJohn",
        "last_name": "UpdatedDoe",
    }
    mock_update_contact = AsyncMock(return_value=updated_contact)
    monkeypatch.setattr(
        "src.services.contacts_service.ContactService.update_contact",
        mock_update_contact,
    )

    # Payload for updating the contact
    payload = {
        "first_name": "UpdatedJohn",
        "last_name": "UpdatedDoe",
        "birth_date": "1990-12-15",
        "email": "john.doe@example.com",
        "phone_number": "123-456-7890",
    }

    contact_id = contacts[0]["id"]

    # API call
    response = client.put(
        f"/api/contacts/{contact_id}", json=payload, headers=auth_headers
    )

    expected_contact = ContactModel(**payload)

    # Assertions
    assert response.status_code == 200
    assert response.json()["id"] == updated_contact["id"]
    assert response.json()["first_name"] == updated_contact["first_name"]
    assert response.json()["last_name"] == updated_contact["last_name"]
    mock_update_contact.assert_called_once_with(contact_id, expected_contact, user_data)


@pytest.mark.asyncio
async def test_update_contact_not_found(client, monkeypatch, auth_headers):
    # Mock jwt.decode and user retrieval as before
    mock_jwt_decode = MagicMock(return_value={"sub": user_data["username"]})
    monkeypatch.setattr("src.services.auth_service.jwt.decode", mock_jwt_decode)
    mock_get_user_from_db = AsyncMock(return_value=user_data)
    monkeypatch.setattr(
        "src.services.auth_service.get_user_from_db", mock_get_user_from_db
    )

    # Mock ContactService to return None for a missing contact
    mock_update_contact = AsyncMock(return_value=None)
    monkeypatch.setattr(
        "src.services.contacts_service.ContactService.update_contact",
        mock_update_contact,
    )

    # Payload for updating the contact
    payload = {
        "first_name": "NonExistent",
        "last_name": "Contact",
        "birth_date": "1990-12-15",
        "email": "nonexistent@example.com",
        "phone_number": "123-456-7890",
    }

    # API call with a non-existent contact ID
    response = client.put("/api/contacts/999", json=payload, headers=auth_headers)

    expected_contact = ContactModel(**payload)
    # Assertions
    assert response.status_code == 404
    assert response.json()["detail"] == messages.CONTACT_NOT_FOUND
    mock_update_contact.assert_called_once_with(999, expected_contact, user_data)


@pytest.mark.asyncio
async def test_update_contact_invalid_data(client, monkeypatch, auth_headers):
    # Mock jwt.decode and user retrieval as before
    mock_jwt_decode = MagicMock(return_value={"sub": user_data["username"]})
    monkeypatch.setattr("src.services.auth_service.jwt.decode", mock_jwt_decode)
    mock_get_user_from_db = AsyncMock(return_value=user_data)
    monkeypatch.setattr(
        "src.services.auth_service.get_user_from_db", mock_get_user_from_db
    )

    # Payload with invalid data
    invalid_payload = {
        "first_name": "",  # Missing or invalid required fields
    }

    # API call with invalid data
    response = client.put("/api/contacts/1", json=invalid_payload, headers=auth_headers)

    # Assertions
    assert response.status_code == 422
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_update_contact_unauthenticated(client, monkeypatch):
    # Mock get_current_user to raise HTTPException for unauthorized access
    mock_get_current_user = AsyncMock(
        side_effect=HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.UNAUTHORIZED,
        )
    )
    monkeypatch.setattr(
        "src.services.auth_service.get_current_user", mock_get_current_user
    )

    # API call without authentication headers
    response = client.put("/api/contacts/1", json={})

    # Assertions
    assert response.status_code == 401
    assert response.json()["detail"] == messages.UNAUTHORIZED


@pytest.mark.asyncio
async def test_delete_contact_success(client, monkeypatch, auth_headers):
    # Mock jwt.decode to bypass token validation
    mock_jwt_decode = MagicMock(return_value={"sub": user_data["username"]})
    monkeypatch.setattr("src.services.auth_service.jwt.decode", mock_jwt_decode)

    # Mock get_user_from_db to return a test user
    mock_get_user_from_db = AsyncMock(return_value=user_data)
    monkeypatch.setattr(
        "src.services.auth_service.get_user_from_db", mock_get_user_from_db
    )

    # Mock ContactService to simulate contact deletion
    mock_delete_contact = AsyncMock(return_value=contacts[0])  # Successfully deleted
    monkeypatch.setattr(
        "src.services.contacts_service.ContactService.remove_contact",
        mock_delete_contact,
    )

    # Contact ID to delete
    contact_id = contacts[0]["id"]

    # API call to delete the contact
    response = client.delete(f"/api/contacts/{contact_id}", headers=auth_headers)

    # Assertions
    assert response.status_code == 200
    assert response.json() == contacts[0]
    mock_delete_contact.assert_called_once_with(contact_id, user_data)


@pytest.mark.asyncio
async def test_delete_contact_not_found(client, monkeypatch, auth_headers):
    # Mock jwt.decode to bypass token validation
    mock_jwt_decode = MagicMock(return_value={"sub": user_data["username"]})
    monkeypatch.setattr("src.services.auth_service.jwt.decode", mock_jwt_decode)

    # Mock get_user_from_db to return a test user
    mock_get_user_from_db = AsyncMock(return_value=user_data)
    monkeypatch.setattr(
        "src.services.auth_service.get_user_from_db", mock_get_user_from_db
    )

    # Mock ContactService to return None for a missing contact
    mock_delete_contact = AsyncMock(return_value=None)  # Contact not found
    monkeypatch.setattr(
        "src.services.contacts_service.ContactService.remove_contact",
        mock_delete_contact,
    )

    # Contact ID to delete
    contact_id = 999  # Non-existent contact ID

    # API call to delete a non-existent contact
    response = client.delete(f"/api/contacts/{contact_id}", headers=auth_headers)

    # Assertions
    assert response.status_code == 404
    assert response.json()["detail"] == messages.CONTACT_NOT_FOUND
    mock_delete_contact.assert_called_once_with(contact_id, user_data)


@pytest.mark.asyncio
async def test_delete_contact_unauthenticated(client, monkeypatch):
    # Mock get_current_user to raise HTTPException for unauthorized access
    mock_get_current_user = AsyncMock(
        side_effect=HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.UNAUTHORIZED,
        )
    )
    monkeypatch.setattr(
        "src.services.auth_service.get_current_user", mock_get_current_user
    )

    # Contact ID to delete
    contact_id = contacts[0]["id"]

    # API call without authentication headers
    response = client.delete(f"/api/contacts/{contact_id}")

    # Assertions
    assert response.status_code == 401
    assert response.json()["detail"] == messages.UNAUTHORIZED
