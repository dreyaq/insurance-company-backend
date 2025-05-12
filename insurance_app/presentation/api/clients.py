from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status

from insurance_app.application.dto.client_dto import ClientCreateDTO, ClientUpdateDTO, ClientResponseDTO
from insurance_app.application.dto.common_dto import PaginatedResponseDTO
from insurance_app.application.dto.mappers import ClientMapper
from insurance_app.application.interfaces.client_service import ClientService
from insurance_app.application.interfaces.policy_service import PolicyService
from insurance_app.presentation.api.dependencies import get_client_service, get_policy_service
from insurance_app.presentation.schemas import ErrorResponse


router = APIRouter(
    prefix="/clients",
    tags=["clients"],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    }
)


@router.post(
    "",
    response_model=ClientResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Создать нового клиента",
    responses={
        status.HTTP_201_CREATED: {"description": "Клиент успешно создан"},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Неверные данные клиента"},
        status.HTTP_409_CONFLICT: {"model": ErrorResponse, "description": "Клиент с таким email уже существует"}
    }
)
async def create_client(
    client_data: ClientCreateDTO,
    client_service: ClientService = Depends(get_client_service)
):
    """
    Создает нового клиента в системе.
    
    - **first_name**: имя клиента
    - **last_name**: фамилия клиента
    - **email**: адрес электронной почты (должен быть уникальным)
    - **phone**: номер телефона (опционально)
    - **birth_date**: дата рождения (опционально)
    - **address**: адрес (опционально)
    - **passport_number**: номер паспорта (опционально)
    """
    # Проверка существования клиента с таким email
    existing_client = client_service.get_by_email(client_data.email)
    if existing_client:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Клиент с email {client_data.email} уже существует"
        )
    
    # Преобразуем DTO в доменную модель
    client = ClientMapper.to_domain(client_data)
    
    # Создаем клиента
    created_client = client_service.create(client)
    
    # Преобразуем доменную модель в DTO для ответа
    return ClientMapper.to_dto(created_client)


@router.get(
    "",
    response_model=List[ClientResponseDTO],
    summary="Получить список клиентов",
    responses={
        status.HTTP_200_OK: {"description": "Список клиентов успешно получен"}
    }
)
async def get_clients(
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(100, ge=1, le=1000, description="Максимальное количество записей"),
    name: Optional[str] = Query(None, description="Имя или фамилия для поиска"),
    client_service: ClientService = Depends(get_client_service)
):
    """
    Получает список клиентов с возможностью фильтрации по имени или фамилии.
    
    - **skip**: количество пропускаемых записей (для пагинации)
    - **limit**: максимальное количество возвращаемых записей (для пагинации)
    - **name**: опциональный параметр для поиска по имени или фамилии
    """
    if name:
        clients = client_service.search_by_name(name, skip, limit)
    else:
        clients = client_service.get_all(skip, limit)
    
    return ClientMapper.to_dto_list(clients)


@router.get(
    "/{client_id}",
    response_model=ClientResponseDTO,
    summary="Получить клиента по ID",
    responses={
        status.HTTP_200_OK: {"description": "Клиент успешно получен"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Клиент не найден"}
    }
)
async def get_client(
    client_id: UUID = Path(..., description="ID клиента"),
    client_service: ClientService = Depends(get_client_service)
):
    """
    Получает информацию о клиенте по его ID.
    
    - **client_id**: уникальный идентификатор клиента
    """
    client = client_service.get_by_id(client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Клиент с ID {client_id} не найден"
        )
    
    return ClientMapper.to_dto(client)


@router.put(
    "/{client_id}",
    response_model=ClientResponseDTO,
    summary="Обновить данные клиента",
    responses={
        status.HTTP_200_OK: {"description": "Данные клиента успешно обновлены"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Клиент не найден"},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Неверные данные клиента"},
        status.HTTP_409_CONFLICT: {"model": ErrorResponse, "description": "Указанный email уже используется"}
    }
)
async def update_client(
    client_data: ClientUpdateDTO,
    client_id: UUID = Path(..., description="ID клиента"),
    client_service: ClientService = Depends(get_client_service)
):
    """
    Обновляет данные клиента по его ID.
    
    - **client_id**: уникальный идентификатор клиента
    - **client_data**: новые данные клиента
    """
    # Проверяем существование клиента
    client = client_service.get_by_id(client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Клиент с ID {client_id} не найден"
        )
    
    # Проверяем уникальность email, если он меняется
    if client_data.email and client_data.email != client.email:
        existing_client = client_service.get_by_email(client_data.email)
        if existing_client and existing_client.id != client_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Клиент с email {client_data.email} уже существует"
            )
    
    # Обновляем данные клиента
    updated_client = ClientMapper.to_domain(client_data, client)
    updated_client = client_service.update(updated_client)
    
    return ClientMapper.to_dto(updated_client)


@router.delete(
    "/{client_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить клиента",
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Клиент успешно удален"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Клиент не найден"},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Невозможно удалить клиента с активными полисами"}
    }
)
async def delete_client(
    client_id: UUID = Path(..., description="ID клиента"),
    client_service: ClientService = Depends(get_client_service),
    policy_service: PolicyService = Depends(get_policy_service)
):
    """
    Удаляет клиента по его ID.
    
    - **client_id**: уникальный идентификатор клиента
    
    Проверяет наличие связанных полисов перед удалением.
    Если у клиента есть полисы, выдает ошибку 400 Bad Request.
    """
    # Проверяем существование клиента
    client = client_service.get_by_id(client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Клиент с ID {client_id} не найден"
        )
    
    # Проверяем наличие связанных полисов
    client_policies = policy_service.get_by_client_id(client_id)
    if client_policies and len(client_policies) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Невозможно удалить клиента, так как с ним связаны {len(client_policies)} полис(ов). Удалите связанные полисы перед удалением клиента."
        )
    
    # Удаляем клиента
    client_service.delete(client_id)
    
    # Возвращаем 204 No Content
    return None


@router.get(
    "/email/{email}",
    response_model=ClientResponseDTO,
    summary="Получить клиента по email",
    responses={
        status.HTTP_200_OK: {"description": "Клиент успешно получен"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Клиент не найден"}
    }
)
async def get_client_by_email(
    email: str = Path(..., description="Email клиента"),
    client_service: ClientService = Depends(get_client_service)
):
    """
    Получает информацию о клиенте по его email.
    
    - **email**: адрес электронной почты клиента
    """
    client = client_service.get_by_email(email)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Клиент с email {email} не найден"
        )
    
    return ClientMapper.to_dto(client)
