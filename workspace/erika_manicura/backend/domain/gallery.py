from pydantic import BaseModel, Field, AnyHttpUrl
from typing import Optional
from datetime import datetime
from uuid import UUID

class PhotoBase(BaseModel):
    title: str = Field(..., description="Título de la foto")
    description: Optional[str] = Field(None, description="Descripción del diseño o trabajo")
    image_url: AnyHttpUrl = Field(..., description="URL o ruta de almacenamiento de la imagen")
    service_id: Optional[UUID] = Field(None, description="ID del servicio asociado (opcional)")
    is_public: bool = Field(True, description="Indica si es visible públicamente en el book")

class PhotoCreate(PhotoBase):
    pass

class PhotoResponse(PhotoBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
