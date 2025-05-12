"""
Интеграционные тесты API для работы с платежами
"""
import pytest
from uuid import uuid4
from datetime import date, timedelta
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from insurance_app.domain.models.payment import PaymentStatus, PaymentType
from insurance_app.domain.models.claim import ClaimStatus
from insurance_app.infrastructure.database.models.payment import PaymentModel
from insurance_app.infrastructure.database.models.claim import ClaimModel
from insurance_app.infrastructure.database.models.policy import PolicyModel
from insurance_app.infrastructure.database.models.client import ClientModel


@pytest.fixture
def client_in_db(db_session: Session):
    """Создает тестового клиента в БД"""
    client = ClientModel(
        id=uuid4(),
        first_name="Тест",
        last_name="Тестович",
        email="test@example.com",
        phone="+7 900 123-45-67",
        birth_date=date(1990, 1, 1),
        address="г. Москва, ул. Тестовая, д. 1",
        passport_number="1234 567890",
        is_active=True
    )
    db_session.add(client)
    db_session.commit()
    db_session.refresh(client)
    return client


@pytest.fixture
def policy_in_db(db_session: Session, client_in_db: ClientModel):
    """Создает тестовый полис в БД"""
    policy = PolicyModel(
        id=uuid4(),
        policy_number=f"POL-{uuid4().hex[:8].upper()}",
        client_id=client_in_db.id,
        type="PROPERTY",
        status="ACTIVE",
        start_date=date.today() - timedelta(days=30),
        end_date=date.today() + timedelta(days=335),
        coverage_amount=Decimal("100000.00"),
        premium_amount=Decimal("5000.00"),
        payment_frequency="monthly",
        description="Тестовый полис страхования имущества",
        is_active=True
    )
    db_session.add(policy)
    db_session.commit()
    db_session.refresh(policy)
    return policy


@pytest.fixture
def approved_claim_in_db(db_session: Session, client_in_db: ClientModel, policy_in_db: PolicyModel):
    """Создает тестовый утвержденный страховой случай в БД"""
    claim = ClaimModel(
        id=uuid4(),
        claim_number=f"CLM-{uuid4().hex[:8].upper()}",
        policy_id=policy_in_db.id,
        client_id=client_in_db.id,
        incident_date=date.today() - timedelta(days=5),
        report_date=date.today(),
        description="Тестовый утвержденный страховой случай",
        status=ClaimStatus.APPROVED,
        claim_amount=Decimal("3000.00"),
        approved_amount=Decimal("2500.00"),
        is_active=True
    )
    db_session.add(claim)
    db_session.commit()
    db_session.refresh(claim)
    return claim


@pytest.fixture
def payment_in_db(db_session: Session, client_in_db: ClientModel, policy_in_db: PolicyModel):
    """Создает тестовый платеж в БД"""
    payment = PaymentModel(
        id=uuid4(),
        payment_number=f"PAY-{uuid4().hex[:8].upper()}",
        client_id=client_in_db.id,
        policy_id=policy_in_db.id,
        amount=Decimal("1000.00"),
        due_date=date.today() + timedelta(days=10),
        status=PaymentStatus.PENDING,
        payment_type=PaymentType.PREMIUM,
        payment_method="card",
        description="Тестовый платеж страховой премии",
        is_active=True
    )
    db_session.add(payment)
    db_session.commit()
    db_session.refresh(payment)
    return payment


