import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from app.db.models.political_entity import PoliticalEntity


class RelationshipType(str, Enum):
    ALLY = "ally"
    OPPONENT = "opponent"
    NEUTRAL = "neutral"


class EntityRelationship(SQLModel, table=True):
    """
    EntityRelationship model for database storage.
    
    This model represents a relationship between two political entities
    and is stored in PostgreSQL.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    relationship_type: RelationshipType
    strength: float = Field(default=0.5, ge=0.0, le=1.0)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    # Foreign keys
    source_entity_id: uuid.UUID = Field(
        foreign_key="politicalentity.id",
        nullable=False,
        ondelete="CASCADE"
    )
    target_entity_id: uuid.UUID = Field(
        foreign_key="politicalentity.id",
        nullable=False,
        ondelete="CASCADE"
    )
    
    # Relationships
    source_entity: PoliticalEntity = Relationship(
        back_populates="source_relationships",
        sa_relationship_kwargs={"foreign_keys": "EntityRelationship.source_entity_id"}
    )
    target_entity: PoliticalEntity = Relationship(
        back_populates="target_relationships",
        sa_relationship_kwargs={"foreign_keys": "EntityRelationship.target_entity_id"}
    ) 