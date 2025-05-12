from typing import List, Optional
from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status

from insurance_app.application.dto.payment_dto import PaymentCreateDTO, PaymentUpdateDTO, PaymentResponseDTO, PaymentProcessDTO
from insurance_app.application.dto.common_dto import PaginatedResponseDTO
from insurance_app.application.dto.mappers import PaymentMapper
from insurance_app.application.interfaces.payment_service import PaymentService
from insurance_app.domain.models.payment import PaymentStatus, PaymentType
from insurance_app.presentation.api.dependencies import get_payment_service
from insurance_app.presentation.schemas import ErrorResponse


router = APIRouter(
    prefix="/payments",
    tags=["payments"],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    }
)


@router.post(
    "",
    response_model=PaymentResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый платеж",
    responses={
        status.HTTP_201_CREATED: {"description": "Платеж успешно создан"},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Неверные данные платежа"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Клиент, полис или страховой случай не найдены"}
    }
)
async def create_payment(
    payment_data: PaymentCreateDTO,
    payment_service: PaymentService = Depends(get_payment_service)
):
    """
    Создает новый платеж в системе.
    
    - **payment_number**: номер платежа (опционально, генерируется автоматически)
    - **client_id**: ID клиента (опционально, если не указан, берется из полиса или страхового случая)
    - **policy_id**: ID полиса (опционально для страховых выплат)
    - **claim_id**: ID страхового случая (опционально для премий)
    - **amount**: сумма платежа
    - **payment_type**: тип платежа (PREMIUM, CLAIM_PAYOUT, REFUND)
    - **status**: статус платежа (PENDING, COMPLETED, FAILED, REFUNDED)
    - **payment_method**: способ оплаты (опционально)
    - **description**: описание платежа (опционально)
    - **due_date**: срок оплаты (опционально)
    - **payment_date**: дата платежа (опционально)
    """
    try:
        # Преобразуем DTO в доменную модель
        payment = PaymentMapper.to_domain(payment_data)
        
        # Создаем платеж
        created_payment = payment_service.create(payment)
        
        # Преобразуем доменную модель в DTO для ответа
        return PaymentMapper.to_dto(created_payment)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "",
    response_model=List[PaymentResponseDTO],
    summary="Получить список платежей",
    responses={
        status.HTTP_200_OK: {"description": "Список платежей успешно получен"}
    }
)
async def get_payments(
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(100, ge=1, le=1000, description="Максимальное количество записей"),
    client_id: Optional[UUID] = Query(None, description="ID клиента для фильтрации"),
    policy_id: Optional[UUID] = Query(None, description="ID полиса для фильтрации"),
    claim_id: Optional[UUID] = Query(None, description="ID страхового случая для фильтрации"),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """
    Получает список платежей с возможностью фильтрации по клиенту, полису или страховому случаю.
    
    - **skip**: количество пропускаемых записей (для пагинации)
    - **limit**: максимальное количество возвращаемых записей (для пагинации)
    - **client_id**: опциональный параметр для фильтрации по ID клиента
    - **policy_id**: опциональный параметр для фильтрации по ID полиса
    - **claim_id**: опциональный параметр для фильтрации по ID страхового случая
    """
    if claim_id:
        payments = payment_service.get_by_claim_id(claim_id, skip, limit)
    elif policy_id:
        payments = payment_service.get_by_policy_id(policy_id, skip, limit)
    elif client_id:
        payments = payment_service.get_by_client_id(client_id, skip, limit)
    else:
        payments = payment_service.get_all(skip, limit)
    
    return PaymentMapper.to_dto_list(payments)


@router.get(
    "/{payment_id}",
    response_model=PaymentResponseDTO,
    summary="Получить платеж по ID",
    responses={
        status.HTTP_200_OK: {"description": "Платеж успешно получен"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Платеж не найден"}
    }
)
async def get_payment(
    payment_id: UUID = Path(..., description="ID платежа"),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """
    Получает информацию о платеже по его ID.
    
    - **payment_id**: уникальный идентификатор платежа
    """
    payment = payment_service.get_by_id(payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Платеж с ID {payment_id} не найден"
        )
    
    return PaymentMapper.to_dto(payment)


@router.put(
    "/{payment_id}",
    response_model=PaymentResponseDTO,
    summary="Обновить данные платежа",
    responses={
        status.HTTP_200_OK: {"description": "Данные платежа успешно обновлены"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Платеж не найден"},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Неверные данные платежа"}
    }
)
async def update_payment(
    payment_data: PaymentUpdateDTO,
    payment_id: UUID = Path(..., description="ID платежа"),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """
    Обновляет данные платежа по его ID.
    
    - **payment_id**: уникальный идентификатор платежа
    - **payment_data**: новые данные платежа
    """
    # Проверяем существование платежа
    payment = payment_service.get_by_id(payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Платеж с ID {payment_id} не найден"
        )
    
    try:
        # Обновляем данные платежа
        updated_payment = PaymentMapper.to_domain(payment_data, payment)
        updated_payment = payment_service.update(updated_payment)
        
        return PaymentMapper.to_dto(updated_payment)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{payment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить платеж",
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Платеж успешно удален"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Платеж не найден"}
    }
)
async def delete_payment(
    payment_id: UUID = Path(..., description="ID платежа"),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """
    Удаляет платеж по его ID.
    
    - **payment_id**: уникальный идентификатор платежа
    """
    # Проверяем существование платежа
    payment = payment_service.get_by_id(payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Платеж с ID {payment_id} не найден"
        )
    
    # Удаляем платеж
    payment_service.delete(payment_id)
    
    # Возвращаем 204 No Content
    return None


@router.get(
    "/number/{payment_number}",
    response_model=PaymentResponseDTO,
    summary="Получить платеж по номеру",
    responses={
        status.HTTP_200_OK: {"description": "Платеж успешно получен"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Платеж не найден"}
    }
)
async def get_payment_by_number(
    payment_number: str = Path(..., description="Номер платежа"),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """
    Получает информацию о платеже по его номеру.
    
    - **payment_number**: номер платежа
    """
    payment = payment_service.get_by_payment_number(payment_number)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Платеж с номером {payment_number} не найден"
        )
    
    return PaymentMapper.to_dto(payment)


@router.post(
    "/{payment_id}/process",
    response_model=PaymentResponseDTO,
    summary="Обработать платеж",
    responses={
        status.HTTP_200_OK: {"description": "Платеж успешно обработан"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Платеж не найден"},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Неверный статус платежа"}
    }
)
async def process_payment(
    process_data: PaymentProcessDTO,
    payment_id: UUID = Path(..., description="ID платежа"),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """
    Обрабатывает платеж, меняя его статус на COMPLETED.
    
    - **payment_id**: уникальный идентификатор платежа
    - **process_data**: данные для обработки платежа (опционально - дата платежа)
    """
    try:
        processed_payment = payment_service.process_payment(payment_id, process_data.payment_date)
        return PaymentMapper.to_dto(processed_payment)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/premium/{policy_id}",
    response_model=PaymentResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Создать платеж страховой премии",
    responses={
        status.HTTP_201_CREATED: {"description": "Платеж страховой премии успешно создан"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Полис не найден"},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Ошибка при создании платежа"}
    }
)
async def create_premium_payment(
    policy_id: UUID = Path(..., description="ID полиса"),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """
    Создает платеж страховой премии для указанного полиса.
    
    - **policy_id**: уникальный идентификатор полиса
    """
    try:
        payment = payment_service.create_premium_payment(policy_id)
        return PaymentMapper.to_dto(payment)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/payout/{claim_id}",
    response_model=PaymentResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Создать платеж страховой выплаты",
    responses={
        status.HTTP_201_CREATED: {"description": "Платеж страховой выплаты успешно создан"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Страховой случай не найден"},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Страховой случай не утвержден или ошибка при создании платежа"}
    }
)
async def create_claim_payout(
    claim_id: UUID = Path(..., description="ID страхового случая"),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """
    Создает платеж страховой выплаты для указанного страхового случая.
    
    - **claim_id**: уникальный идентификатор страхового случая
    """
    try:
        payment = payment_service.create_claim_payout(claim_id)
        return PaymentMapper.to_dto(payment)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
