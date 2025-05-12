class DomainException(Exception):
    """Базовое исключение для всех доменных исключений"""
    pass


class EntityNotFoundException(DomainException):
    """Исключение, возникающее при отсутствии запрашиваемой сущности"""
    def __init__(self, entity_type: str, entity_id: str):
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(f"{entity_type} с ID {entity_id} не найден")


class BusinessRuleViolationException(DomainException):
    """Исключение, возникающее при нарушении бизнес-правил"""
    pass


class InvalidOperationException(DomainException):
    """Исключение, возникающее при попытке выполнения недопустимой операции"""
    pass


class AuthenticationException(DomainException):
    """Исключение, возникающее при ошибке аутентификации"""
    pass


class AuthorizationException(DomainException):
    """Исключение, возникающее при ошибке авторизации"""
    def __init__(self, required_role: str = None):
        if required_role:
            message = f"Недостаточно прав. Требуется роль: {required_role}"
        else:
            message = "Недостаточно прав"
        super().__init__(message)