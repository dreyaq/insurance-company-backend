from typing import List, Optional
from uuid import UUID
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status

from insurance_app.application.dto.claim_dto import ClaimCreateDTO, ClaimUpdateDTO, ClaimResponseDTO, ClaimApproveDTO
from insurance_app.application.dto.common_dto import PaginatedResponseDTO
from insurance_app.application.dto.mappers import ClaimMapper
from insurance_app.application.interfaces.claim_service import ClaimService
from insurance_app.domain.models.claim import ClaimStatus
from insurance_app.presentation.api.dependencies import get_claim_service
from insurance_app.presentation.schemas import ErrorResponse


router = APIRouter(
    prefix="/claims",
    tags=["claims"],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    }
)


@router.post(
    "",
    response_model=ClaimResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый страховой случай",
    responses={
        status.HTTP_201_CREATED: {"description": "Страховой случай успешно создан"},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Неверные данные страхового случая"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Полис или клиент не найдены"}
    }
)
async def create_claim(
    claim_data: ClaimCreateDTO,
    claim_service: ClaimService = Depends(get_claim_service)
):
    """
    Создает новый страховой случай в системе.
    
    - **claim_number**: номер страхового случая (опционально, генерируется автоматически)
    - **policy_id**: ID полиса
    - **client_id**: ID клиента (опционально, если не указан, берется из полиса)
    - **incident_date**: дата происшествия (опционально)
    - **report_date**: дата подачи заявления (опционально, по умолчанию текущая дата)
    - **description**: описание страхового случая
    - **claim_amount**: требуемая сумма выплаты
    """
    try:
        # Преобразуем DTO в доменную модель
        claim = ClaimMapper.to_domain(claim_data)
        
        # Создаем страховой случай
        created_claim = claim_service.create(claim)
        
        # Преобразуем доменную модель в DTO для ответа
        return ClaimMapper.to_dto(created_claim)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "",
    response_model=List[ClaimResponseDTO],
    summary="Получить список страховых случаев",
    responses={
        status.HTTP_200_OK: {"description": "Список страховых случаев успешно получен"}
    }
)
async def get_claims(
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(100, ge=1, le=1000, description="Максимальное количество записей"),
    client_id: Optional[UUID] = Query(None, description="ID клиента для фильтрации"),
    policy_id: Optional[UUID] = Query(None, description="ID полиса для фильтрации"),
    claim_service: ClaimService = Depends(get_claim_service)
):
    """
    Получает список страховых случаев с возможностью фильтрации по клиенту и полису.
    
    - **skip**: количество пропускаемых записей (для пагинации)
    - **limit**: максимальное количество возвращаемых записей (для пагинации)
    - **client_id**: опциональный параметр для фильтрации по ID клиента
    - **policy_id**: опциональный параметр для фильтрации по ID полиса
    """
    if policy_id:
        claims = claim_service.get_by_policy_id(policy_id, skip, limit)
    elif client_id:
        claims = claim_service.get_by_client_id(client_id, skip, limit)
    else:
        claims = claim_service.get_all(skip, limit)
    
    return ClaimMapper.to_dto_list(claims)


@router.get(
    "/{claim_id}",
    response_model=ClaimResponseDTO,
    summary="Получить страховой случай по ID",
    responses={
        status.HTTP_200_OK: {"description": "Страховой случай успешно получен"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Страховой случай не найден"}
    }
)
async def get_claim(
    claim_id: UUID = Path(..., description="ID страхового случая"),
    claim_service: ClaimService = Depends(get_claim_service)
):
    """
    Получает информацию о страховом случае по его ID.
    
    - **claim_id**: уникальный идентификатор страхового случая
    """
    claim = claim_service.get_by_id(claim_id)
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Страховой случай с ID {claim_id} не найден"
        )
    
    return ClaimMapper.to_dto(claim)


