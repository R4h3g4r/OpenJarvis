from pydantic import BaseModel, Field, AnyHttpUrl
from typing import Optional
from datetime import datetime
from uuid import UUID

class ContactInfoBase(BaseModel):
    address: Optional[str] = Field(None, description="Dirección del local o estudio")
    whatsapp_number: Optional[str] = Field(None, description="Número de WhatsApp Business")
    email: Optional[str] = Field(None, description="Correo de contacto profesional")

class SocialMediaBase(BaseModel):
    platform: str = Field(..., description="Nombre de la red social (Instagram, TikTok, Facebook)")
    handle: str = Field(..., description="Nombre de usuario o arroba")
    url: AnyHttpUrl = Field(..., description="Enlace directo al perfil")

class ContactInfoCreate(ContactInfoBase):
    pass

class ContactInfoResponse(ContactInfoBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SocialMediaCreate(SocialMediaBase):
    pass

class SocialMediaResponse(SocialMediaBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
