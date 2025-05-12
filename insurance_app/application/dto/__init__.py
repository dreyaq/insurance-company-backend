# Файл для инициализации пакета
from insurance_app.application.dto.common_dto import PaginationDTO, PaginatedResponseDTO, ErrorDTO
from insurance_app.application.dto.client_dto import ClientBaseDTO, ClientCreateDTO, ClientUpdateDTO, ClientResponseDTO
from insurance_app.application.dto.policy_dto import PolicyBaseDTO, PolicyCreateDTO, PolicyUpdateDTO, PolicyResponseDTO
from insurance_app.application.dto.claim_dto import ClaimBaseDTO, ClaimCreateDTO, ClaimUpdateDTO, ClaimResponseDTO, ClaimApproveDTO
from insurance_app.application.dto.payment_dto import PaymentBaseDTO, PaymentCreateDTO, PaymentUpdateDTO, PaymentResponseDTO, PaymentProcessDTO
from insurance_app.application.dto.user_dto import UserBaseDTO, UserCreateDTO, UserUpdateDTO, UserResponseDTO, TokenDTO, LoginDTO

__all__ = [
    'PaginationDTO',
    'PaginatedResponseDTO',
    'ErrorDTO',
    'ClientBaseDTO',
    'ClientCreateDTO',
    'ClientUpdateDTO',
    'ClientResponseDTO',
    'PolicyBaseDTO',
    'PolicyCreateDTO',
    'PolicyUpdateDTO',
    'PolicyResponseDTO',
    'ClaimBaseDTO',
    'ClaimCreateDTO',
    'ClaimUpdateDTO',
    'ClaimResponseDTO',
    'ClaimApproveDTO',
    'PaymentBaseDTO',
    'PaymentCreateDTO',
    'PaymentUpdateDTO',
    'PaymentResponseDTO',
    'PaymentProcessDTO',
    'UserBaseDTO',
    'UserCreateDTO',
    'UserUpdateDTO',
    'UserResponseDTO',
    'TokenDTO',
    'LoginDTO'
]
