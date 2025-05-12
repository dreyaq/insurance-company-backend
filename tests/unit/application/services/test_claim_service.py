"""
Тесты для сервиса работы с страховыми случаями
"""
import pytest
from uuid import uuid4
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

from insurance_app.application.services.claim_service import ClaimServiceImpl
from insurance_app.application.interfaces.claim_repository import ClaimRepository
from insurance_app.application.interfaces.policy_repository import PolicyRepository
from insurance_app.application.interfaces.client_repository import ClientRepository
from insurance_app.domain.models.claim import Claim, ClaimStatus
from insurance_app.domain.models.policy import Policy, PolicyStatus
from insurance_app.domain.exceptions import EntityNotFoundException, BusinessRuleViolationException
from tests.factories import ClaimFactory, PolicyFactory, ClientFactory


class TestClaimService:
    """Тесты для сервиса работы с страховыми случаями"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.claim_repository = MagicMock()
        self.policy_repository = MagicMock()
        self.client_repository = MagicMock()
        self.claim_service = ClaimServiceImpl(
            self.claim_repository,
            self.policy_repository,
            self.client_repository
        )
    
    def test_create_claim(self):
        """Тестирование создания страхового случая"""
        # Arrange
        policy_id = uuid4()
        client_id = uuid4()
        
        policy = PolicyFactory(
            id=policy_id,
            client_id=client_id, 
            status=PolicyStatus.ACTIVE,
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() + timedelta(days=335)
        )
        
        claim_data = Claim(
            policy_id=policy_id,
            client_id=client_id,
            incident_date=date.today() - timedelta(days=5),
            description="Тестовый страховой случай",
            claim_amount=Decimal("5000.00")
        )
        
        expected_claim = Claim(
            id=uuid4(),
            claim_number="CLM-12345678",
            policy_id=policy_id,
            client_id=client_id,
            incident_date=date.today() - timedelta(days=5),
            report_date=date.today(),
            description="Тестовый страховой случай",
            status=ClaimStatus.PENDING,
            claim_amount=Decimal("5000.00"),
            approved_amount=None,
            created_at=date.today(),
            updated_at=date.today(),
            is_active=True
        )
        
        self.policy_repository.get_by_id.return_value = policy
        self.client_repository.get_by_id.return_value = ClientFactory(id=client_id)
        self.claim_repository.create.return_value = expected_claim
        
        # Act
        result = self.claim_service.create(claim_data)
        
        # Assert
        assert result == expected_claim
        self.policy_repository.get_by_id.assert_called_once_with(policy_id)
        self.claim_repository.create.assert_called_once()
    
    def test_create_claim_policy_not_found(self):
        """Тестирование создания страхового случая с несуществующим полисом"""
        # Arrange
        policy_id = uuid4()
        client_id = uuid4()
        
        claim_data = Claim(
            policy_id=policy_id,
            client_id=client_id,
            incident_date=date.today() - timedelta(days=5),
            description="Тестовый страховой случай",
            claim_amount=Decimal("5000.00")
        )
        
        self.policy_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match=f"Полис с ID {policy_id} не найден"):
            self.claim_service.create(claim_data)
        
        self.policy_repository.get_by_id.assert_called_once_with(policy_id)
        self.claim_repository.create.assert_not_called()
    
    def test_create_claim_with_inactive_policy(self):
        """Тестирование создания страхового случая с неактивным полисом"""
        # Arrange
        policy_id = uuid4()
        client_id = uuid4()
        policy = PolicyFactory(
            id=policy_id,
            client_id=client_id,
            status=PolicyStatus.CANCELED  # Неактивный полис
        )
        
        claim_data = Claim(
            policy_id=policy_id,
            client_id=client_id,
            incident_date=date.today() - timedelta(days=5),
            description="Тестовый страховой случай",
            claim_amount=Decimal("5000.00")
        )
        
        self.policy_repository.get_by_id.return_value = policy
        
        # Act & Assert
        with pytest.raises(ValueError, match=f"Полис {policy.policy_number} не активен"):
            self.claim_service.create(claim_data)
        
        self.policy_repository.get_by_id.assert_called_once_with(policy_id)
        self.claim_repository.create.assert_not_called()
    
    def test_create_claim_incident_date_before_policy_start(self):
        """Тестирование создания страхового случая с датой происшествия до начала действия полиса"""
        # Arrange
        policy_id = uuid4()
        client_id = uuid4()
        
        policy = PolicyFactory(
            id=policy_id,
            client_id=client_id, 
            status=PolicyStatus.ACTIVE,
            start_date=date.today() - timedelta(days=10)
        )
        
        claim_data = Claim(
            policy_id=policy_id,
            client_id=client_id,
            incident_date=date.today() - timedelta(days=15),  # До начала действия полиса
            description="Тестовый страховой случай",
            claim_amount=Decimal("5000.00")
        )
        
        self.policy_repository.get_by_id.return_value = policy
        
        # Act & Assert
        with pytest.raises(ValueError, match=f"Дата происшествия не может быть раньше даты начала действия полиса"):
            self.claim_service.create(claim_data)
        
        self.policy_repository.get_by_id.assert_called_once_with(policy_id)
        self.claim_repository.create.assert_not_called()
    
    def test_create_claim_incident_date_after_policy_end(self):
        """Тестирование создания страхового случая с датой происшествия после окончания действия полиса"""
        # Arrange
        policy_id = uuid4()
        client_id = uuid4()
        
        policy = PolicyFactory(
            id=policy_id,
            client_id=client_id, 
            status=PolicyStatus.ACTIVE,
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() - timedelta(days=5)  # Полис уже закончился
        )
        
        claim_data = Claim(
            policy_id=policy_id,
            client_id=client_id,
            incident_date=date.today() - timedelta(days=3),  # После окончания действия полиса
            description="Тестовый страховой случай",
            claim_amount=Decimal("5000.00")
        )
        
        self.policy_repository.get_by_id.return_value = policy
        
        # Act & Assert
        with pytest.raises(ValueError, match=f"Дата происшествия не может быть позже даты окончания действия полиса"):
            self.claim_service.create(claim_data)
        
        self.policy_repository.get_by_id.assert_called_once_with(policy_id)
        self.claim_repository.create.assert_not_called()
    
    def test_get_all_claims(self):
        """Тестирование получения всех страховых случаев"""
        # Arrange
        expected_claims = [
            ClaimFactory(),
            ClaimFactory(),
            ClaimFactory()
        ]
        
        self.claim_repository.get_all.return_value = expected_claims
        
        # Act
        result = self.claim_service.get_all()
        
        # Assert
        assert result == expected_claims
        self.claim_repository.get_all.assert_called_once()
    
    def test_get_claim_by_id(self):
        """Тестирование получения страхового случая по ID"""
        # Arrange
        claim_id = uuid4()
        expected_claim = ClaimFactory(id=claim_id)
        
        self.claim_repository.get_by_id.return_value = expected_claim
        
        # Act
        result = self.claim_service.get_by_id(claim_id)
        
        # Assert
        assert result == expected_claim
        self.claim_repository.get_by_id.assert_called_once_with(claim_id)
    
    def test_get_claim_by_id_not_found(self):
        """Тестирование получения несуществующего страхового случая"""
        # Arrange
        claim_id = uuid4()
        
        self.claim_repository.get_by_id.return_value = None
        
        # Act
        result = self.claim_service.get_by_id(claim_id)
        
        # Assert
        assert result is None
        self.claim_repository.get_by_id.assert_called_once_with(claim_id)
    
    def test_update_claim(self):
        """Тестирование обновления страхового случая"""
        # Arrange
        claim_id = uuid4()
        existing_claim = ClaimFactory(
            id=claim_id,
            description="Старое описание",
            claim_amount=Decimal("5000.00")
        )
        
        updated_claim_data = Claim(
            id=claim_id,
            description="Новое описание",
            claim_amount=Decimal("6000.00")
        )
        
        expected_updated_claim = Claim(
            id=claim_id,
            description="Новое описание",
            claim_amount=Decimal("6000.00"),
            updated_at=date.today()
        )
        
        self.claim_repository.get_by_id.return_value = existing_claim
        self.claim_repository.update.return_value = expected_updated_claim
        
        # Act
        result = self.claim_service.update(updated_claim_data)
        
        # Assert
        assert result == expected_updated_claim
        self.claim_repository.get_by_id.assert_called_once_with(claim_id)
        self.claim_repository.update.assert_called_once()
    
    def test_update_claim_not_found(self):
        """Тестирование обновления несуществующего страхового случая"""
        # Arrange
        claim_id = uuid4()
        updated_claim_data = Claim(
            id=claim_id,
            description="Новое описание",
            claim_amount=Decimal("6000.00")
        )
        
        self.claim_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(EntityNotFoundException, match=f"Страховой случай с ID {claim_id} не найден"):
            self.claim_service.update(updated_claim_data)
        
        self.claim_repository.get_by_id.assert_called_once_with(claim_id)
        self.claim_repository.update.assert_not_called()
    
    def test_delete_claim(self):
        """Тестирование удаления страхового случая"""
        # Arrange
        claim_id = uuid4()
        existing_claim = ClaimFactory(id=claim_id)
        
        self.claim_repository.get_by_id.return_value = existing_claim
        self.claim_repository.delete.return_value = True
        
        # Act
        result = self.claim_service.delete(claim_id)
        
        # Assert
        assert result is True
        self.claim_repository.get_by_id.assert_called_once_with(claim_id)
        self.claim_repository.delete.assert_called_once_with(claim_id)
    
    def test_delete_claim_not_found(self):
        """Тестирование удаления несуществующего страхового случая"""
        # Arrange
        claim_id = uuid4()
        
        self.claim_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(EntityNotFoundException, match=f"Страховой случай с ID {claim_id} не найден"):
            self.claim_service.delete(claim_id)
        
        self.claim_repository.get_by_id.assert_called_once_with(claim_id)
        self.claim_repository.delete.assert_not_called()
    
    def test_get_claims_by_policy_id(self):
        """Тестирование получения страховых случаев по ID полиса"""
        # Arrange
        policy_id = uuid4()
        expected_claims = [
            ClaimFactory(policy_id=policy_id),
            ClaimFactory(policy_id=policy_id)
        ]
        
        self.claim_repository.get_by_policy_id.return_value = expected_claims
        
        # Act
        result = self.claim_service.get_by_policy_id(policy_id)
        
        # Assert
        assert result == expected_claims
        self.claim_repository.get_by_policy_id.assert_called_once_with(policy_id, 0, 100)
    
    def test_get_claims_by_client_id(self):
        """Тестирование получения страховых случаев по ID клиента"""
        # Arrange
        client_id = uuid4()
        expected_claims = [
            ClaimFactory(client_id=client_id),
            ClaimFactory(client_id=client_id)
        ]
        
        self.claim_repository.get_by_client_id.return_value = expected_claims
        
        # Act
        result = self.claim_service.get_by_client_id(client_id)
        
        # Assert
        assert result == expected_claims
        self.claim_repository.get_by_client_id.assert_called_once_with(client_id, 0, 100)
    
    def test_approve_claim(self):
        """Тестирование утверждения страхового случая"""
        # Arrange
        claim_id = uuid4()
        approved_amount = Decimal("4500.00")
        
        existing_claim = ClaimFactory(
            id=claim_id,
            status=ClaimStatus.UNDER_REVIEW,
            claim_amount=Decimal("5000.00"),
            approved_amount=None
        )
        
        expected_approved_claim = Claim(
            id=claim_id,
            status=ClaimStatus.APPROVED,
            claim_amount=Decimal("5000.00"),
            approved_amount=approved_amount,
            updated_at=date.today()
        )
        
        self.claim_repository.get_by_id.return_value = existing_claim
        self.claim_repository.update.return_value = expected_approved_claim
        
        # Act
        result = self.claim_service.approve_claim(claim_id, approved_amount)
        
        # Assert
        assert result == expected_approved_claim
        assert result.status == ClaimStatus.APPROVED
        assert result.approved_amount == approved_amount
        self.claim_repository.get_by_id.assert_called_once_with(claim_id)
        self.claim_repository.update.assert_called_once()
    
    def test_approve_claim_not_found(self):
        """Тестирование утверждения несуществующего страхового случая"""
        # Arrange
        claim_id = uuid4()
        approved_amount = Decimal("4500.00")
        
        self.claim_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(EntityNotFoundException, match=f"Страховой случай с ID {claim_id} не найден"):
            self.claim_service.approve_claim(claim_id, approved_amount)
        
        self.claim_repository.get_by_id.assert_called_once_with(claim_id)
        self.claim_repository.update.assert_not_called()
    
    def test_approve_claim_already_approved(self):
        """Тестирование повторного утверждения страхового случая"""
        # Arrange
        claim_id = uuid4()
        approved_amount = Decimal("4500.00")
        
        existing_claim = ClaimFactory(
            id=claim_id,
            status=ClaimStatus.APPROVED,
            claim_amount=Decimal("5000.00"),
            approved_amount=Decimal("4000.00")
        )
        
        self.claim_repository.get_by_id.return_value = existing_claim
        
        # Act & Assert
        with pytest.raises(BusinessRuleViolationException, match=f"Страховой случай уже был утвержден"):
            self.claim_service.approve_claim(claim_id, approved_amount)
        
        self.claim_repository.get_by_id.assert_called_once_with(claim_id)
        self.claim_repository.update.assert_not_called()
    
    def test_approve_claim_amount_too_high(self):
        """Тестирование утверждения страхового случая с суммой превышающей заявленную"""
        # Arrange
        claim_id = uuid4()
        
        existing_claim = ClaimFactory(
            id=claim_id,
            status=ClaimStatus.UNDER_REVIEW,
            claim_amount=Decimal("5000.00"),
            approved_amount=None
        )
        
        approved_amount = Decimal("5500.00")  # Больше чем claim_amount
        
        self.claim_repository.get_by_id.return_value = existing_claim
        
        # Act & Assert
        with pytest.raises(
            BusinessRuleViolationException, 
            match=f"Утвержденная сумма не может превышать сумму страхового случая"
        ):
            self.claim_service.approve_claim(claim_id, approved_amount)
        
        self.claim_repository.get_by_id.assert_called_once_with(claim_id)
        self.claim_repository.update.assert_not_called()
    
    def test_reject_claim(self):
        """Тестирование отклонения страхового случая"""
        # Arrange
        claim_id = uuid4()
        rejection_reason = "Случай не покрывается условиями полиса"
        
        existing_claim = ClaimFactory(
            id=claim_id,
            status=ClaimStatus.UNDER_REVIEW,
            claim_amount=Decimal("5000.00"),
            rejection_reason=None
        )
        
        expected_rejected_claim = Claim(
            id=claim_id,
            status=ClaimStatus.REJECTED,
            claim_amount=Decimal("5000.00"),
            rejection_reason=rejection_reason,
            updated_at=date.today()
        )
        
        self.claim_repository.get_by_id.return_value = existing_claim
        self.claim_repository.update.return_value = expected_rejected_claim
        
        # Act
        result = self.claim_service.reject_claim(claim_id, rejection_reason)
        
        # Assert
        assert result == expected_rejected_claim
        assert result.status == ClaimStatus.REJECTED
        assert result.rejection_reason == rejection_reason
        self.claim_repository.get_by_id.assert_called_once_with(claim_id)
        self.claim_repository.update.assert_called_once()
    
    def test_reject_claim_not_found(self):
        """Тестирование отклонения несуществующего страхового случая"""
        # Arrange
        claim_id = uuid4()
        rejection_reason = "Случай не покрывается условиями полиса"
        
        self.claim_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(EntityNotFoundException, match=f"Страховой случай с ID {claim_id} не найден"):
            self.claim_service.reject_claim(claim_id, rejection_reason)
        
        self.claim_repository.get_by_id.assert_called_once_with(claim_id)
        self.claim_repository.update.assert_not_called()
    
    def test_reject_claim_already_rejected(self):
        """Тестирование повторного отклонения страхового случая"""
        # Arrange
        claim_id = uuid4()
        rejection_reason = "Новая причина отклонения"
        
        existing_claim = ClaimFactory(
            id=claim_id,
            status=ClaimStatus.REJECTED,
            claim_amount=Decimal("5000.00"),
            rejection_reason="Первоначальная причина отклонения"
        )
        
        self.claim_repository.get_by_id.return_value = existing_claim
        
        # Act & Assert
        with pytest.raises(BusinessRuleViolationException, match=f"Страховой случай уже был отклонен"):
            self.claim_service.reject_claim(claim_id, rejection_reason)
        
        self.claim_repository.get_by_id.assert_called_once_with(claim_id)
        self.claim_repository.update.assert_not_called()
    
    def test_get_by_claim_number(self):
        """Тестирование получения страхового случая по номеру"""
        # Arrange
        claim_number = "CLM-12345678"
        expected_claim = ClaimFactory(claim_number=claim_number)
        
        self.claim_repository.get_by_claim_number.return_value = expected_claim
        
        # Act
        result = self.claim_service.get_by_claim_number(claim_number)
        
        # Assert
        assert result == expected_claim
        self.claim_repository.get_by_claim_number.assert_called_once_with(claim_number)