@router.put(
    "/{claim_id}",
    response_model=ClaimResponseDTO,
    summary="Обновить данные страхового случая",
    responses={
        status.HTTP_200_OK: {"description": "Данные страхового случая успешно обновлены"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Страховой случай не найден"},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Неверные данные страхового случая"}
    }
)
async def update_claim(
    claim_data: ClaimUpdateDTO,
    claim_id: UUID = Path(..., description="ID страхового случая"),
    claim_service: ClaimService = Depends(get_claim_service)
):
    """
    Обновляет данные страхового случая по его ID.
    
    - **claim_id**: уникальный идентификатор страхового случая
    - **claim_data**: новые данные страхового случая
    """
    # Проверяем существование страхового случая
    claim = claim_service.get_by_id(claim_id)
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Страховой случай с ID {claim_id} не найден"
        )
    
    try:
        # Обновляем данные страхового случая
        updated_claim = ClaimMapper.to_domain(claim_data, claim)
        updated_claim = claim_service.update(updated_claim)
        
        return ClaimMapper.to_dto(updated_claim)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{claim_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить страховой случай",
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Страховой случай успешно удален"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Страховой случай не найден"}
    }
)
async def delete_claim(
    claim_id: UUID = Path(..., description="ID страхового случая"),
    claim_service: ClaimService = Depends(get_claim_service)
):
    """
    Удаляет страховой случай по его ID.
    
    - **claim_id**: уникальный идентификатор страхового случая
    """
    # Проверяем существование страхового случая
    claim = claim_service.get_by_id(claim_id)
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Страховой случай с ID {claim_id} не найден"
        )
    
    # Удаляем страховой случай
    claim_service.delete(claim_id)
    
    # Возвращаем 204 No Content
    return None


@router.get(
    "/number/{claim_number}",
    response_model=ClaimResponseDTO,
    summary="Получить страховой случай по номеру",
    responses={
        status.HTTP_200_OK: {"description": "Страховой случай успешно получен"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Страховой случай не найден"}
    }
)
async def get_claim_by_number(
    claim_number: str = Path(..., description="Номер страхового случая"),
    claim_service: ClaimService = Depends(get_claim_service)
):
    """
    Получает информацию о страховом случае по его номеру.
    
    - **claim_number**: номер страхового случая
    """
    claim = claim_service.get_by_claim_number(claim_number)
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Страховой случай с номером {claim_number} не найден"
        )
    
    return ClaimMapper.to_dto(claim)


@router.patch(
    "/{claim_id}/status",
    response_model=ClaimResponseDTO,
    summary="Изменить статус страхового случая",
    responses={
        status.HTTP_200_OK: {"description": "Статус страхового случая успешно изменен"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Страховой случай не найден"},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Неверный статус"}
    }
)
async def update_claim_status(
    status_data: ClaimStatus,
    claim_id: UUID = Path(..., description="ID страхового случая"),
    claim_service: ClaimService = Depends(get_claim_service)
):
    """
    Изменяет статус страхового случая.
    
    - **claim_id**: уникальный идентификатор страхового случая
    - **status_data**: новый статус страхового случая
    """
    try:
        updated_claim = claim_service.update_status(claim_id, status_data)
        return ClaimMapper.to_dto(updated_claim)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/{claim_id}/approve",
    response_model=ClaimResponseDTO,
    summary="Утвердить страховой случай",
    responses={
        status.HTTP_200_OK: {"description": "Страховой случай успешно утвержден"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Страховой случай не найден"},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Неверная сумма или статус"}
    }
)
async def approve_claim(
    approve_data: ClaimApproveDTO,
    claim_id: UUID = Path(..., description="ID страхового случая"),
    claim_service: ClaimService = Depends(get_claim_service)
):
    """
    Утверждает страховой случай с указанной суммой выплаты.
    
    - **claim_id**: уникальный идентификатор страхового случая
    - **approve_data**: данные для утверждения страхового случая
    """
    try:
        updated_claim = claim_service.approve_claim(claim_id, float(approve_data.approved_amount))
        return ClaimMapper.to_dto(updated_claim)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
