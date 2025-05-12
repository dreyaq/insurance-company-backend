"""
Тесты для сервиса работы с клиентами
"""
import pytest
from uuid import uuid4
from datetime import date
from unittest.mock import MagicMock, patch

from insurance_app.application.services.client_service import ClientServiceImpl
from insurance_app.domain.models.client import Client
from insurance_app.domain.exceptions import EntityNotFoundException, BusinessRuleViolationException
from tests.factories import ClientFactory


class TestClientService:
    """Тесты для сервиса работы с клиентами"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.client_repository = MagicMock()
        self.client_service = ClientServiceImpl(self.client_repository)
    
    def test_create_client(self):
        """Тестирование создания клиента"""
        # Arrange
        client_data = {
            "first_name": "Иван",
            "last_name": "Иванов",
            "email": "ivan@example.com",
            "phone": "+7 900 123-45-67",
            "birth_date": date(1990, 1, 1),
            "address": "г. Москва, ул. Примерная, д. 1",
            "passport_number": "1234 567890"
        }
        
        self.client_repository.get_by_email.return_value = None
        self.client_repository.get_by_phone.return_value = None
        self.client_repository.get_by_passport.return_value = None
        
        expected_client = Client(
            id=uuid4(),
            **client_data,
            created_at=None,
            is_active=True
        )
        
        self.client_repository.create.return_value = expected_client
        
        # Act
        result = self.client_service.create_client(**client_data)
        
        # Assert
        assert result == expected_client
        self.client_repository.create.assert_called_once()
        self.client_repository.get_by_email.assert_called_once_with(client_data["email"])
        self.client_repository.get_by_phone.assert_called_once_with(client_data["phone"])
        self.client_repository.get_by_passport.assert_called_once_with(client_data["passport_number"])
    
    def test_create_client_with_existing_email(self):
        """Тестирование создания клиента с существующим email"""
        # Arrange
        client_data = {
            "first_name": "Иван",
            "last_name": "Иванов",
            "email": "ivan@example.com",
            "phone": "+7 900 123-45-67",
            "birth_date": date(1990, 1, 1),
            "address": "г. Москва, ул. Примерная, д. 1",
            "passport_number": "1234 567890"
        }
        
        existing_client = ClientFactory(email=client_data["email"])
        self.client_repository.get_by_email.return_value = existing_client
        
        # Act & Assert
        with pytest.raises(BusinessRuleViolationException):
            self.client_service.create_client(**client_data)
    
    def test_get_client_by_id(self):
        """Тестирование получения клиента по ID"""
        # Arrange
        client_id = uuid4()
        expected_client = ClientFactory(id=client_id)
        
        self.client_repository.get_by_id.return_value = expected_client
        
        # Act
        result = self.client_service.get_client_by_id(client_id)
        
        # Assert
        assert result == expected_client
        self.client_repository.get_by_id.assert_called_once_with(client_id)
    
    def test_get_client_by_id_not_found(self):
        """Тестирование получения клиента по ID, когда клиент не найден"""
        # Arrange
        client_id = uuid4()
        
        self.client_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(EntityNotFoundException):
            self.client_service.get_client_by_id(client_id)
    
    def test_update_client(self):
        """Тестирование обновления клиента"""
        # Arrange
        client_id = uuid4()
        existing_client = ClientFactory(
            id=client_id,
            first_name="Иван",
            last_name="Иванов",
            email="ivan@example.com"
        )
        
        update_data = {
            "first_name": "Петр",
            "last_name": "Петров"
        }
        
        self.client_repository.get_by_id.return_value = existing_client
        self.client_repository.update.return_value = Client(
            id=client_id,
            first_name="Петр",
            last_name="Петров",
            email="ivan@example.com",
            phone=existing_client.phone,
            birth_date=existing_client.birth_date,
            address=existing_client.address,
            passport_number=existing_client.passport_number,
            created_at=existing_client.created_at,
            is_active=existing_client.is_active
        )
        
        # Act
        result = self.client_service.update_client(client_id, update_data)
        
        # Assert
        assert result.first_name == "Петр"
        assert result.last_name == "Петров"
        assert result.email == "ivan@example.com"  # Не изменилось
        self.client_repository.get_by_id.assert_called_once_with(client_id)
        self.client_repository.update.assert_called_once()
    
    def test_update_client_not_found(self):
        """Тестирование обновления клиента, когда клиент не найден"""
        # Arrange
        client_id = uuid4()
        update_data = {
            "first_name": "Петр",
            "last_name": "Петров"
        }
        
        self.client_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(EntityNotFoundException):
            self.client_service.update_client(client_id, update_data)
    
    def test_delete_client(self):
        """Тестирование удаления клиента"""
        # Arrange
        client_id = uuid4()
        
        self.client_repository.delete.return_value = True
        
        # Act
        result = self.client_service.delete_client(client_id)
        
        # Assert
        assert result is True
        self.client_repository.delete.assert_called_once_with(client_id)
    
    def test_list_clients(self):
        """Тестирование получения списка клиентов"""
        # Arrange
        clients = [ClientFactory() for _ in range(5)]
        skip = 0
        limit = 10
        
        self.client_repository.list.return_value = clients
        
        # Act
        result = self.client_service.list_clients(skip, limit)
        
        # Assert
        assert result == clients
        self.client_repository.list.assert_called_once_with(skip, limit)
