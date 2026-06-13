from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4

class ClientBase(BaseModel):
    name: str = Field(..., description="Nombre del cliente")
    phone: str = Field(..., description="Teléfono de contacto")
    email: Optional[EmailStr] = Field(None, description="Correo electrónico")
    instagram_handle: Optional[str] = Field(None, description="Usuario de Instagram")
    notes: Optional[str] = Field(None, description="Notas adicionales sobre el cliente")

class ClientCreate(ClientBase):
    pass

class ClientResponse(ClientBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
