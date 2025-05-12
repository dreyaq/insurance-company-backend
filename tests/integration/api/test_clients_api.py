"""
Интеграционные тесты для API клиентов
"""
import pytest
import json
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4

from insurance_app.presentation.main import app
from insurance_app.infrastructure.database.models.client import ClientModel
from insurance_app.infrastructure.database.models.user import UserModel
from insurance_app.infrastructure.auth.auth_service import AuthService


@pytest.fixture
def auth_token(app_client, db_session):
    """Фикстура для получения токена аутентификации"""
    # Создаем пользователя для тестов
    auth_service = AuthService(secret_key="your-secret-key")
    hashed_password = auth_service.create_password_hash("testpassword")
    
    test_user = UserModel(
        id=uuid4(),
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=False,
        roles=["user"]
    )
    
    db_session.add(test_user)
    db_session.commit()
    
    # Получаем токен
    response = app_client.post(
        "/api/auth/login",
        data={"username": "testuser", "password": "testpassword"}
    )
    
    token_data = response.json()
    return token_data["access_token"]


class TestClientAPI:
    """Интеграционные тесты для API клиентов"""
    
    def test_create_client(self, app_client, auth_token):
        """Тестирование создания клиента через API"""
        # Arrange
        client_data = {
            "first_name": "Иван",
            "last_name": "Иванов",
            "email": "ivan@example.com",
            "phone": "+7 900 123-45-67",
            "birth_date": "1990-01-01",
            "address": "г. Москва, ул. Примерная, д. 1",
            "passport_number": "1234 567890"
        }
        
        # Act
        response = app_client.post(
            "/api/clients",
            json=client_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == client_data["first_name"]
        assert data["last_name"] == client_data["last_name"]
        assert data["email"] == client_data["email"]
        assert "id" in data
    
    def test_get_clients(self, app_client, db_session, auth_token):
        """Тестирование получения списка клиентов через API"""
        # Arrange - создаем несколько клиентов в базе
        clients = []
        for i in range(3):
            client = ClientModel(
                id=uuid4(),
                first_name=f"Имя{i}",
                last_name=f"Фамилия{i}",
                email=f"email{i}@example.com",
                phone=f"+7 900 123-45-{i}",
                birth_date="1990-01-01",
                address=f"Адрес {i}",
                passport_number=f"1234 56789{i}",
                is_active=True
            )
            db_session.add(client)
            clients.append(client)
        
        db_session.commit()
        
        # Act
        response = app_client.get(
            "/api/clients",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 3
    
    def test_get_client_by_id(self, app_client, db_session, auth_token):
        """Тестирование получения клиента по ID через API"""
        # Arrange - создаем клиента в базе
        client_id = uuid4()
        client = ClientModel(
            id=client_id,
            first_name="Тест",
            last_name="Тестов",
            email="test@example.com",
            phone="+7 900 123-45-67",
            birth_date="1990-01-01",
            address="Тестовый адрес",
            passport_number="1234 567890",
            is_active=True
        )
        db_session.add(client)
        db_session.commit()
        
        # Act
        response = app_client.get(
            f"/api/clients/{client_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(client_id)
        assert data["first_name"] == "Тест"
        assert data["last_name"] == "Тестов"
        assert data["email"] == "test@example.com"
    
    def test_update_client(self, app_client, db_session, auth_token):
        """Тестирование обновления клиента через API"""
        # Arrange - создаем клиента в базе
        client_id = uuid4()
        client = ClientModel(
            id=client_id,
            first_name="Старое",
            last_name="Значение",
            email="old@example.com",
            phone="+7 900 123-45-67",
            birth_date="1990-01-01",
            address="Старый адрес",
            passport_number="1234 567890",
            is_active=True
        )
        db_session.add(client)
        db_session.commit()
        
        update_data = {
            "first_name": "Новое",
            "last_name": "Значение",
            "address": "Новый адрес"
        }
        
        # Act
        response = app_client.patch(
            f"/api/clients/{client_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(client_id)
        assert data["first_name"] == "Новое"
        assert data["last_name"] == "Значение"
        assert data["address"] == "Новый адрес"
        assert data["email"] == "old@example.com"  # Не должно измениться
    
    def test_delete_client(self, app_client, db_session, auth_token):
        """Тестирование удаления клиента через API"""
        # Arrange - создаем клиента в базе
        client_id = uuid4()
        client = ClientModel(
            id=client_id,
            first_name="Удаляемый",
            last_name="Клиент",
            email="delete@example.com",
            phone="+7 900 123-45-67",
            birth_date="1990-01-01",
            address="Адрес",
            passport_number="1234 567890",
            is_active=True
        )
        db_session.add(client)
        db_session.commit()
        
        # Act
        response = app_client.delete(
            f"/api/clients/{client_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Assert
        assert response.status_code == 204
        
        # Проверяем, что клиент удален
        deleted_client = db_session.query(ClientModel).filter(ClientModel.id == client_id).first()
        assert deleted_client is None
