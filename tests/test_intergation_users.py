from unittest import mock
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException, status
from src.conf import messages


user_data_admin = {
    "id": 1,
    "username": "agent007",
    "email": "agent007@gmail.com",
    "password": "12345678",
    "role": "admin",
    "confirmed": True,
    "avatar": "https://example.com/avatar.png",
}

user_data_not_admin = {
    "id": 1,
    "username": "agent007",
    "email": "agent007@gmail.com",
    "password": "12345678",
    "role": "user",
    "confirmed": True,
    "avatar": "https://example.com/avatar.png",
}


@pytest.mark.asyncio
async def test_me(client, monkeypatch, auth_headers):
    # Mock jwt.decode to bypass token validation
    mock_jwt_decode = MagicMock(return_value={"sub": user_data_admin["username"]})
    monkeypatch.setattr("src.services.auth_service.jwt.decode", mock_jwt_decode)

    # Mock get_user_from_db to return a test user
    mock_get_user_from_db = AsyncMock(return_value=user_data_admin)
    monkeypatch.setattr(
        "src.services.auth_service.get_user_from_db", mock_get_user_from_db
    )

    # API call to get current user
    response = client.get("/api/users/me", headers=auth_headers)

    # Assertions
    assert response.status_code == 200
    assert response.json()["email"] == user_data_admin["email"]
    assert response.json()["username"] == user_data_admin["username"]
    mock_jwt_decode.assert_called_once()
    mock_get_user_from_db.assert_called_once_with(user_data_admin["username"], mock.ANY)


@pytest.mark.asyncio
async def test_me_unauthenticated(client, monkeypatch):
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

    # API call to get current user without valid authentication
    response = client.get("/api/users/me")

    # Assertions
    assert response.status_code == 401
    assert response.json()["detail"] == messages.UNAUTHORIZED