def test_get_payments(client: TestClient, auth_token: str, db_session: Session, payment_in_db: PaymentModel):
    """Тест получения списка платежей"""
    response = client.get(
        "/api/payments",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1  # Должен быть хотя бы один платеж


def test_get_payment_by_id(client: TestClient, auth_token: str, db_session: Session, payment_in_db: PaymentModel):
    """Тест получения платежа по ID"""
    response = client.get(
        f"/api/payments/{payment_in_db.id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(payment_in_db.id)
    assert data["payment_number"] == payment_in_db.payment_number
    assert data["status"] == payment_in_db.status.value
    assert data["payment_type"] == payment_in_db.payment_type.value


def test_get_payment_by_id_not_found(client: TestClient, auth_token: str):
    """Тест получения несуществующего платежа"""
    non_existent_id = uuid4()
    response = client.get(
        f"/api/payments/{non_existent_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 404
    assert "не найден" in response.json()["detail"]


def test_create_payment(client: TestClient, auth_token: str, db_session: Session, client_in_db: ClientModel, policy_in_db: PolicyModel):
    """Тест создания платежа"""
    payment_data = {
        "client_id": str(client_in_db.id),
        "policy_id": str(policy_in_db.id),
        "amount": "1500.00",
        "payment_type": PaymentType.PREMIUM.value,
        "payment_method": "bank_transfer",
        "description": "Новый тестовый платеж"
    }
    
    response = client.post(
        "/api/payments",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=payment_data
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["client_id"] == str(client_in_db.id)
    assert data["policy_id"] == str(policy_in_db.id)
    assert data["amount"] == payment_data["amount"]
    assert data["payment_type"] == payment_data["payment_type"]
    assert data["status"] == PaymentStatus.PENDING.value
    
    # Проверка, что платеж добавлен в БД
    payment_in_db = db_session.query(PaymentModel).filter(PaymentModel.id == uuid4(data["id"])).first()
    assert payment_in_db is not None


def test_create_payment_with_invalid_client(client: TestClient, auth_token: str, policy_in_db: PolicyModel):
    """Тест создания платежа с несуществующим клиентом"""
    payment_data = {
        "client_id": str(uuid4()),  # Несуществующий клиент
        "policy_id": str(policy_in_db.id),
        "amount": "1500.00",
        "payment_type": PaymentType.PREMIUM.value,
        "description": "Платеж с несуществующим клиентом"
    }
    
    response = client.post(
        "/api/payments",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=payment_data
    )
    
    assert response.status_code == 400
    assert "не найден" in response.json()["detail"]


def test_update_payment(client: TestClient, auth_token: str, db_session: Session, payment_in_db: PaymentModel):
    """Тест обновления платежа"""
    update_data = {
        "description": "Обновленное описание платежа",
        "amount": "2000.00",
        "payment_method": "cash"
    }
    
    response = client.put(
        f"/api/payments/{payment_in_db.id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=update_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(payment_in_db.id)
    assert data["description"] == update_data["description"]
    assert data["amount"] == update_data["amount"]
    assert data["payment_method"] == update_data["payment_method"]
    
    # Проверка, что изменения сохранены в БД
    updated_payment = db_session.query(PaymentModel).filter(PaymentModel.id == payment_in_db.id).first()
    assert updated_payment.description == update_data["description"]
    assert updated_payment.amount == Decimal(update_data["amount"])
    assert updated_payment.payment_method == update_data["payment_method"]


def test_update_payment_not_found(client: TestClient, auth_token: str):
    """Тест обновления несуществующего платежа"""
    non_existent_id = uuid4()
    update_data = {
        "description": "Обновленное описание",
        "amount": "2000.00"
    }
    
    response = client.put(
        f"/api/payments/{non_existent_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=update_data
    )
    
    assert response.status_code == 404
    assert "не найден" in response.json()["detail"]


def test_process_payment(client: TestClient, auth_token: str, db_session: Session, payment_in_db: PaymentModel):
    """Тест обработки платежа"""
    process_data = {
        "payment_date": date.today().isoformat()
    }
    
    response = client.post(
        f"/api/payments/{payment_in_db.id}/process",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=process_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(payment_in_db.id)
    assert data["status"] == PaymentStatus.COMPLETED.value
    assert data["payment_date"] == process_data["payment_date"]
    
    # Проверка, что платеж обработан в БД
    processed_payment = db_session.query(PaymentModel).filter(PaymentModel.id == payment_in_db.id).first()
    assert processed_payment.status == PaymentStatus.COMPLETED
    assert processed_payment.payment_date == date.today()


def test_process_payment_not_found(client: TestClient, auth_token: str):
    """Тест обработки несуществующего платежа"""
    non_existent_id = uuid4()
    process_data = {
        "payment_date": date.today().isoformat()
    }
    
    response = client.post(
        f"/api/payments/{non_existent_id}/process",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=process_data
    )
    
    assert response.status_code == 400
    assert "не найден" in response.json()["detail"]


def test_delete_payment(client: TestClient, auth_token: str, db_session: Session, payment_in_db: PaymentModel):
    """Тест удаления платежа"""
    response = client.delete(
        f"/api/payments/{payment_in_db.id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 204
    
    # Проверка, что платеж удален из БД
    deleted_payment = db_session.query(PaymentModel).filter(PaymentModel.id == payment_in_db.id).first()
    assert deleted_payment is None


def test_delete_payment_not_found(client: TestClient, auth_token: str):
    """Тест удаления несуществующего платежа"""
    non_existent_id = uuid4()
    
    response = client.delete(
        f"/api/payments/{non_existent_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 404
    assert "не найден" in response.json()["detail"]


def test_create_premium_payment(client: TestClient, auth_token: str, db_session: Session, policy_in_db: PolicyModel):
    """Тест создания платежа страховой премии"""
    response = client.post(
        f"/api/payments/premium/{policy_in_db.id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["policy_id"] == str(policy_in_db.id)
    assert data["client_id"] == str(policy_in_db.client_id)
    assert data["payment_type"] == PaymentType.PREMIUM.value
    assert data["amount"] == str(policy_in_db.premium_amount)
    
    # Проверка, что платеж добавлен в БД
    payment_in_db = db_session.query(PaymentModel).filter(PaymentModel.id == uuid4(data["id"])).first()
    assert payment_in_db is not None
    assert payment_in_db.payment_type == PaymentType.PREMIUM


def test_create_premium_payment_policy_not_found(client: TestClient, auth_token: str):
    """Тест создания платежа страховой премии с несуществующим полисом"""
    non_existent_id = uuid4()
    
    response = client.post(
        f"/api/payments/premium/{non_existent_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 400
    assert "не найден" in response.json()["detail"]


def test_create_claim_payout(client: TestClient, auth_token: str, db_session: Session, approved_claim_in_db: ClaimModel):
    """Тест создания платежа страховой выплаты"""
    response = client.post(
        f"/api/payments/payout/{approved_claim_in_db.id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["claim_id"] == str(approved_claim_in_db.id)
    assert data["client_id"] == str(approved_claim_in_db.client_id)
    assert data["policy_id"] == str(approved_claim_in_db.policy_id)
    assert data["payment_type"] == PaymentType.CLAIM_PAYOUT.value
    assert data["amount"] == str(approved_claim_in_db.approved_amount)
    
    # Проверка, что платеж добавлен в БД
    payment_in_db = db_session.query(PaymentModel).filter(PaymentModel.id == uuid4(data["id"])).first()
    assert payment_in_db is not None
    assert payment_in_db.payment_type == PaymentType.CLAIM_PAYOUT


def test_create_claim_payout_not_approved(client: TestClient, auth_token: str, db_session: Session):
    """Тест создания платежа страховой выплаты по неутвержденному страховому случаю"""
    # Создаем неутвержденный страховой случай
    claim = ClaimModel(
        id=uuid4(),
        claim_number=f"CLM-{uuid4().hex[:8].upper()}",
        client_id=uuid4(),
        policy_id=uuid4(),
        incident_date=date.today() - timedelta(days=5),
        report_date=date.today(),
        description="Неутвержденный страховой случай",
        status=ClaimStatus.PENDING,  # Не утвержден
        claim_amount=Decimal("3000.00"),
        is_active=True
    )
    db_session.add(claim)
    db_session.commit()
    db_session.refresh(claim)
    
    response = client.post(
        f"/api/payments/payout/{claim.id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 400
    assert "должен быть утвержден" in response.json()["detail"]
