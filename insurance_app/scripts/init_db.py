"""
Скрипт для инициализации базы данных и создания таблиц.
Запустите этот скрипт перед первым запуском приложения.
"""
import os
import sys
from sqlalchemy import inspect
from uuid import uuid4
from datetime import datetime

# Добавляем корневую директорию проекта в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from insurance_app.infrastructure.database.config import engine, Base, get_db
from insurance_app.infrastructure.database.models.client import ClientModel
from insurance_app.infrastructure.database.models.policy import PolicyModel
from insurance_app.infrastructure.database.models.claim import ClaimModel
from insurance_app.infrastructure.database.models.payment import PaymentModel
from insurance_app.infrastructure.database.models.user import UserModel
from insurance_app.infrastructure.auth.auth_service import AuthService


def init_db():
    """
    Инициализирует базу данных, создавая все таблицы.
    """
    # Получаем инспектор для проверки существования таблиц
    inspector = inspect(engine)
    
    # Создаем таблицы если они не существуют
    tables = {
        'clients': ClientModel.__tablename__,
        'policies': PolicyModel.__tablename__,
        'claims': ClaimModel.__tablename__,
        'payments': PaymentModel.__tablename__,
        'users': UserModel.__tablename__
    }
    
    for name, table in tables.items():
        if not inspector.has_table(table):
            print(f"Создание таблицы {name}...")
        else:
            print(f"Таблица {name} уже существует")
      # Создаем все таблицы
    Base.metadata.create_all(bind=engine)
    print("База данных инициализирована успешно!")
    
    # Создаем административного пользователя, если он не существует
    # Используем сессию напрямую вместо контекстного менеджера
    from sqlalchemy.orm import Session
    db = Session(engine)
    try:
        admin_user = db.query(UserModel).filter(UserModel.username == "admin").first()
        
        if not admin_user:
            print("Создание административного пользователя...")
            
            # Создаем хеш пароля
            auth_service = AuthService(secret_key="your-secret-key")
            hashed_password = auth_service.create_password_hash("admin123")
            
            # Создаем пользователя-администратора
            admin_user = UserModel(
                id=uuid4(),
                username="admin",
                email="admin@insurance.com",
                full_name="Administrator",
                hashed_password=hashed_password,
                is_active=True,
                is_superuser=True,
                roles=["admin", "user"],
                created_at=datetime.utcnow()
            )
            
            db.add(admin_user)
            db.commit()
            print("Административный пользователь создан успешно!")
        else:
            print("Административный пользователь уже существует")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
