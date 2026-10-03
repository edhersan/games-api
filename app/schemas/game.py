from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing_extensions import Annotated
from pydantic.functional_validators import BeforeValidator
from typing import Optional, List, Dict, Any
import re
from datetime import datetime


def validate_object_id(v: str) -> str:
    if not ObjectId.is_valid(v):
        raise ValueError("Invalid ObjectId")
    return v


PyObjectId = Annotated[str, BeforeValidator(validate_object_id)]


URL_PATTERN = re.compile(
    r'^https?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


def validate_url(v: str) -> str:
    if v and not URL_PATTERN.match(v):
        raise ValueError("URL inválida")
    return v


class Screenshot(BaseModel):
    id: Optional[int] = None
    image: str


class SystemRequirements(BaseModel):
    os: Optional[str] = None
    processor: Optional[str] = None
    memory: Optional[str] = None
    graphics: Optional[str] = None
    storage: Optional[str] = None


class GameBase(BaseModel):
    """Esquema base compatible con freetogame API"""
    title: str = Field(..., min_length=1, max_length=200)
    platform: Optional[str] = None
    genre: Optional[str] = None
    release_date: Optional[str] = None
    release_year: Optional[int] = Field(None, ge=1970, le=2030)
    game_id: Optional[int] = None
    thumbnail: Optional[str] = None
    short_description: Optional[str] = None
    description: Optional[str] = None
    game_url: Optional[str] = None
    publisher: Optional[str] = None
    developer: Optional[str] = None
    minimum_system_requirements: Optional[SystemRequirements] = None
    screenshots: List[Screenshot] = Field(default_factory=list)

    @field_validator("thumbnail", "game_url", mode="before")
    @classmethod
    def validate_urls(cls, v):
        return validate_url(v)

    @field_validator("release_year", mode="before")
    @classmethod
    def extract_year_from_date(cls, v):
        if v is not None:
            return v
        return None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="allow"
    )


class GameCreate(GameBase):
    pass


class GameUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    platform: Optional[str] = None
    genre: Optional[str] = None
    release_date: Optional[str] = None
    release_year: Optional[int] = Field(None, ge=1970, le=2030)
    thumbnail: Optional[str] = None
    short_description: Optional[str] = None
    description: Optional[str] = None
    game_url: Optional[str] = None
    publisher: Optional[str] = None
    developer: Optional[str] = None
    minimum_system_requirements: Optional[SystemRequirements] = None
    screenshots: Optional[List[Screenshot]] = None


class GameResponse(GameBase):
    id: str = Field(alias="_id")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="allow"
    )


class GameArtResponse(BaseModel):
    id: str = Field(alias="_id")
    title: str
    thumbnail: Optional[str] = None
    screenshots: List[Screenshot] = Field(default_factory=list)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="allow"
    )


class GameInfoResponse(BaseModel):
    id: str = Field(alias="_id")
    title: str
    short_description: Optional[str] = None
    description: Optional[str] = None
    publisher: Optional[str] = None
    developer: Optional[str] = None
    genre: Optional[str] = None
    platform: Optional[str] = None
    release_date: Optional[str] = None
    game_url: Optional[str] = None
    minimum_system_requirements: Optional[SystemRequirements] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="allow"
    )


class GameFullResponse(GameResponse):
    pass