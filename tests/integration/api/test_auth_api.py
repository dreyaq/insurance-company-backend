"""
Интеграционные тесты для API аутентификации
"""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from insurance_app.presentation.main import app
from insurance_app.infrastructure.database.models.user import UserModel
from insurance_app.infrastructure.auth.auth_service import AuthService


class TestAuthAPI:
    """Интеграционные тесты для API аутентификации"""
    
    def test_register_user(self, app_client):
        """Тестирование регистрации пользователя"""
        # Arrange
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
            "full_name": "New User"
        }
        
        # Act
        response = app_client.post(
            "/api/auth/register",
            json=user_data
        )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert "id" in data
        assert "password" not in data  # Пароль не должен возвращаться
    
    def test_login_success(self, app_client, db_session):
        """Тестирование успешного входа в систему"""
        # Arrange - создаем пользователя
        auth_service = AuthService(secret_key="your-secret-key")
        hashed_password = auth_service.create_password_hash("testpassword")
        
        user = UserModel(
            id=uuid4(),
            username="loginuser",
            email="login@example.com",
            full_name="Login User",
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False,
            roles=["user"]
        )
        
        db_session.add(user)
        db_session.commit()
        
        # Act
        response = app_client.post(
            "/api/auth/login",
            data={"username": "loginuser", "password": "testpassword"}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, app_client, db_session):
        """Тестирование входа с неправильными учетными данными"""
        # Arrange - создаем пользователя
        auth_service = AuthService(secret_key="your-secret-key")
        hashed_password = auth_service.create_password_hash("correctpassword")
        
        user = UserModel(
            id=uuid4(),
            username="invaliduser",
            email="invalid@example.com",
            full_name="Invalid User",
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False,
            roles=["user"]
        )
        
        db_session.add(user)
        db_session.commit()
        
        # Act
        response = app_client.post(
            "/api/auth/login",
            data={"username": "invaliduser", "password": "wrongpassword"}
        )
        
        # Assert
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
    
    def test_register_duplicate_username(self, app_client, db_session):
        """Тестирование регистрации с существующим именем пользователя"""
        # Arrange - создаем пользователя
        existing_user = UserModel(
            id=uuid4(),
            username="duplicateuser",
            email="original@example.com",
            full_name="Original User",
            hashed_password="somehash",
            is_active=True,
            is_superuser=False,
            roles=["user"]
        )
        
        db_session.add(existing_user)
        db_session.commit()
        
        # Пытаемся зарегистрировать пользователя с тем же именем
        user_data = {
            "username": "duplicateuser",
            "email": "different@example.com",
            "password": "password123",
            "full_name": "Different User"
        }
        
        # Act
        response = app_client.post(
            "/api/auth/register",
            json=user_data
        )
        
        # Assert
        assert response.status_code == 409  # Conflict
    
    def test_refresh_token(self, app_client, db_session):
        """Тестирование обновления токена"""
        # Arrange - создаем пользователя и получаем токен
        auth_service = AuthService(secret_key="your-secret-key")
        hashed_password = auth_service.create_password_hash("refreshpassword")
        
        user = UserModel(
            id=uuid4(),
            username="refreshuser",
            email="refresh@example.com",
            full_name="Refresh User",
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False,
            roles=["user"]
        )
        
        db_session.add(user)
        db_session.commit()
        
        # Получаем токен
        login_response = app_client.post(
            "/api/auth/login",
            data={"username": "refreshuser", "password": "refreshpassword"}
        )
        
        token_data = login_response.json()
        access_token = token_data["access_token"]
        
        # Act - обновляем токен
        refresh_response = app_client.post(
            "/api/auth/refresh",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        # Assert
        assert refresh_response.status_code == 200
        new_token_data = refresh_response.json()
        assert "access_token" in new_token_data
        assert new_token_data["token_type"] == "bearer"
        # Проверяем, что токены разные
        assert new_token_data["access_token"] != access_token
