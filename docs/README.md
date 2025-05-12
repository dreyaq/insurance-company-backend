# Страховая компания - серверная часть веб-приложения

## Описание

Данное веб-приложение представляет собой серверную часть системы управления страховой компанией, 
разработанную в рамках курсовой работы. Система позволяет управлять клиентами, полисами, 
страховыми случаями и платежами.

## Используемые технологии

- **Язык программирования**: Python 3.10+
- **Фреймворк**: FastAPI
- **СУБД**: PostgreSQL
- **ORM**: SQLAlchemy
- **Миграции**: Alembic
- **Валидация данных**: Pydantic
- **Аутентификация**: JWT токены
- **Тестирование**: pytest, factory-boy, pytest-asyncio
- **Архитектура**: Domain-Driven Design (DDD)

## Архитектура приложения

Приложение разработано с использованием паттерна Domain-Driven Design (DDD), который разделяет систему на следующие слои:

### 1. Доменный слой (Domain Layer)
Содержит бизнес-логику, доменные модели и бизнес-правила.
- `domain/models/` - доменные модели (Client, Policy, Claim, Payment, User)
- `domain/exceptions.py` - доменные исключения
- `domain/repositories/` - интерфейсы репозиториев

### 2. Слой приложения (Application Layer)
Содержит сервисы, интерфейсы и DTO.
- `application/interfaces/` - интерфейсы репозиториев и сервисов
- `application/services/` - реализации сервисов
- `application/dto/` - объекты передачи данных

### 3. Инфраструктурный слой (Infrastructure Layer)
Содержит реализации репозиториев, конфигурацию базы данных и внешние зависимости.
- `infrastructure/database/` - конфигурация БД и ORM модели
- `infrastructure/database/repositories/` - реализации репозиториев
- `infrastructure/auth/` - аутентификация и авторизация

### 4. Слой представления (Presentation Layer)
Содержит API и пользовательский интерфейс.
- `presentation/api/` - API роутеры
- `presentation/main.py` - основной файл приложения

## Установка и запуск

### Предварительные требования
- Python 3.10+
- PostgreSQL

### Установка зависимостей

```bash
pip install -r requirements.txt
```

### Настройка окружения

Создайте файл `.env` в корневой директории проекта со следующим содержимым:

```
DATABASE_URL=postgresql://username:password@localhost/insurance
SECRET_KEY=your_secret_key_here
```

Замените `username`, `password` на ваши учетные данные PostgreSQL, а `your_secret_key_here` на секретный ключ для JWT токенов.

### Инициализация базы данных

```bash
# Создайте базу данных
createdb insurance

# Применение миграций
alembic upgrade head

# Инициализируйте таблицы и создайте администратора
python -m insurance_app.scripts.init_db
```

### Запуск приложения

```bash
uvicorn insurance_app.presentation.main:app --reload
```

После запуска приложение будет доступно по адресу: http://localhost:8000

API документация доступна по адресу: http://localhost:8000/api/docs

## Структура API

API построено с использованием REST принципов и включает следующие эндпоинты:

### Аутентификация (/api/auth)
- POST /api/auth/register - регистрация нового пользователя
- POST /api/auth/login - вход в систему и получение токена
- POST /api/auth/refresh - обновление токена

### Пользователи (/api/users)
- GET /api/users - получение списка пользователей (только для администраторов)
- GET /api/users/{user_id} - получение информации о пользователе
- GET /api/users/me - получение информации о текущем пользователе
- PATCH /api/users/{user_id} - обновление информации о пользователе
- PATCH /api/users/me - обновление информации о текущем пользователе
- DELETE /api/users/{user_id} - удаление пользователя (только для администраторов)
- POST /api/users/me/change-password - изменение пароля текущего пользователя

### Клиенты (/api/clients)
- GET /api/clients - получение списка клиентов
- GET /api/clients/{client_id} - получение информации о клиенте
- POST /api/clients - создание нового клиента
- PATCH /api/clients/{client_id} - обновление информации о клиенте
- DELETE /api/clients/{client_id} - удаление клиента

### Полисы (/api/policies)
- GET /api/policies - получение списка полисов
- GET /api/policies/{policy_id} - получение информации о полисе
- POST /api/policies - создание нового полиса
- PATCH /api/policies/{policy_id} - обновление информации о полисе
- DELETE /api/policies/{policy_id} - удаление полиса

### Страховые случаи (/api/claims)
- GET /api/claims - получение списка страховых случаев
- GET /api/claims/{claim_id} - получение информации о страховом случае
- POST /api/claims - создание нового страхового случая
- PATCH /api/claims/{claim_id} - обновление информации о страховом случае
- DELETE /api/claims/{claim_id} - удаление страхового случая
- POST /api/claims/{claim_id}/approve - утверждение страхового случая

### Платежи (/api/payments)
- GET /api/payments - получение списка платежей
- GET /api/payments/{payment_id} - получение информации о платеже
- POST /api/payments - создание нового платежа
- PATCH /api/payments/{payment_id} - обновление информации о платеже
- DELETE /api/payments/{payment_id} - удаление платежа
- POST /api/payments/{payment_id}/process - обработка платежа

## Тестирование

Для запуска тестов используйте команду:

```bash
pytest
```

Для запуска тестов с отчетом о покрытии кода:

```bash
pytest --cov=insurance_app
```

Для запуска только модульных тестов:

```bash
pytest -m unit
```

Для запуска только интеграционных тестов:

```bash
pytest -m integration
```

## Аутентификация

Система использует JWT токены для аутентификации. После входа в систему вы получите access token, который нужно передавать в заголовке Authorization:

```
Authorization: Bearer <access_token>
```

Для регистрации используйте эндпоинт `/api/auth/register`, а для входа - `/api/auth/login`.

По умолчанию создается администратор с учетными данными:
- Логин: admin
- Пароль: admin123

## Автор

Усов Егор Леонидович, ИКБО-16-22
