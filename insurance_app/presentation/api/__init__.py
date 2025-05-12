# Файл для инициализации пакета
from insurance_app.presentation.api.clients import router as clients_router
from insurance_app.presentation.api.policies import router as policies_router
from insurance_app.presentation.api.claims import router as claims_router
from insurance_app.presentation.api.payments import router as payments_router
from insurance_app.presentation.api.auth import router as auth_router
from insurance_app.presentation.api.users import router as users_router

__all__ = [
    'clients_router',
    'policies_router',
    'claims_router',
    'payments_router',
    'auth_router',
    'users_router'
]
