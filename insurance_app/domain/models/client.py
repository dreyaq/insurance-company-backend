from dataclasses import dataclass
from datetime import date
from typing import Optional
from uuid import UUID


@dataclass
class Client:
    id: Optional[UUID] = None
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: str = ""
    birth_date: Optional[date] = None
    address: str = ""
    passport_number: str = ""
    created_at: Optional[date] = None
    is_active: bool = True