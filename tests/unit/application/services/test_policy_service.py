"""
Тесты для сервиса работы с полисами
"""
import pytest
from uuid import uuid4
from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

from insurance_app.application.services.policy_service import PolicyServiceImpl
from insurance_app.domain.models.policy import Policy, PolicyStatus, PolicyType
from insurance_app.domain.models.client import Client
from insurance_app.domain.exceptions import EntityNotFoundException, BusinessRuleViolationException
from tests.factories import PolicyFactory, ClientFactory


class TestPolicyService:
    """Тесты для сервиса работы с полисами"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.policy_repository = MagicMock()
        self.client_repository = MagicMock()
        self.policy_service = PolicyServiceImpl(self.policy_repository, self.client_repository)
    
    def test_create_policy(self):
        """Тестирование создания полиса"""
        # Arrange
        client_id = uuid4()
        client = ClientFactory(id=client_id)
        
        policy_data = {
            "client_id": client_id,
            "type": PolicyType.LIFE,
            "start_date": date.today(),
            "end_date": date.today() + timedelta(days=365),
            "coverage_amount": Decimal("100000"),
            "payment_frequency": "monthly",
            "description": "Тестовый полис"
        }
        
        self.client_repository.get_by_id.return_value = client
        
        created_policy = Policy(
            id=uuid4(),
            policy_number="POL-12345",
            status=PolicyStatus.ACTIVE,
            premium_amount=Decimal("5000"),  # Рассчитанная премия
            **policy_data,
            created_at=datetime.utcnow(),
            is_active=True
        )
        
        self.policy_repository.create.return_value = created_policy
        
        # Act
        result = self.policy_service.create_policy(**policy_data)
        
        # Assert
        assert result == created_policy
        self.client_repository.get_by_id.assert_called_once_with(client_id)
        self.policy_repository.create.assert_called_once()
        # Премия должна быть рассчитана
        assert result.premium_amount > 0
    
    def test_create_policy_client_not_found(self):
        """Тестирование создания полиса с несуществующим клиентом"""
        # Arrange
        client_id = uuid4()
        
        policy_data = {
            "client_id": client_id,
            "type": PolicyType.LIFE,
            "start_date": date.today(),
            "end_date": date.today() + timedelta(days=365),
            "coverage_amount": Decimal("100000"),
            "payment_frequency": "monthly",
            "description": "Тестовый полис"
        }
        
        self.client_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(EntityNotFoundException):
            self.policy_service.create_policy(**policy_data)
        
        self.client_repository.get_by_id.assert_called_once_with(client_id)
        self.policy_repository.create.assert_not_called()
    
    def test_get_policy_by_id(self):
        """Тестирование получения полиса по ID"""
        # Arrange
        policy_id = uuid4()
        expected_policy = PolicyFactory(id=policy_id)
        
        self.policy_repository.get_by_id.return_value = expected_policy
        
        # Act
        result = self.policy_service.get_policy_by_id(policy_id)
        
        # Assert
        assert result == expected_policy
        self.policy_repository.get_by_id.assert_called_once_with(policy_id)
    
    def test_get_policy_by_id_not_found(self):
        """Тестирование получения полиса по ID, когда полис не найден"""
        # Arrange
        policy_id = uuid4()
        
        self.policy_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(EntityNotFoundException):
            self.policy_service.get_policy_by_id(policy_id)
        
        self.policy_repository.get_by_id.assert_called_once_with(policy_id)
    
    def test_calculate_premium(self):
        """Тестирование расчета страховой премии"""
        # Arrange
        policy = PolicyFactory(
            type=PolicyType.LIFE,
            coverage_amount=Decimal("100000"),
            premium_amount=None  # Премия не установлена
        )
        
        # Act
        result = self.policy_service.calculate_premium(policy)
        
        # Assert
        assert result.premium_amount is not None
        assert result.premium_amount > 0
        # Для страхования жизни премия должна быть выше из-за коэффициента риска
        assert result.premium_amount > policy.coverage_amount * Decimal("0.05")
    
    def test_update_policy(self):
        """Тестирование обновления полиса"""
        # Arrange
        policy_id = uuid4()
        client_id = uuid4()
        
        existing_policy = PolicyFactory(
            id=policy_id,
            client_id=client_id,
            type=PolicyType.PROPERTY,
            coverage_amount=Decimal("100000"),
            premium_amount=Decimal("5000")
        )
        
        update_data = {
            "coverage_amount": Decimal("150000"),
            "description": "Обновленное описание"
        }
        
        updated_policy = Policy(
            id=policy_id,
            client_id=client_id,
            policy_number=existing_policy.policy_number,
            type=existing_policy.type,
            status=existing_policy.status,
            start_date=existing_policy.start_date,
            end_date=existing_policy.end_date,
            coverage_amount=Decimal("150000"),  # Обновлено
            premium_amount=Decimal("7500"),  # Должна быть пересчитана
            payment_frequency=existing_policy.payment_frequency,
            description="Обновленное описание",  # Обновлено
            created_at=existing_policy.created_at,
            is_active=existing_policy.is_active
        )
        
        self.policy_repository.get_by_id.return_value = existing_policy
        self.policy_repository.update.return_value = updated_policy
        
        # Act
        result = self.policy_service.update_policy(policy_id, update_data)
        
        # Assert
        assert result == updated_policy
        assert result.coverage_amount == Decimal("150000")
        assert result.description == "Обновленное описание"
        assert result.premium_amount > existing_policy.premium_amount  # Премия должна быть пересчитана
        self.policy_repository.get_by_id.assert_called_once_with(policy_id)
        self.policy_repository.update.assert_called_once()
    
    def test_update_policy_not_found(self):
        """Тестирование обновления полиса, когда полис не найден"""
        # Arrange
        policy_id = uuid4()
        
        update_data = {
            "coverage_amount": Decimal("150000"),
            "description": "Обновленное описание"
        }
        
        self.policy_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(EntityNotFoundException):
            self.policy_service.update_policy(policy_id, update_data)
        
        self.policy_repository.get_by_id.assert_called_once_with(policy_id)
        self.policy_repository.update.assert_not_called()
    
    def test_cancel_policy(self):
        """Тестирование отмены полиса"""
        # Arrange
        policy_id = uuid4()
        
        existing_policy = PolicyFactory(
            id=policy_id,
            status=PolicyStatus.ACTIVE
        )
        
        cancelled_policy = Policy(
            id=policy_id,
            client_id=existing_policy.client_id,
            policy_number=existing_policy.policy_number,
            type=existing_policy.type,
            status=PolicyStatus.CANCELLED,  # Статус изменен
            start_date=existing_policy.start_date,
            end_date=existing_policy.end_date,
            coverage_amount=existing_policy.coverage_amount,
            premium_amount=existing_policy.premium_amount,
            payment_frequency=existing_policy.payment_frequency,
            description=existing_policy.description,
            created_at=existing_policy.created_at,
            is_active=existing_policy.is_active
        )
        
        self.policy_repository.get_by_id.return_value = existing_policy
        self.policy_repository.update.return_value = cancelled_policy
        
        # Act
        result = self.policy_service.cancel_policy(policy_id)
        
        # Assert
        assert result == cancelled_policy
        assert result.status == PolicyStatus.CANCELLED
        self.policy_repository.get_by_id.assert_called_once_with(policy_id)
        self.policy_repository.update.assert_called_once()
    
    def test_delete_policy(self):
        """Тестирование удаления полиса"""
        # Arrange
        policy_id = uuid4()
        
        self.policy_repository.delete.return_value = True
        
        # Act
        result = self.policy_service.delete_policy(policy_id)
        
        # Assert
        assert result is True
        self.policy_repository.delete.assert_called_once_with(policy_id)
    
    def test_list_policies(self):
        """Тестирование получения списка полисов"""
        # Arrange
        policies = [PolicyFactory() for _ in range(5)]
        skip = 0
        limit = 10
        
        self.policy_repository.list.return_value = policies
        
        # Act
        result = self.policy_service.list_policies(skip, limit)
        
        # Assert
        assert result == policies
        self.policy_repository.list.assert_called_once_with(skip, limit)
    
    def test_get_policies_by_client(self):
        """Тестирование получения полисов по клиенту"""
        # Arrange
        client_id = uuid4()
        policies = [PolicyFactory(client_id=client_id) for _ in range(3)]
        
        self.policy_repository.get_by_client.return_value = policies
        
        # Act
        result = self.policy_service.get_policies_by_client(client_id)
        
        # Assert
        assert result == policies
        self.policy_repository.get_by_client.assert_called_once_with(client_id)
    
    def test_get_active_policies(self):
        """Тестирование получения активных полисов"""
        # Arrange
        active_policies = [PolicyFactory(status=PolicyStatus.ACTIVE) for _ in range(3)]
        
        self.policy_repository.get_active.return_value = active_policies
        
        # Act
        result = self.policy_service.get_active_policies()
        
        # Assert
        assert result == active_policies
        self.policy_repository.get_active.assert_called_once()
        
    def test_renew_policy(self):
        """Тестирование продления полиса"""
        # Arrange
        policy_id = uuid4()
        
        existing_policy = PolicyFactory(
            id=policy_id,
            status=PolicyStatus.ACTIVE,
            end_date=date.today() - timedelta(days=10)  # Уже истек
        )
        
        new_end_date = date.today() + timedelta(days=365)
        
        renewed_policy = Policy(
            id=policy_id,
            client_id=existing_policy.client_id,
            policy_number=existing_policy.policy_number,
            type=existing_policy.type,
            status=PolicyStatus.ACTIVE,
            start_date=date.today(),  # Новая дата начала
            end_date=new_end_date,  # Новая дата окончания
            coverage_amount=existing_policy.coverage_amount,
            premium_amount=existing_policy.premium_amount,
            payment_frequency=existing_policy.payment_frequency,
            description=existing_policy.description,
            created_at=existing_policy.created_at,
            is_active=existing_policy.is_active
        )
        
        self.policy_repository.get_by_id.return_value = existing_policy
        self.policy_repository.update.return_value = renewed_policy
        
        # Act
        result = self.policy_service.renew_policy(policy_id, new_end_date)
        
        # Assert
        assert result == renewed_policy
        assert result.start_date == date.today()
        assert result.end_date == new_end_date
        self.policy_repository.get_by_id.assert_called_once_with(policy_id)
        self.policy_repository.update.assert_called_once()
