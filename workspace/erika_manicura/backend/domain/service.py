from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class ServiceBase(BaseModel):
    name: str = Field(..., description="Nombre del servicio (e.g. Manicura Rusa)")
    description: Optional[str] = Field(None, description="Descripción del servicio")
    price: float = Field(..., description="Valor del servicio")
    duration_minutes: int = Field(..., description="Duración estimada en minutos")
    is_active: bool = Field(True, description="Indica si el servicio está disponible actualmente")

class ServiceCreate(ServiceBase):
    pass

class ServiceResponse(ServiceBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
