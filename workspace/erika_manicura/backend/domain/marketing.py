from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum

class CampaignStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class MarketingCampaignBase(BaseModel):
    title: str = Field(..., description="Título de la campaña (Ej: Promo Día de la Madre)")
    description: str = Field(..., description="Descripción y objetivo de la campaña")
    start_date: datetime = Field(..., description="Fecha de inicio")
    end_date: datetime = Field(..., description="Fecha de término")
    discount_percentage: Optional[float] = Field(None, description="Porcentaje de descuento si aplica")
    status: CampaignStatus = Field(default=CampaignStatus.DRAFT)

class MarketingCampaignCreate(MarketingCampaignBase):
    pass

class MarketingCampaignResponse(MarketingCampaignBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ReelContentBase(BaseModel):
    title: str = Field(..., description="Título o idea del reel")
    script_or_notes: Optional[str] = Field(None, description="Guion o notas para grabar")
    audio_trend: Optional[str] = Field(None, description="Audio en tendencia recomendado")
    status: str = Field(default="idea", description="Estado: idea, grabado, editado, publicado")
    url: Optional[str] = Field(None, description="URL del reel publicado")

class ReelContentCreate(ReelContentBase):
    pass

class ReelContentResponse(ReelContentBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
