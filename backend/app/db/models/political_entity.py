import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.db.models.social_media_account import SocialMediaAccount
    from app.db.models.entity_relationship import EntityRelationship


class EntityType(str, Enum):
    POLITICIAN = "politician"
    PARTY = "party"
    ORGANIZATION = "organization"


class PoliticalEntity(SQLModel, table=True):
    """
    PoliticalEntity model for database storage.
    
    This model represents a political entity (politician, party, organization) 
    in the system and is stored in PostgreSQL.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(index=True, max_length=255)
    entity_type: EntityType
    description: Optional[str] = Field(default=None)
    country: Optional[str] = Field(default=None, max_length=100)
    region: Optional[str] = Field(default=None, max_length=100)
    political_alignment: Optional[str] = Field(default=None, max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    social_media_accounts: List["SocialMediaAccount"] = Relationship(
        back_populates="political_entity",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    
    # Relationships for EntityRelationship
    source_relationships: List["EntityRelationship"] = Relationship(
        back_populates="source_entity",
        sa_relationship_kwargs={
            "primaryjoin": "PoliticalEntity.id==EntityRelationship.source_entity_id",
            "cascade": "all, delete-orphan",
        },
    )
    
    target_relationships: List["EntityRelationship"] = Relationship(
        back_populates="target_entity",
        sa_relationship_kwargs={
            "primaryjoin": "PoliticalEntity.id==EntityRelationship.target_entity_id",
            "cascade": "all, delete",
        },
    ) 