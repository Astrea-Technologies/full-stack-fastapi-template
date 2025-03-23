"""
MongoDB schema definitions using Pydantic models.

This module defines Pydantic models for MongoDB collections used for
storing social media content and engagement data in the Political
Social Media Analysis Platform.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class PostContent(BaseModel):
    """Content sub-schema for social media posts."""
    text: str
    media: List[HttpUrl] = []
    links: List[HttpUrl] = []
    hashtags: List[str] = []
    mentions: List[str] = []
    
    class Config:
        schema_extra = {
            "example": {
                "text": "Excited to announce our new policy on #ClimateChange with @EPA",
                "media": ["https://example.com/image1.jpg", "https://example.com/image2.jpg"],
                "links": ["https://example.com/policy"],
                "hashtags": ["ClimateChange", "GreenFuture"],
                "mentions": ["EPA", "WhiteHouse"]
            }
        }


class PostMetadata(BaseModel):
    """Metadata sub-schema for social media posts."""
    created_at: datetime
    language: str
    location: Optional[Dict[str, Any]] = None
    client: Optional[str] = None
    is_repost: bool = False
    is_reply: bool = False
    
    class Config:
        schema_extra = {
            "example": {
                "created_at": "2023-06-15T14:32:19Z",
                "language": "en",
                "location": {"country": "USA", "state": "DC"},
                "client": "Twitter Web App",
                "is_repost": False,
                "is_reply": False
            }
        }


class PostEngagement(BaseModel):
    """Engagement metrics sub-schema for social media posts."""
    likes_count: int = 0
    shares_count: int = 0
    comments_count: int = 0
    views_count: Optional[int] = None
    engagement_rate: Optional[float] = None
    
    class Config:
        schema_extra = {
            "example": {
                "likes_count": 1245,
                "shares_count": 327,
                "comments_count": 89,
                "views_count": 15720,
                "engagement_rate": 3.8
            }
        }


class PostAnalysis(BaseModel):
    """Content analysis sub-schema for social media posts."""
    sentiment_score: Optional[float] = None
    topics: List[str] = []
    entities_mentioned: List[str] = []
    key_phrases: List[str] = []
    emotional_tone: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "sentiment_score": 0.64,
                "topics": ["climate", "environment", "policy"],
                "entities_mentioned": ["EPA", "Climate Change Initiative"],
                "key_phrases": ["new policy", "climate action", "sustainable future"],
                "emotional_tone": "positive"
            }
        }


class SocialMediaPost(BaseModel):
    """
    Schema for social media posts stored in MongoDB.
    
    This model represents a post from various social media platforms
    including its content, metadata, engagement metrics, and analysis.
    """
    platform_id: str = Field(..., description="Original ID from the social media platform")
    platform: str = Field(..., description="Social media platform name (e.g., twitter, facebook)")
    account_id: UUID = Field(..., description="Reference to PostgreSQL SocialMediaAccount UUID")
    content_type: str = Field(..., description="Type of post (e.g., post, story, video)")
    
    content: PostContent
    metadata: PostMetadata
    engagement: PostEngagement
    analysis: Optional[PostAnalysis] = None
    vector_id: Optional[str] = Field(None, description="Reference to vector database entry")
    
    class Config:
        schema_extra = {
            "example": {
                "platform_id": "1458794356725891073",
                "platform": "twitter",
                "account_id": "123e4567-e89b-12d3-a456-426614174000",
                "content_type": "post",
                "content": {
                    "text": "Excited to announce our new policy on #ClimateChange with @EPA",
                    "media": ["https://example.com/image1.jpg"],
                    "links": ["https://example.com/policy"],
                    "hashtags": ["ClimateChange", "GreenFuture"],
                    "mentions": ["EPA", "WhiteHouse"]
                },
                "metadata": {
                    "created_at": "2023-06-15T14:32:19Z",
                    "language": "en",
                    "location": {"country": "USA", "state": "DC"},
                    "client": "Twitter Web App",
                    "is_repost": False,
                    "is_reply": False
                },
                "engagement": {
                    "likes_count": 1245,
                    "shares_count": 327,
                    "comments_count": 89,
                    "views_count": 15720,
                    "engagement_rate": 3.8
                },
                "analysis": {
                    "sentiment_score": 0.64,
                    "topics": ["climate", "environment", "policy"],
                    "entities_mentioned": ["EPA", "Climate Change Initiative"],
                    "key_phrases": ["new policy", "climate action", "sustainable future"],
                    "emotional_tone": "positive"
                },
                "vector_id": "vec_123456789"
            }
        }


class CommentContent(BaseModel):
    """Content sub-schema for social media comments."""
    text: str
    media: Optional[List[HttpUrl]] = None
    mentions: List[str] = []
    
    class Config:
        schema_extra = {
            "example": {
                "text": "Great initiative! @GreenOrg should partner on this",
                "media": ["https://example.com/comment-img.jpg"],
                "mentions": ["GreenOrg"]
            }
        }


class CommentMetadata(BaseModel):
    """Metadata sub-schema for social media comments."""
    created_at: datetime
    language: str
    location: Optional[Dict[str, Any]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "created_at": "2023-06-15T15:45:22Z",
                "language": "en",
                "location": {"country": "USA", "state": "CA"}
            }
        }


class CommentEngagement(BaseModel):
    """Engagement metrics sub-schema for social media comments."""
    likes_count: int = 0
    replies_count: int = 0
    
    class Config:
        schema_extra = {
            "example": {
                "likes_count": 45,
                "replies_count": 3
            }
        }


class CommentAnalysis(BaseModel):
    """Content analysis sub-schema for social media comments."""
    sentiment_score: Optional[float] = None
    emotional_tone: Optional[str] = None
    toxicity_flag: Optional[bool] = None
    entities_mentioned: List[str] = []
    
    class Config:
        schema_extra = {
            "example": {
                "sentiment_score": 0.78,
                "emotional_tone": "positive",
                "toxicity_flag": False,
                "entities_mentioned": ["GreenOrg"]
            }
        }


class SocialMediaComment(BaseModel):
    """
    Schema for social media comments stored in MongoDB.
    
    This model represents a comment on a social media post including
    its content, metadata, engagement metrics, and analysis.
    """
    platform_id: str = Field(..., description="Original ID from the social media platform")
    platform: str = Field(..., description="Social media platform name (e.g., twitter, facebook)")
    post_id: str = Field(..., description="Reference to MongoDB post ID")
    user_id: str = Field(..., description="User ID from the platform")
    user_name: str = Field(..., description="User name from the platform")
    
    content: CommentContent
    metadata: CommentMetadata
    engagement: CommentEngagement
    analysis: Optional[CommentAnalysis] = None
    vector_id: Optional[str] = Field(None, description="Reference to vector database entry")
    
    class Config:
        schema_extra = {
            "example": {
                "platform_id": "1458812639457283072",
                "platform": "twitter",
                "post_id": "1458794356725891073",
                "user_id": "987654321",
                "user_name": "EcoAdvocate",
                "content": {
                    "text": "Great initiative! @GreenOrg should partner on this",
                    "media": ["https://example.com/comment-img.jpg"],
                    "mentions": ["GreenOrg"]
                },
                "metadata": {
                    "created_at": "2023-06-15T15:45:22Z",
                    "language": "en",
                    "location": {"country": "USA", "state": "CA"}
                },
                "engagement": {
                    "likes_count": 45,
                    "replies_count": 3
                },
                "analysis": {
                    "sentiment_score": 0.78,
                    "emotional_tone": "positive",
                    "toxicity_flag": False,
                    "entities_mentioned": ["GreenOrg"]
                },
                "vector_id": "vec_987654321"
            }
        } 