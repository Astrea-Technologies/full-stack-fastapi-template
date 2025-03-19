import uuid
from enum import Enum
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from app.db.models.political_entity import PoliticalEntity


class Platform(str, Enum):
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    OTHER = "other"


class SocialMediaAccount(SQLModel, table=True):
    """
    SocialMediaAccount model for database storage.
    
    This model represents a social media account linked to a political entity
    and is stored in PostgreSQL.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    platform: Platform
    platform_id: str = Field(index=True, max_length=255)
    handle: str = Field(max_length=255)
    name: Optional[str] = Field(default=None, max_length=255)
    url: Optional[str] = Field(default=None, max_length=2083)
    verified: bool = Field(default=False)
    follower_count: Optional[int] = Field(default=None)
    following_count: Optional[int] = Field(default=None)
    
    # Foreign key
    political_entity_id: uuid.UUID = Field(
        foreign_key="politicalentity.id",
        nullable=False,
        ondelete="CASCADE"
    )
    
    # Relationship
    political_entity: PoliticalEntity = Relationship(back_populates="social_media_accounts") 