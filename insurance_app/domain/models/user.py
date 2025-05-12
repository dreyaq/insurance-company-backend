from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from uuid import UUID


@dataclass
class User:
    id: Optional[UUID] = None
    username: str = ""
    email: str = ""
    full_name: str = ""
    hashed_password: str = ""
    is_active: bool = True
    is_superuser: bool = False
    roles: List[str] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.roles is None:
            self.roles = ["user"]
