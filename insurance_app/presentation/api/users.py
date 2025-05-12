from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from insurance_app.application.dto.user_dto import UserResponseDTO, UserUpdateDTO
from insurance_app.application.dto.common_dto import PaginationDTO, PaginatedResponseDTO
from insurance_app.application.dto.mappers import UserMapper
from insurance_app.application.interfaces.user_service import UserService
from insurance_app.presentation.api.dependencies import get_user_service, get_current_user
from insurance_app.domain.models.user import User
from insurance_app.domain.exceptions import EntityNotFoundException, BusinessRuleViolationException, AuthenticationException

# Создаем роутер для пользователей
router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
    }
)


@router.get(
    "",
    response_model=PaginatedResponseDTO[UserResponseDTO],
    summary="Получение списка пользователей",
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden"}
    }
)
async def list_users(
    pagination: PaginationDTO = Depends(),
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """
    Получает список пользователей системы.
    Требуется аутентификация и роль администратора.
    """
    # Проверяем, что пользователь имеет права администратора
    if not current_user.is_superuser and "admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для выполнения операции"
        )
    
    users = user_service.list_users(pagination.skip, pagination.limit)
    total = len(users)  # В реальном приложении заменить на отдельный запрос для подсчета всех пользователей
    
    return PaginatedResponseDTO[UserResponseDTO](
        items=UserMapper.to_dto_list(users),
        total=total,
        page=pagination.page,
        size=pagination.limit
    )


@router.get(
    "/{user_id}",
    response_model=UserResponseDTO,
    summary="Получение информации о пользователе",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "User not found"},
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden"}
    }
)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """
    Получает информацию о пользователе по ID.
    Пользователь может получить только свою информацию, администратор - любую.
    """
    # Проверяем, что пользователь запрашивает свою информацию или является администратором
    if str(current_user.id) != str(user_id) and not current_user.is_superuser and "admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для выполнения операции"
        )
    
    try:
        user = user_service.get_user_by_id(user_id)
        return UserMapper.to_dto(user)
    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.patch(
    "/{user_id}",
    response_model=UserResponseDTO,
    summary="Обновление информации о пользователе",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "User not found"},
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden"},
        status.HTTP_409_CONFLICT: {"description": "Conflict"}
    }
)
async def update_user(
    user_id: UUID,
    user_data: UserUpdateDTO,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """
    Обновляет информацию о пользователе.
    Пользователь может обновить только свою информацию, администратор - любую.
    """
    # Проверяем, что пользователь обновляет свою информацию или является администратором
    if str(current_user.id) != str(user_id) and not current_user.is_superuser and "admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для выполнения операции"
        )
    
    # Не позволяем обычным пользователям менять роли
    if user_data.roles is not None and not current_user.is_superuser and "admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для изменения ролей"
        )
    
    try:
        updated_user = user_service.update_user(user_id, user_data.dict(exclude_unset=True))
        return UserMapper.to_dto(updated_user)
    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except BusinessRuleViolationException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление пользователя",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "User not found"},
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden"}
    }
)
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """
    Удаляет пользователя.
    Только администратор может удалять пользователей.
    """
    # Проверяем, что пользователь является администратором
    if not current_user.is_superuser and "admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для выполнения операции"
        )
    
    # Не позволяем удалить самого себя
    if str(current_user.id) == str(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Невозможно удалить свою учетную запись"
        )
    
    result = user_service.delete_user(user_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {user_id} не найден"
        )


@router.get(
    "/me",
    response_model=UserResponseDTO,
    summary="Получение информации о текущем пользователе",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"}
    }
)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Получает информацию о текущем авторизованном пользователе.
    """
    return UserMapper.to_dto(current_user)


@router.patch(
    "/me",
    response_model=UserResponseDTO,
    summary="Обновление информации о текущем пользователе",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
        status.HTTP_409_CONFLICT: {"description": "Conflict"}
    }
)
async def update_current_user(
    user_data: UserUpdateDTO,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """
    Обновляет информацию о текущем авторизованном пользователе.
    """
    # Не позволяем пользователю менять роли
    if user_data.roles is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для изменения ролей"
        )
    
    try:
        updated_user = user_service.update_user(current_user.id, user_data.dict(exclude_unset=True))
        return UserMapper.to_dto(updated_user)
    except BusinessRuleViolationException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.post(
    "/me/change-password",
    response_model=UserResponseDTO,
    summary="Изменение пароля текущего пользователя",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
        status.HTTP_400_BAD_REQUEST: {"description": "Bad Request"}
    }
)
async def change_current_user_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """
    Изменяет пароль текущего авторизованного пользователя.
    """
    try:
        user_service.change_password(current_user.id, current_password, new_password)
        return UserMapper.to_dto(current_user)
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
