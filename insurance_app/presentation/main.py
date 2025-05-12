import uvicorn
import os
import datetime
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from insurance_app.presentation.api.clients import router as clients_router
from insurance_app.presentation.api.policies import router as policies_router
from insurance_app.presentation.api.claims import router as claims_router
from insurance_app.presentation.api.payments import router as payments_router
from insurance_app.presentation.api.auth import router as auth_router
from insurance_app.presentation.api.users import router as users_router
from insurance_app.presentation.schemas import HealthCheckResponse, ErrorResponse
from insurance_app.domain.exceptions import DomainException, AuthenticationException, AuthorizationException
from insurance_app.infrastructure.auth.middleware import JWTAuthMiddleware


# Создаем экземпляр FastAPI приложения
app = FastAPI(
    title="Insurance Company API",
    description="API для страховой компании",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],  # В продакшене нужно указать конкретные домены
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", 
                   "X-Requested-With", "X-CSRF-Token", "Access-Control-Allow-Origin"],
    expose_headers=["Authorization", "Content-Type"],
)

# Настройка JWT аутентификации
secret_key = os.environ.get("SECRET_KEY", "your-secret-key")

# Пути, которые не требуют аутентификации
excluded_paths = [
    "/api/docs",
    "/api/redoc",
    "/api/openapi.json",
    "/api/health-check",
    "/api/auth/login",
    "/api/auth/register",
]

# Добавляем эндпоинт для проверки состояния API
@app.get("/api/health-check", response_model=HealthCheckResponse, tags=["System"])
async def health_check():
    """
    Проверка доступности API.
    """
    return {
        "status": "ok",
        "version": app.version,
        "timestamp": datetime.datetime.now().isoformat()
    }

# Определение требуемых ролей для разных путей
def get_required_roles(path: str) -> list:
    """Возвращает список ролей, необходимых для доступа к пути"""
    # Администраторские операции
    if path.startswith("/api/users") and not path.endswith("/me"):
        return ["admin"]
    return []

# Добавление middleware для JWT-аутентификации
app.add_middleware(
    JWTAuthMiddleware,
    secret_key=secret_key,
    excluded_paths=excluded_paths,
    required_roles=get_required_roles
)

# Регистрация роутеров
app.include_router(clients_router, prefix="/api")
app.include_router(policies_router, prefix="/api")
app.include_router(claims_router, prefix="/api")
app.include_router(payments_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")


# Обработчик ошибок валидации
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Обработчик ошибок валидации запросов"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "validation_error", "message": "Ошибка валидации данных", "details": exc.errors()},
    )


# Обработчик доменных ошибок
@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException):
    """Обработчик доменных ошибок"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "domain_error", "message": str(exc), "details": None},
    )


# Обработчик ошибок аутентификации
@app.exception_handler(AuthenticationException)
async def authentication_exception_handler(request: Request, exc: AuthenticationException):
    """Обработчик ошибок аутентификации"""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"error": "authentication_error", "message": str(exc), "details": None},
        headers={"WWW-Authenticate": "Bearer"}
    )


# Обработчик ошибок авторизации
@app.exception_handler(AuthorizationException)
async def authorization_exception_handler(request: Request, exc: AuthorizationException):
    """Обработчик ошибок авторизации"""
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"error": "authorization_error", "message": str(exc), "details": None},
    )


# Проверка состояния API
@app.get(
    "/api/health",
    response_model=HealthCheckResponse,
    tags=["health"],
    summary="Проверка работоспособности API"
)
async def health_check():
    """Проверка работоспособности API"""
    return {"status": "ok", "version": "1.0.0"}


if __name__ == "__main__":
    uvicorn.run("insurance_app.presentation.main:app", host="0.0.0.0", port=8000, reload=True)