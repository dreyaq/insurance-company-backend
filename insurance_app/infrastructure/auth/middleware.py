import os
from typing import List, Callable, Optional
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

from insurance_app.domain.exceptions import AuthenticationException, AuthorizationException


class JWTAuthMiddleware:
    """Middleware для JWT аутентификации"""
    
    def __init__(
        self,
        app,
        secret_key: str,
        algorithm: str = "HS256",
        excluded_paths: List[str] = None,
        required_roles: Optional[Callable[[str], List[str]]] = None
    ):
        self.app = app
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.excluded_paths = excluded_paths or []
        self.required_roles = required_roles or (lambda _: [])
        self.security = HTTPBearer(auto_error=False)
    
    async def __call__(self, scope, receive, send):
        """Обработка запроса в соответствии с ASGI спецификацией"""
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
              # Создаем request для доступа к информации о запросе
        request = Request(scope, receive=receive)
        
        # Проверяем, является ли это OPTIONS запросом (для CORS preflight)
        if request.method == "OPTIONS":
            return await self.app(scope, receive, send)
            
        # Проверяем, нужно ли обрабатывать этот путь
        if self._is_path_excluded(request.url.path):
            return await self.app(scope, receive, send)
        
        # Получаем токен из запроса
        credentials = None
        authorization = request.headers.get("Authorization")
        
        if authorization and authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")
            credentials = HTTPAuthorizationCredentials(credentials=token, scheme="Bearer")
        
        if not credentials:
            # Если нет токена, но путь не в исключениях, возвращаем 401
            if not self._is_path_excluded(request.url.path, strict=True):
                return await self._unauthorized_response(scope, receive, send)
            return await self.app(scope, receive, send)
          # Проверяем токен
        try:
            payload = jwt.decode(
                credentials.credentials,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            
            # Проверяем роли, если требуются
            path = request.url.path
            required_roles = self.required_roles(path)
            
            if required_roles:
                user_roles = payload.get("roles", [])
                is_superuser = payload.get("is_superuser", False)
                
                if not is_superuser and not any(role in user_roles for role in required_roles):
                    return await self._forbidden_response(scope, receive, send)
            
            # Добавляем информацию о пользователе в запрос
            # В ASGI middleware мы не можем напрямую изменить объект request
            # Поэтому сохраняем данные пользователя в scope
            scope["user"] = payload
            
        except ExpiredSignatureError:
            return await self._unauthorized_response(scope, receive, send, "Срок действия токена истек")
        except InvalidTokenError:
            return await self._unauthorized_response(scope, receive, send, "Недействительный токен")
        
        return await self.app(scope, receive, send)
    
    def _is_path_excluded(self, path: str, strict: bool = False) -> bool:
        """Проверяет, исключен ли путь из обработки"""
        for excluded in self.excluded_paths:
            if strict:
                if excluded == path:
                    return True
            else:
                if path.startswith(excluded):
                    return True
        return False
        
    async def _unauthorized_response(self, scope, receive, send, detail="Не предоставлены учетные данные"):
        """Возвращает ответ 401 Unauthorized"""
        from starlette.responses import JSONResponse
        response = JSONResponse(
            {"error": "authentication_error", "message": detail, "details": None},
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"}
        )
        await response(scope, receive, send)
        
    async def _forbidden_response(self, scope, receive, send, detail="Доступ запрещен"):
        """Возвращает ответ 403 Forbidden"""
        from starlette.responses import JSONResponse
        response = JSONResponse(
            {"error": "authorization_error", "message": detail, "details": None},
            status_code=status.HTTP_403_FORBIDDEN
        )
        await response(scope, receive, send)
