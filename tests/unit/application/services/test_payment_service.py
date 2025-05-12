"""
Тесты для сервиса работы с платежами
"""
import pytest
from uuid import uuid4
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

from insurance_app.application.services.payment_service import PaymentServiceImpl
from insurance_app.application.interfaces.payment_repository import PaymentRepository
from insurance_app.application.interfaces.policy_repository import PolicyRepository
from insurance_app.application.interfaces.claim_repository import ClaimRepository
from insurance_app.application.interfaces.client_repository import ClientRepository
from insurance_app.domain.models.payment import Payment, PaymentStatus, PaymentType
from insurance_app.domain.models.claim import Claim, ClaimStatus
from insurance_app.domain.models.policy import Policy, PolicyStatus
from insurance_app.domain.exceptions import EntityNotFoundException, BusinessRuleViolationException
from tests.factories import PaymentFactory, PolicyFactory, ClaimFactory, ClientFactory


class TestPaymentService:
    """Тесты для сервиса работы с платежами"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.payment_repository = MagicMock()
        self.policy_repository = MagicMock()
        self.claim_repository = MagicMock()
        self.client_repository = MagicMock()
        self.payment_service = PaymentServiceImpl(
            self.payment_repository,
            self.policy_repository,
            self.claim_repository,
            self.client_repository
        )
    
    def test_create_payment(self):
        """Тестирование создания платежа"""
        # Arrange
        policy_id = uuid4()
        client_id = uuid4()
        
        policy = PolicyFactory(
            id=policy_id,
            client_id=client_id,
            status=PolicyStatus.ACTIVE
        )
        
        client = ClientFactory(id=client_id)
        
        payment_data = Payment(
            policy_id=policy_id,
            client_id=client_id,
            amount=Decimal("1000.00"),
            payment_type=PaymentType.PREMIUM,
            payment_method="card",
            description="Тестовый платеж"
        )
        
        expected_payment = Payment(
            id=uuid4(),
            payment_number="PAY-12345678",
            policy_id=policy_id,
            client_id=client_id,
            claim_id=None,
            amount=Decimal("1000.00"),
            payment_date=None,
            due_date=None,
            status=PaymentStatus.PENDING,
            payment_type=PaymentType.PREMIUM,
            payment_method="card",
            description="Тестовый платеж",
            created_at=date.today(),
            is_active=True
        )
        
        self.policy_repository.get_by_id.return_value = policy
        self.client_repository.get_by_id.return_value = client
        self.payment_repository.create.return_value = expected_payment
        
        # Act
        result = self.payment_service.create(payment_data)
        
        # Assert
        assert result == expected_payment
        self.policy_repository.get_by_id.assert_called_once_with(policy_id)
        self.client_repository.get_by_id.assert_called_once_with(client_id)
        self.payment_repository.create.assert_called_once()
    
    def test_create_payment_client_not_found(self):
        """Тестирование создания платежа с несуществующим клиентом"""
        # Arrange
        client_id = uuid4()
        
        payment_data = Payment(
            client_id=client_id,
            amount=Decimal("1000.00"),
            payment_type=PaymentType.PREMIUM,
            payment_method="card",
            description="Тестовый платеж"
        )
        
        self.client_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match=f"Клиент с ID {client_id} не найден"):
            self.payment_service.create(payment_data)
        
        self.client_repository.get_by_id.assert_called_once_with(client_id)
        self.payment_repository.create.assert_not_called()
    
    def test_create_payment_policy_not_found(self):
        """Тестирование создания платежа с несуществующим полисом"""
        # Arrange
        policy_id = uuid4()
        client_id = uuid4()
        
        payment_data = Payment(
            policy_id=policy_id,
            client_id=client_id,
            amount=Decimal("1000.00"),
            payment_type=PaymentType.PREMIUM,
            payment_method="card",
            description="Тестовый платеж"
        )
        
        self.client_repository.get_by_id.return_value = ClientFactory(id=client_id)
        self.policy_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match=f"Полис с ID {policy_id} не найден"):
            self.payment_service.create(payment_data)
        
        self.client_repository.get_by_id.assert_called_once_with(client_id)
        self.policy_repository.get_by_id.assert_called_once_with(policy_id)
        self.payment_repository.create.assert_not_called()
    
    def test_create_payment_claim_not_found(self):
        """Тестирование создания платежа с несуществующим страховым случаем"""
        # Arrange
        claim_id = uuid4()
        client_id = uuid4()
        
        payment_data = Payment(
            claim_id=claim_id,
            client_id=client_id,
            amount=Decimal("1000.00"),
            payment_type=PaymentType.CLAIM_PAYOUT,
            payment_method="bank_transfer",
            description="Тестовый платеж по страховому случаю"
        )
        
        self.client_repository.get_by_id.return_value = ClientFactory(id=client_id)
        self.claim_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match=f"Страховой случай с ID {claim_id} не найден"):
            self.payment_service.create(payment_data)
        
        self.client_repository.get_by_id.assert_called_once_with(client_id)
        self.claim_repository.get_by_id.assert_called_once_with(claim_id)
        self.payment_repository.create.assert_not_called()
    
    def test_create_payment_client_from_policy(self):
        """Тестирование создания платежа с получением клиента из полиса"""
        # Arrange
        policy_id = uuid4()
        client_id = uuid4()
        
        policy = PolicyFactory(
            id=policy_id,
            client_id=client_id,
            status=PolicyStatus.ACTIVE
        )
        
        payment_data = Payment(
            policy_id=policy_id,  # Только ID полиса
            amount=Decimal("1000.00"),
            payment_type=PaymentType.PREMIUM,
            payment_method="card",
            description="Тестовый платеж"
        )
        
        expected_payment = Payment(
            id=uuid4(),
            payment_number="PAY-12345678",
            policy_id=policy_id,
            client_id=client_id,  # Клиент должен быть взят из полиса
            claim_id=None,
            amount=Decimal("1000.00"),
            payment_date=None,
            due_date=None,
            status=PaymentStatus.PENDING,
            payment_type=PaymentType.PREMIUM,
            payment_method="card",
            description="Тестовый платеж",
            created_at=date.today(),
            is_active=True
        )
        
        self.policy_repository.get_by_id.return_value = policy
        self.payment_repository.create.return_value = expected_payment
        
        # Act
        result = self.payment_service.create(payment_data)
        
        # Assert
        assert result == expected_payment
        assert result.client_id == client_id  # Должен быть клиент из полиса
        self.policy_repository.get_by_id.assert_called_once_with(policy_id)
        self.payment_repository.create.assert_called_once()
    
    def test_get_payment_by_id(self):
        """Тестирование получения платежа по ID"""
        # Arrange
        payment_id = uuid4()
        expected_payment = PaymentFactory(id=payment_id)
        
        self.payment_repository.get_by_id.return_value = expected_payment
        
        # Act
        result = self.payment_service.get_by_id(payment_id)
        
        # Assert
        assert result == expected_payment
        self.payment_repository.get_by_id.assert_called_once_with(payment_id)
    
    def test_get_payment_by_id_not_found(self):
        """Тестирование получения платежа по ID, когда платеж не найден"""
        # Arrange
        payment_id = uuid4()
        
        self.payment_repository.get_by_id.return_value = None
        
        # Act
        result = self.payment_service.get_by_id(payment_id)
        
        # Assert
        assert result is None
        self.payment_repository.get_by_id.assert_called_once_with(payment_id)
    
    def test_get_payment_by_payment_number(self):
        """Тестирование получения платежа по номеру"""
        # Arrange
        payment_number = "PAY-12345"
        expected_payment = PaymentFactory(payment_number=payment_number)
        
        self.payment_repository.get_by_payment_number.return_value = expected_payment
        
        # Act
        result = self.payment_service.get_by_payment_number(payment_number)
        
        # Assert
        assert result == expected_payment
        self.payment_repository.get_by_payment_number.assert_called_once_with(payment_number)
    
    def test_get_payments_by_client_id(self):
        """Тестирование получения платежей по клиенту"""
        # Arrange
        client_id = uuid4()
        expected_payments = [PaymentFactory(client_id=client_id) for _ in range(3)]
        
        self.payment_repository.get_by_client_id.return_value = expected_payments
        
        # Act
        result = self.payment_service.get_by_client_id(client_id)
        
        # Assert
        assert result == expected_payments
        self.payment_repository.get_by_client_id.assert_called_once_with(client_id, 0, 100)
    
    def test_get_payments_by_policy_id(self):
        """Тестирование получения платежей по полису"""
        # Arrange
        policy_id = uuid4()
        expected_payments = [PaymentFactory(policy_id=policy_id) for _ in range(3)]
        
        self.payment_repository.get_by_policy_id.return_value = expected_payments
        
        # Act
        result = self.payment_service.get_by_policy_id(policy_id)
        
        # Assert
        assert result == expected_payments
        self.payment_repository.get_by_policy_id.assert_called_once_with(policy_id, 0, 100)
    
    def test_get_payments_by_claim_id(self):
        """Тестирование получения платежей по страховому случаю"""
        # Arrange
        claim_id = uuid4()
        expected_payments = [PaymentFactory(claim_id=claim_id) for _ in range(2)]
        
        self.payment_repository.get_by_claim_id.return_value = expected_payments
        
        # Act
        result = self.payment_service.get_by_claim_id(claim_id)
        
        # Assert
        assert result == expected_payments
        self.payment_repository.get_by_claim_id.assert_called_once_with(claim_id, 0, 100)
    
    def test_update_payment(self):
        """Тестирование обновления платежа"""
        # Arrange
        payment_id = uuid4()
        
        existing_payment = PaymentFactory(
            id=payment_id,
            status=PaymentStatus.PENDING,
            description="Первоначальное описание"
        )
        
        updated_payment = Payment(
            id=payment_id,
            payment_number=existing_payment.payment_number,
            client_id=existing_payment.client_id,
            policy_id=existing_payment.policy_id,
            claim_id=existing_payment.claim_id,
            amount=existing_payment.amount,
            payment_date=existing_payment.payment_date,
            due_date=existing_payment.due_date,
            status=PaymentStatus.COMPLETED,  # Изменили статус
            payment_type=existing_payment.payment_type,
            payment_method=existing_payment.payment_method,
            description="Обновленное описание",  # Изменили описание
            created_at=existing_payment.created_at,
            is_active=existing_payment.is_active
        )
        
        self.payment_repository.update.return_value = updated_payment
        
        # Act
        result = self.payment_service.update(updated_payment)
        
        # Assert
        assert result == updated_payment
        assert result.status == PaymentStatus.COMPLETED
        assert result.description == "Обновленное описание"
        self.payment_repository.update.assert_called_once()
    
    def test_delete_payment(self):
        """Тестирование удаления платежа"""
        # Arrange
        payment_id = uuid4()
        
        self.payment_repository.delete.return_value = True
        
        # Act
        result = self.payment_service.delete(payment_id)
        
        # Assert
        assert result is True
        self.payment_repository.delete.assert_called_once_with(payment_id)
    
    def test_process_payment(self):
        """Тестирование обработки платежа"""
        # Arrange
        payment_id = uuid4()
        payment_date = date.today()
        
        existing_payment = PaymentFactory(
            id=payment_id,
            status=PaymentStatus.PENDING,
            payment_date=None
        )
        
        processed_payment = Payment(
            id=payment_id,
            payment_number=existing_payment.payment_number,
            client_id=existing_payment.client_id,
            policy_id=existing_payment.policy_id,
            claim_id=existing_payment.claim_id,
            amount=existing_payment.amount,
            payment_date=payment_date,  # Устанавливается дата платежа
            due_date=existing_payment.due_date,
            status=PaymentStatus.COMPLETED,  # Статус меняется на "Завершен"
            payment_type=existing_payment.payment_type,
            payment_method=existing_payment.payment_method,
            description=existing_payment.description,
            created_at=existing_payment.created_at,
            is_active=existing_payment.is_active
        )
        
        self.payment_repository.get_by_id.return_value = existing_payment
        self.payment_repository.update.return_value = processed_payment
        
        # Act
        result = self.payment_service.process_payment(payment_id, payment_date)
        
        # Assert
        assert result == processed_payment
        assert result.status == PaymentStatus.COMPLETED
        assert result.payment_date == payment_date
        self.payment_repository.get_by_id.assert_called_once_with(payment_id)
        self.payment_repository.update.assert_called_once()
    
    def test_process_payment_not_found(self):
        """Тестирование обработки платежа, когда платеж не найден"""
        # Arrange
        payment_id = uuid4()
        
        self.payment_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match=f"Платеж с ID {payment_id} не найден"):
            self.payment_service.process_payment(payment_id)
        
        self.payment_repository.get_by_id.assert_called_once_with(payment_id)
        self.payment_repository.update.assert_not_called()
    
    def test_process_payment_default_date(self):
        """Тестирование обработки платежа с использованием текущей даты по умолчанию"""
        # Arrange
        payment_id = uuid4()
        
        existing_payment = PaymentFactory(
            id=payment_id,
            status=PaymentStatus.PENDING,
            payment_date=None
        )
        
        processed_payment = Payment(
            id=payment_id,
            payment_number=existing_payment.payment_number,
            client_id=existing_payment.client_id,
            policy_id=existing_payment.policy_id,
            claim_id=existing_payment.claim_id,
            amount=existing_payment.amount,
            payment_date=date.today(),  # Должна быть установлена текущая дата
            due_date=existing_payment.due_date,
            status=PaymentStatus.COMPLETED,  # Статус меняется на "Завершен"
            payment_type=existing_payment.payment_type,
            payment_method=existing_payment.payment_method,
            description=existing_payment.description,
            created_at=existing_payment.created_at,
            is_active=existing_payment.is_active
        )
        
        self.payment_repository.get_by_id.return_value = existing_payment
        self.payment_repository.update.return_value = processed_payment
        
        # Act
        with patch('insurance_app.application.services.payment_service.date') as mock_date:
            mock_date.today.return_value = date.today()
            result = self.payment_service.process_payment(payment_id)
        
        # Assert
        assert result == processed_payment
        assert result.status == PaymentStatus.COMPLETED
        assert result.payment_date == date.today()
        self.payment_repository.get_by_id.assert_called_once_with(payment_id)
        self.payment_repository.update.assert_called_once()
    
    def test_create_premium_payment(self):
        """Тестирование создания платежа страховой премии"""
        # Arrange
        policy_id = uuid4()
        client_id = uuid4()
        
        policy = PolicyFactory(
            id=policy_id,
            client_id=client_id,
            policy_number="POL-12345",
            premium_amount=Decimal("5000.00")
        )
        
        expected_payment = Payment(
            id=uuid4(),
            payment_number="PAY-12345678",
            policy_id=policy_id,
            client_id=client_id,
            claim_id=None,
            amount=Decimal("5000.00"),  # Должна быть равна премии полиса
            payment_date=None,
            due_date=date.today(),  # Текущая дата как срок оплаты
            status=PaymentStatus.PENDING,
            payment_type=PaymentType.PREMIUM,  # Тип "Премия"
            payment_method="",
            description=f"Страховая премия по полису POL-12345",
            created_at=date.today(),
            is_active=True
        )
        
        self.policy_repository.get_by_id.return_value = policy
        self.payment_repository.create.return_value = expected_payment
        
        # Act
        with patch('insurance_app.application.services.payment_service.date') as mock_date:
            mock_date.today.return_value = date.today()
            result = self.payment_service.create_premium_payment(policy_id)
        
        # Assert
        assert result == expected_payment
        assert result.amount == policy.premium_amount
        assert result.payment_type == PaymentType.PREMIUM
        self.policy_repository.get_by_id.assert_called_once_with(policy_id)
        self.payment_repository.create.assert_called_once()
    
    def test_create_premium_payment_policy_not_found(self):
        """Тестирование создания платежа страховой премии, когда полис не найден"""
        # Arrange
        policy_id = uuid4()
        
        self.policy_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match=f"Полис с ID {policy_id} не найден"):
            self.payment_service.create_premium_payment(policy_id)
        
        self.policy_repository.get_by_id.assert_called_once_with(policy_id)
        self.payment_repository.create.assert_not_called()
    
    def test_create_claim_payout(self):
        """Тестирование создания платежа страховой выплаты"""
        # Arrange
        claim_id = uuid4()
        policy_id = uuid4()
        client_id = uuid4()
        
        claim = ClaimFactory(
            id=claim_id,
            claim_number="CLM-12345",
            policy_id=policy_id,
            client_id=client_id,
            status=ClaimStatus.APPROVED,  # Должен быть утвержден
            approved_amount=Decimal("3000.00")  # Должна быть установлена сумма
        )
        
        expected_payment = Payment(
            id=uuid4(),
            payment_number="PAY-12345678",
            policy_id=policy_id,
            client_id=client_id,
            claim_id=claim_id,
            amount=Decimal("3000.00"),  # Должна быть равна утвержденной сумме
            payment_date=None,
            due_date=None,
            status=PaymentStatus.PENDING,
            payment_type=PaymentType.CLAIM_PAYOUT,  # Тип "Страховая выплата"
            payment_method="",
            description=f"Страховая выплата по страховому случаю CLM-12345",
            created_at=date.today(),
            is_active=True
        )
        
        self.claim_repository.get_by_id.return_value = claim
        self.payment_repository.create.return_value = expected_payment
        
        # Act
        result = self.payment_service.create_claim_payout(claim_id)
        
        # Assert
        assert result == expected_payment
        assert result.amount == claim.approved_amount
        assert result.payment_type == PaymentType.CLAIM_PAYOUT
        self.claim_repository.get_by_id.assert_called_once_with(claim_id)
        self.payment_repository.create.assert_called_once()
    
    def test_create_claim_payout_claim_not_found(self):
        """Тестирование создания платежа страховой выплаты, когда страховой случай не найден"""
        # Arrange
        claim_id = uuid4()
        
        self.claim_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match=f"Страховой случай с ID {claim_id} не найден"):
            self.payment_service.create_claim_payout(claim_id)
        
        self.claim_repository.get_by_id.assert_called_once_with(claim_id)
        self.payment_repository.create.assert_not_called()
    
    def test_create_claim_payout_claim_not_approved(self):
        """Тестирование создания платежа страховой выплаты, когда страховой случай не утвержден"""
        # Arrange
        claim_id = uuid4()
        
        claim = ClaimFactory(
            id=claim_id,
            status=ClaimStatus.PENDING  # Не утвержден
        )
        
        self.claim_repository.get_by_id.return_value = claim
        
        # Act & Assert
        with pytest.raises(ValueError, match="Страховой случай должен быть утвержден для создания выплаты"):
            self.payment_service.create_claim_payout(claim_id)
        
        self.claim_repository.get_by_id.assert_called_once_with(claim_id)
        self.payment_repository.create.assert_not_called()
    
    def test_create_claim_payout_no_approved_amount(self):
        """Тестирование создания платежа страховой выплаты, когда не установлена сумма выплаты"""
        # Arrange
        claim_id = uuid4()
        
        claim = ClaimFactory(
            id=claim_id,
            status=ClaimStatus.APPROVED,  # Утвержден
            approved_amount=None  # Но сумма не установлена
        )
        
        self.claim_repository.get_by_id.return_value = claim
        
        # Act & Assert
        with pytest.raises(ValueError, match="Сумма выплаты не установлена"):
            self.payment_service.create_claim_payout(claim_id)
        
        self.claim_repository.get_by_id.assert_called_once_with(claim_id)
        self.payment_repository.create.assert_not_called()
