# Re-exports to maintain backward compatibility
# While the codebase transitions to the new structure

# SQL Models
from app.models.sql.user import (
    User,
    UserBase,
    UserCreate,
    UserRegister,
    UserUpdate,
    UserUpdateMe,
    UpdatePassword,
    UserPublic,
    UsersPublic,
)
from app.models.sql.item import (
    Item,
    ItemBase,
    ItemCreate,
    ItemUpdate,
    ItemPublic,
    ItemsPublic,
)

# Schemas
from app.models.schemas.auth import Token, TokenPayload, NewPassword
from app.models.schemas.base import Message
