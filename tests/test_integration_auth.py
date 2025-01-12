from unittest.mock import Mock, AsyncMock

import pytest

from sqlalchemy import select

from src.conf import messages
from src.database.models import User
from tests.conftest import TestingSessionLocal

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


def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_confirm_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "hashed_password" not in data
    assert "avatar" in data
    assert data["role"] == user_data["role"]


def test_signup_same_email(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_confirm_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 409, response.text
    assert response.json()["detail"] == messages.USER_EMAIL_ALREADY_EXISTS


def test_signup_same_username(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_confirm_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data_unique_email)
    assert response.status_code == 409, response.text
    assert response.json()["detail"] == messages.USER_NAME_ALREADY_EXISTS


def test_repeat_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_confirm_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == messages.USER_EMAIL_ALREADY_EXISTS


def test_not_confirmed_login(client):
    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("username"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.USER_NOT_CONFIRMED


@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == user_data.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("username"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data


def test_wrong_password_login(client):
    response = client.post(
        "api/auth/login",
        data={"username": user_data.get("username"), "password": "password"},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.INVALID_CREDENTIALS


def test_wrong_username_login(client):
    response = client.post(
        "api/auth/login",
        data={"username": "username", "password": user_data.get("password")},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.INVALID_CREDENTIALS


def test_validation_error_login(client):
    response = client.post(
        "api/auth/login", data={"password": user_data.get("password")}
    )
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_confirm_email(client, monkeypatch):
    mock_get_email_from_token = AsyncMock(return_value="test_user@gmail.com")
    monkeypatch.setattr("src.api.auth.get_email_from_token", mock_get_email_from_token)

    mock_user_service = Mock()
    mock_user_service.get_user_by_email = AsyncMock(return_value=Mock(confirmed=False))
    mock_user_service.confirmed_email = AsyncMock(return_value=True)
    monkeypatch.setattr("src.api.auth.UserService", lambda db: mock_user_service)

    # API calls
    response = client.get("api/auth/confirmed_email/token")
    assert response.status_code == 200
    assert response.json()["message"] == messages.EMAIL_CONFIRMED

    # Check calls
    mock_get_email_from_token.assert_called_once_with("token")
    mock_user_service.get_user_by_email.assert_called_once_with("test_user@gmail.com")
    mock_user_service.confirmed_email.assert_called_once_with("test_user@gmail.com")


@pytest.mark.asyncio
async def test_confirm_email_already_confirmed(client, monkeypatch):
    # Mocking the function to get the email from the token
    mock_get_email_from_token = AsyncMock(return_value="test_user@gmail.com")
    monkeypatch.setattr("src.api.auth.get_email_from_token", mock_get_email_from_token)

    # Mocking the UserService and its methods
    mock_user_service = Mock()
    # Returning a user with confirmed set to True (indicating the user is already activated)
    mock_user_service.get_user_by_email = AsyncMock(return_value=Mock(confirmed=True))
    monkeypatch.setattr("src.api.auth.UserService", lambda db: mock_user_service)

    # API calls
    response = client.get("api/auth/confirmed_email/token")

    # Asserts
    assert response.status_code == 200
    assert response.json()["message"] == messages.EMAIL_ALREADY_CONFIRMED

    # Check that the correct methods were called
    mock_get_email_from_token.assert_called_once_with("token")
    mock_user_service.get_user_by_email.assert_called_once_with("test_user@gmail.com")
    # The method should not be called if the user is already confirmed
    mock_user_service.confirmed_email.assert_not_called()


@pytest.mark.asyncio
async def test_request_email(client, monkeypatch):
    # Setup mock
    mock_send_email = AsyncMock()
    monkeypatch.setattr("src.api.auth.send_confirm_email", mock_send_email)

    # create new user (not activated)
    client.post("api/auth/register", json=user_data_unique)
    # request new activation email call
    response = client.post(
        "api/auth/request_email", json={"email": user_data_unique["email"]}
    )

    # Check calls
    assert response.status_code == 200
    assert response.json()["message"] == messages.CHECK_YOUR_EMAIL


@pytest.mark.asyncio
async def test_request_email_already_confirmed(client, monkeypatch):
    mock_send_email = AsyncMock()
    monkeypatch.setattr("src.api.auth.send_confirm_email", mock_send_email)

    # API call
    response = client.post("api/auth/request_email", json={"email": user_data["email"]})

    # Check calls
    assert response.status_code == 200
    assert response.json()["message"] == messages.EMAIL_ALREADY_CONFIRMED


@pytest.mark.asyncio
async def test_confirm_reset_password(client, monkeypatch):
    # Mock the function to get email and password from the token
    mock_get_email_from_token = AsyncMock(return_value="test_user@gmail.com")
    mock_get_password_from_token = AsyncMock(return_value="new_hashed_password")
    monkeypatch.setattr("src.api.auth.get_email_from_token", mock_get_email_from_token)
    monkeypatch.setattr(
        "src.api.auth.get_password_from_token", mock_get_password_from_token
    )

    # Mock the UserService and its methods
    mock_user_service = Mock()
    # Returning a user with an existing email
    mock_user_service.get_user_by_email = AsyncMock(
        return_value=Mock(id=1, email="test_user@gmail.com")
    )
    mock_user_service.reset_password = AsyncMock(
        return_value=None
    )  # Password reset is successful
    monkeypatch.setattr("src.api.auth.UserService", lambda db: mock_user_service)

    # API call to reset password
    response = client.get("api/auth/confirm_reset_password/token")

    # Assertions
    assert response.status_code == 200
    assert response.json()["message"] == messages.PASSWORD_CHANGED

    # Check the functions were called with the correct parameters
    mock_get_email_from_token.assert_called_once_with("token")
    mock_get_password_from_token.assert_called_once_with("token")
    mock_user_service.get_user_by_email.assert_called_once_with("test_user@gmail.com")
    mock_user_service.reset_password.assert_called_once_with(1, "new_hashed_password")


@pytest.mark.asyncio
async def test_confirm_reset_password_invalid_token(client, monkeypatch):
    # Mock the function to simulate an invalid token (returns None for email and password)
    mock_get_email_from_token = AsyncMock(return_value=None)
    mock_get_password_from_token = AsyncMock(return_value=None)
    monkeypatch.setattr("src.api.auth.get_email_from_token", mock_get_email_from_token)
    monkeypatch.setattr(
        "src.api.auth.get_password_from_token", mock_get_password_from_token
    )

    # API call to attempt password reset with invalid token
    response = client.get("api/auth/confirm_reset_password/token")

    # Assertions
    assert response.status_code == 400
    assert response.json()["detail"] == messages.INVALID_OR_EXPIRED_TOKEN

    # Check that the functions were called
    mock_get_email_from_token.assert_called_once_with("token")
    mock_get_password_from_token.assert_called_once_with("token")


@pytest.mark.asyncio
async def test_confirm_reset_password_user_not_found(client, monkeypatch):
    # Mock the function to get email and password from the token
    mock_get_email_from_token = AsyncMock(return_value="test_user@gmail.com")
    mock_get_password_from_token = AsyncMock(return_value="new_hashed_password")
    monkeypatch.setattr("src.api.auth.get_email_from_token", mock_get_email_from_token)
    monkeypatch.setattr(
        "src.api.auth.get_password_from_token", mock_get_password_from_token
    )

    # Mock the UserService and simulate no user found
    mock_user_service = Mock()
    mock_user_service.get_user_by_email = AsyncMock(return_value=None)  # No user found
    monkeypatch.setattr("src.api.auth.UserService", lambda db: mock_user_service)

    # API call to reset password
    response = client.get("api/auth/confirm_reset_password/token")

    # Assertions
    assert response.status_code == 404
    assert response.json()["detail"] == messages.USER_WITH_SUCH_EMAIL_NOT_FOUND

    # Check that the correct functions were called
    mock_get_email_from_token.assert_called_once_with("token")
    mock_get_password_from_token.assert_called_once_with("token")
    mock_user_service.get_user_by_email.assert_called_once_with("test_user@gmail.com")
