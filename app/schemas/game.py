from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing_extensions import Annotated
from pydantic.functional_validators import BeforeValidator
from typing import Optional, List
import re
from pydantic_core import core_schema


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


class GameBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    platform: str = Field(..., min_length=1)
    genre: str = Field(..., min_length=1)
    release_year: int = Field(..., ge=1970, le=2030)


class GameArt(BaseModel):
    cover_url: Optional[str] = Field(None, description="URL de la portada del juego")
    screenshots: List[str] = Field(default_factory=list, description="Capturas de pantalla")
    background_url: Optional[str] = Field(None, description="Imagen de fondo/banner")
    icon_url: Optional[str] = Field(None, description="Icono del juego")

    @field_validator("cover_url", "background_url", "icon_url", mode="before")
    @classmethod
    def validate_single_url(cls, v):
        return validate_url(v)

    @field_validator("screenshots", mode="before")
    @classmethod
    def validate_screenshots(cls, v):
        if isinstance(v, list):
            return [validate_url(url) for url in v]
        return v


class GameInfo(BaseModel):
    description: Optional[str] = Field(None, description="Descripción completa del juego")
    short_description: Optional[str] = Field(None, max_length=500, description="Descripción corta")
    developer: Optional[str] = Field(None, description="Desarrollador")
    publisher: Optional[str] = Field(None, description="Publicador")
    esrb_rating: Optional[str] = Field(None, description="Clasificación ESRB")
    pegi_rating: Optional[str] = Field(None, description="Clasificación PEGI")
    players: Optional[str] = Field(None, description="Modos de juego (ej: Single-player, Multiplayer)")
    languages: List[str] = Field(default_factory=list, description="Idiomas soportados")


class GameFullInfo(GameInfo):
    system_requirements: Optional[dict] = Field(None, description="Requisitos del sistema (min/recomendados)")
    release_dates: dict = Field(default_factory=dict, description="Fechas de lanzamiento por región")
    tags: List[str] = Field(default_factory=list, description="Etiquetas/géneros adicionales")
    website: Optional[str] = Field(None, description="Sitio web oficial")
    trailer_url: Optional[str] = Field(None, description="URL del trailer")

    @field_validator("website", "trailer_url", mode="before")
    @classmethod
    def validate_urls(cls, v):
        return validate_url(v)


class GameCreate(GameBase):
    art: Optional[GameArt] = None
    info: Optional[GameInfo] = None
    full_info: Optional[GameFullInfo] = None


class GameUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    platform: Optional[str] = None
    genre: Optional[str] = None
    release_year: Optional[int] = Field(None, ge=1970, le=2030)
    art: Optional[GameArt] = None
    info: Optional[GameInfo] = None
    full_info: Optional[GameFullInfo] = None


class GameResponse(GameBase):
    id: str = Field(alias="_id")
    art: Optional[GameArt] = None
    info: Optional[GameInfo] = None
    full_info: Optional[GameFullInfo] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class GameArtResponse(BaseModel):
    id: str = Field(alias="_id")
    title: str
    art: Optional[GameArt] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class GameInfoResponse(BaseModel):
    id: str = Field(alias="_id")
    title: str
    info: Optional[GameInfo] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class GameFullResponse(BaseModel):
    id: str = Field(alias="_id")
    title: str
    platform: str
    genre: str
    release_year: int
    art: Optional[GameArt] = None
    info: Optional[GameInfo] = None
    full_info: Optional[GameFullInfo] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )