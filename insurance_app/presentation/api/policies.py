from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status

from insurance_app.application.dto.policy_dto import PolicyCreateDTO, PolicyUpdateDTO, PolicyResponseDTO
from insurance_app.application.dto.common_dto import PaginatedResponseDTO
from insurance_app.application.dto.mappers import PolicyMapper
from insurance_app.application.interfaces.policy_service import PolicyService
from insurance_app.domain.models.policy import PolicyStatus
from insurance_app.presentation.api.dependencies import get_policy_service
from insurance_app.presentation.schemas import ErrorResponse


router = APIRouter(
    prefix="/policies",
    tags=["policies"],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    }
)


@router.post(
    "",
    response_model=PolicyResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый страховой полис",
    responses={
        status.HTTP_201_CREATED: {"description": "Полис успешно создан"},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Неверные данные полиса"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Клиент не найден"}
    }
)
async def create_policy(
    policy_data: PolicyCreateDTO,
    policy_service: PolicyService = Depends(get_policy_service)
):
    """
    Создает новый страховой полис в системе.
    
    - **policy_number**: номер полиса (опционально, генерируется автоматически)
    - **client_id**: ID клиента
    - **type**: тип полиса (LIFE, HEALTH, PROPERTY, VEHICLE, TRAVEL)
    - **start_date**: дата начала действия полиса (опционально)
    - **end_date**: дата окончания действия полиса (опционально)
    - **coverage_amount**: страховая сумма
    - **payment_frequency**: частота платежей (по умолчанию "monthly")
    - **description**: описание полиса (опционально)
    """
    try:
        # Преобразуем DTO в доменную модель
        policy = PolicyMapper.to_domain(policy_data)
        
        # Создаем полис
        created_policy = policy_service.create(policy)
        
        # Преобразуем доменную модель в DTO для ответа
        return PolicyMapper.to_dto(created_policy)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "",
    response_model=List[PolicyResponseDTO],
    summary="Получить список полисов",
    responses={
        status.HTTP_200_OK: {"description": "Список полисов успешно получен"}
    }
)
async def get_policies(
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(100, ge=1, le=1000, description="Максимальное количество записей"),
    client_id: Optional[UUID] = Query(None, description="ID клиента для фильтрации"),
    active_only: bool = Query(False, description="Только активные полисы"),
    policy_service: PolicyService = Depends(get_policy_service)
):
    """
    Получает список полисов с возможностью фильтрации по клиенту и статусу.
    
    - **skip**: количество пропускаемых записей (для пагинации)
    - **limit**: максимальное количество возвращаемых записей (для пагинации)
    - **client_id**: опциональный параметр для фильтрации по ID клиента
    - **active_only**: если true, возвращает только активные полисы
    """
    if client_id:
        policies = policy_service.get_by_client_id(client_id, skip, limit)
    elif active_only:
        policies = policy_service.get_active_policies(skip, limit)
    else:
        policies = policy_service.get_all(skip, limit)
    
    return PolicyMapper.to_dto_list(policies)


@router.get(
    "/{policy_id}",
    response_model=PolicyResponseDTO,
    summary="Получить полис по ID",
    responses={
        status.HTTP_200_OK: {"description": "Полис успешно получен"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Полис не найден"}
    }
)
async def get_policy(
    policy_id: UUID = Path(..., description="ID полиса"),
    policy_service: PolicyService = Depends(get_policy_service)
):
    """
    Получает информацию о полисе по его ID.
    
    - **policy_id**: уникальный идентификатор полиса
    """
    policy = policy_service.get_by_id(policy_id)
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Полис с ID {policy_id} не найден"
        )
    
    return PolicyMapper.to_dto(policy)


@router.put(
    "/{policy_id}",
    response_model=PolicyResponseDTO,
    summary="Обновить данные полиса",
    responses={
        status.HTTP_200_OK: {"description": "Данные полиса успешно обновлены"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Полис не найден"},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Неверные данные полиса"}
    }
)
async def update_policy(
    policy_data: PolicyUpdateDTO,
    policy_id: UUID = Path(..., description="ID полиса"),
    policy_service: PolicyService = Depends(get_policy_service)
):
    """
    Обновляет данные полиса по его ID.
    
    - **policy_id**: уникальный идентификатор полиса
    - **policy_data**: новые данные полиса
    """
    # Проверяем существование полиса
    policy = policy_service.get_by_id(policy_id)
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Полис с ID {policy_id} не найден"
        )
    
    try:
        # Обновляем данные полиса
        updated_policy = PolicyMapper.to_domain(policy_data, policy)
        updated_policy = policy_service.update(updated_policy)
        
        return PolicyMapper.to_dto(updated_policy)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{policy_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить полис",
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Полис успешно удален"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Полис не найден"}
    }
)
async def delete_policy(
    policy_id: UUID = Path(..., description="ID полиса"),
    policy_service: PolicyService = Depends(get_policy_service)
):
    """
    Удаляет полис по его ID.
    
    - **policy_id**: уникальный идентификатор полиса
    """
    # Проверяем существование полиса
    policy = policy_service.get_by_id(policy_id)
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Полис с ID {policy_id} не найден"
        )
    
    # Удаляем полис
    policy_service.delete(policy_id)
    
    # Возвращаем 204 No Content
    return None


@router.get(
    "/number/{policy_number}",
    response_model=PolicyResponseDTO,
    summary="Получить полис по номеру",
    responses={
        status.HTTP_200_OK: {"description": "Полис успешно получен"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Полис не найден"}
    }
)
async def get_policy_by_number(
    policy_number: str = Path(..., description="Номер полиса"),
    policy_service: PolicyService = Depends(get_policy_service)
):
    """
    Получает информацию о полисе по его номеру.
    
    - **policy_number**: номер полиса
    """
    policy = policy_service.get_by_policy_number(policy_number)
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Полис с номером {policy_number} не найден"
        )
    
    return PolicyMapper.to_dto(policy)


@router.patch(
    "/{policy_id}/status",
    response_model=PolicyResponseDTO,
    summary="Изменить статус полиса",
    responses={
        status.HTTP_200_OK: {"description": "Статус полиса успешно изменен"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Полис не найден"},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Неверный статус"}
    }
)
async def update_policy_status(
    status_data: PolicyStatus,
    policy_id: UUID = Path(..., description="ID полиса"),
    policy_service: PolicyService = Depends(get_policy_service)
):
    """
    Изменяет статус полиса.
    
    - **policy_id**: уникальный идентификатор полиса
    - **status_data**: новый статус полиса
    """
    # Проверяем существование полиса
    policy = policy_service.get_by_id(policy_id)
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Полис с ID {policy_id} не найден"
        )
    
    # Изменяем статус полиса
    policy.status = status_data
    updated_policy = policy_service.update(policy)
    
    return PolicyMapper.to_dto(updated_policy)
