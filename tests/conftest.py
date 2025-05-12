"""
Конфигурация для тестов
"""
import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Добавляем корневую директорию проекта в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from insurance_app.infrastructure.database.config import Base
from insurance_app.infrastructure.database.models.client import ClientModel
from insurance_app.infrastructure.database.models.policy import PolicyModel
from insurance_app.infrastructure.database.models.claim import ClaimModel
from insurance_app.infrastructure.database.models.payment import PaymentModel
from insurance_app.infrastructure.database.models.user import UserModel


# Создаем тестовый движок SQLite в памяти
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def engine():
    """Создает движок SQLite в памяти для тестов"""
    return create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture(scope="session")
def tables(engine):
    """Создает все таблицы в тестовой базе данных"""
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(engine, tables):
    """Создает сессию для тестов и откатывает все изменения после каждого теста"""
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(autocommit=False, autoflush=False, bind=connection)()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def app_client():
    """Создает тестовый клиент для FastAPI приложения"""
    from fastapi.testclient import TestClient
    from insurance_app.presentation.main import app
    
    # Переопределяем зависимость для тестов
    from insurance_app.presentation.api.dependencies import get_db
    
    # Создаем движок SQLite в памяти
    test_engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Создаем таблицы
    Base.metadata.create_all(bind=test_engine)
    
    # Создаем сессию
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    
    # Переопределяем зависимость get_db
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    # Устанавливаем переопределенную зависимость
    app.dependency_overrides[get_db] = override_get_db
    
    # Создаем тестового клиента
    client = TestClient(app)
    
    # Возвращаем клиент
    yield client
    
    # Очищаем таблицы после тестов
    Base.metadata.drop_all(bind=test_engine)
