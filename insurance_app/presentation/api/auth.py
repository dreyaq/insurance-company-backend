from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from insurance_app.application.dto.user_dto import UserCreateDTO, UserResponseDTO, TokenDTO, LoginDTO
from insurance_app.application.dto.mappers import UserMapper
from insurance_app.application.interfaces.user_service import UserService
from insurance_app.presentation.api.dependencies import get_db, get_user_service, get_auth_service
from insurance_app.domain.exceptions import (
    BusinessRuleViolationException,
    AuthenticationException,
    EntityNotFoundException
)

# Создаем роутер для авторизации
router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
    }
)

# Создаем объект для OAuth2 с использованием пароля
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


@router.post(
    "/register",
    response_model=UserResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid input"},
        status.HTTP_409_CONFLICT: {"description": "User already exists"}
    }
)
async def register(
    user_data: UserCreateDTO,
    user_service: UserService = Depends(get_user_service)
):
    """
    Регистрирует нового пользователя системы.
    """
    try:
        user = user_service.register_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
        return UserMapper.to_dto(user)
    except BusinessRuleViolationException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/login",
    response_model=TokenDTO,
    summary="Вход в систему и получение токена",
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid credentials"}
    }
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service),
    auth_service = Depends(get_auth_service)
):
    """
    Проверяет учетные данные и возвращает токен доступа.
    """
    print(f"Attempting login for user: {form_data.username}")
    user = user_service.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        print(f"Authentication failed for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"}
        )
      # Создаем JWT токен для пользователя
    access_token = auth_service.create_access_token(user)
    print(f"Generated token for user {form_data.username}: {access_token[:10]}...")
    
    token_dto = TokenDTO(
        access_token=access_token, 
        user_id=str(user.id),
        username=user.username,
        email=user.email
    )
    print(f"Return TokenDTO: {token_dto}")
    return token_dto


@router.post(
    "/refresh",
    response_model=TokenDTO,
    summary="Обновление токена",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid token"}
    }
)
async def refresh_token(
    token: str = Depends(oauth2_scheme),
    auth_service = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service)
):
    """
    Обновляет токен доступа.
    """
    try:
        # Получаем ID пользователя из токена
        user_id = auth_service.get_current_user_id(token)
        
        # Получаем пользователя по ID
        user = user_service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Создаем новый JWT токен для пользователя
        access_token = auth_service.create_access_token(user)
        
        return TokenDTO(access_token=access_token)
    
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
