"""
Интеграционные тесты API для работы с страховыми случаями
"""
import pytest
from uuid import uuid4
from datetime import date, timedelta
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from insurance_app.domain.models.claim import ClaimStatus
from insurance_app.domain.models.policy import PolicyStatus
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
        status=PolicyStatus.ACTIVE,
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
def claim_in_db(db_session: Session, client_in_db: ClientModel, policy_in_db: PolicyModel):
    """Создает тестовый страховой случай в БД"""
    claim = ClaimModel(
        id=uuid4(),
        claim_number=f"CLM-{uuid4().hex[:8].upper()}",
        policy_id=policy_in_db.id,
        client_id=client_in_db.id,
        incident_date=date.today() - timedelta(days=5),
        report_date=date.today(),
        description="Тестовый страховой случай",
        status=ClaimStatus.PENDING,
        claim_amount=Decimal("3000.00"),
        is_active=True
    )
    db_session.add(claim)
    db_session.commit()
    db_session.refresh(claim)
    return claim


def test_get_claims(client: TestClient, auth_token: str, db_session: Session, claim_in_db: ClaimModel):
    """Тест получения списка страховых случаев"""
    response = client.get(
        "/api/claims",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1  # Должен быть хотя бы один страховой случай


def test_get_claim_by_id(client: TestClient, auth_token: str, db_session: Session, claim_in_db: ClaimModel):
    """Тест получения страхового случая по ID"""
    response = client.get(
        f"/api/claims/{claim_in_db.id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(claim_in_db.id)
    assert data["claim_number"] == claim_in_db.claim_number
    assert data["status"] == claim_in_db.status.value


def test_get_claim_by_id_not_found(client: TestClient, auth_token: str):
    """Тест получения несуществующего страхового случая"""
    non_existent_id = uuid4()
    response = client.get(
        f"/api/claims/{non_existent_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 404
    assert "не найден" in response.json()["detail"]


def test_create_claim(client: TestClient, auth_token: str, db_session: Session, policy_in_db: PolicyModel):
    """Тест создания страхового случая"""
    claim_data = {
        "policy_id": str(policy_in_db.id),
        "incident_date": (date.today() - timedelta(days=3)).isoformat(),
        "description": "Новый тестовый страховой случай",
        "claim_amount": "2500.00"
    }
    
    response = client.post(
        "/api/claims",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=claim_data
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["policy_id"] == str(policy_in_db.id)
    assert data["description"] == claim_data["description"]
    assert data["claim_amount"] == claim_data["claim_amount"]
    assert data["status"] == ClaimStatus.PENDING.value
    
    # Проверка, что страховой случай добавлен в БД
    claim_in_db = db_session.query(ClaimModel).filter(ClaimModel.id == uuid4(data["id"])).first()
    assert claim_in_db is not None


def test_create_claim_with_invalid_policy(client: TestClient, auth_token: str):
    """Тест создания страхового случая с несуществующим полисом"""
    claim_data = {
        "policy_id": str(uuid4()),  # Несуществующий полис
        "incident_date": (date.today() - timedelta(days=3)).isoformat(),
        "description": "Страховой случай с несуществующим полисом",
        "claim_amount": "2500.00"
    }
    
    response = client.post(
        "/api/claims",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=claim_data
    )
    
    assert response.status_code == 400
    assert "не найден" in response.json()["detail"]


def test_update_claim(client: TestClient, auth_token: str, db_session: Session, claim_in_db: ClaimModel):
    """Тест обновления страхового случая"""
    update_data = {
        "description": "Обновленное описание страхового случая",
        "claim_amount": "3500.00"
    }
    
    response = client.put(
        f"/api/claims/{claim_in_db.id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=update_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(claim_in_db.id)
    assert data["description"] == update_data["description"]
    assert data["claim_amount"] == update_data["claim_amount"]
    
    # Проверка, что изменения сохранены в БД
    updated_claim = db_session.query(ClaimModel).filter(ClaimModel.id == claim_in_db.id).first()
    assert updated_claim.description == update_data["description"]
    assert updated_claim.claim_amount == Decimal(update_data["claim_amount"])


def test_update_claim_not_found(client: TestClient, auth_token: str):
    """Тест обновления несуществующего страхового случая"""
    non_existent_id = uuid4()
    update_data = {
        "description": "Обновленное описание",
        "claim_amount": "3500.00"
    }
    
    response = client.put(
        f"/api/claims/{non_existent_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=update_data
    )
    
    assert response.status_code == 404
    assert "не найден" in response.json()["detail"]


def test_update_claim_status(client: TestClient, auth_token: str, db_session: Session, claim_in_db: ClaimModel):
    """Тест обновления статуса страхового случая"""
    status_data = ClaimStatus.UNDER_REVIEW.value
    
    response = client.patch(
        f"/api/claims/{claim_in_db.id}/status",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=status_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(claim_in_db.id)
    assert data["status"] == ClaimStatus.UNDER_REVIEW.value
    
    # Проверка, что статус обновлен в БД
    updated_claim = db_session.query(ClaimModel).filter(ClaimModel.id == claim_in_db.id).first()
    assert updated_claim.status == ClaimStatus.UNDER_REVIEW


def test_approve_claim(client: TestClient, auth_token: str, db_session: Session, claim_in_db: ClaimModel):
    """Тест утверждения страхового случая"""
    approve_data = {
        "approved_amount": "2000.00"
    }
    
    response = client.post(
        f"/api/claims/{claim_in_db.id}/approve",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=approve_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(claim_in_db.id)
    assert data["status"] == ClaimStatus.APPROVED.value
    assert data["approved_amount"] == approve_data["approved_amount"]
    
    # Проверка, что статус и сумма обновлены в БД
    updated_claim = db_session.query(ClaimModel).filter(ClaimModel.id == claim_in_db.id).first()
    assert updated_claim.status == ClaimStatus.APPROVED
    assert updated_claim.approved_amount == Decimal(approve_data["approved_amount"])


def test_approve_claim_amount_too_high(client: TestClient, auth_token: str, db_session: Session, claim_in_db: ClaimModel):
    """Тест утверждения страхового случая с суммой, превышающей заявленную"""
    # Сумма больше чем claim_amount
    approve_data = {
        "approved_amount": str(float(claim_in_db.claim_amount) + 1000)
    }
    
    response = client.post(
        f"/api/claims/{claim_in_db.id}/approve",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=approve_data
    )
    
    assert response.status_code == 400
    assert "не может превышать сумму страхового случая" in response.json()["detail"]


def test_delete_claim(client: TestClient, auth_token: str, db_session: Session, claim_in_db: ClaimModel):
    """Тест удаления страхового случая"""
    response = client.delete(
        f"/api/claims/{claim_in_db.id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 204
    
    # Проверка, что страховой случай удален из БД
    deleted_claim = db_session.query(ClaimModel).filter(ClaimModel.id == claim_in_db.id).first()
    assert deleted_claim is None


def test_delete_claim_not_found(client: TestClient, auth_token: str):
    """Тест удаления несуществующего страхового случая"""
    non_existent_id = uuid4()
    
    response = client.delete(
        f"/api/claims/{non_existent_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 404
    assert "не найден" in response.json()["detail"]
