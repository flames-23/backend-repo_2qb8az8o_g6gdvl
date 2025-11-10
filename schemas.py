"""
Database Schemas for PromptToTube

Each Pydantic model represents a collection in MongoDB.
Collection name is the lowercase class name.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Literal

class VideoProject(BaseModel):
    """
    Video projects created from a text/voice prompt.
    Collection name: "videoproject"
    """
    prompt: str = Field(..., description="User prompt describing the video to create")
    mode: Literal["short", "long"] = Field("short", description="Video format: short or long")
    duration_sec: int = Field(..., ge=10, le=3600, description="Target duration in seconds")
    language: str = Field("en", description="Language for narration/captions")
    voice: Optional[str] = Field(None, description="Selected AI voice id/name")
    template: Optional[str] = Field(None, description="Selected visual template")
    brand_name: Optional[str] = Field(None, description="Brand name for watermark/branding")
    status: Literal["created", "generating", "generated", "error"] = Field("created")

    # Generated assets / metadata
    script: Optional[str] = Field(None, description="Generated narration/script")
    title: Optional[str] = Field(None, description="SEO optimized title")
    tags: Optional[List[str]] = Field(default_factory=list, description="SEO tags")
    suggestions: Optional[List[str]] = Field(default_factory=list, description="AI edit suggestions")
    thumbnail_url: Optional[str] = None
    video_url: Optional[str] = None
    captions_srt: Optional[str] = None

class AssetRequest(BaseModel):
    """
    Minimal payload for creating a new project
    """
    prompt: str
    mode: Literal["short", "long"] = "short"
    duration_sec: int = 60
    language: str = "en"
    voice: Optional[str] = None
    template: Optional[str] = None
    brand_name: Optional[str] = None
