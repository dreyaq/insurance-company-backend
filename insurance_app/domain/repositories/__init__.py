"""
This module is deprecated and should not be used.
Repository interfaces are now located in insurance_app.application.interfaces.
"""

# Keep only the UserRepository for backward compatibility
from .user_repository import UserRepository

__all__ = [
    'UserRepository'
]
