from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from enum import Enum

class AppointmentStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"

class AppointmentBase(BaseModel):
    client_id: UUID = Field(..., description="ID del cliente")
    service_id: UUID = Field(..., description="ID del servicio")
    appointment_date: datetime = Field(..., description="Fecha y hora de la cita")
    status: AppointmentStatus = Field(default=AppointmentStatus.PENDING, description="Estado de la cita")
    notes: Optional[str] = Field(None, description="Notas adicionales para la cita")

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentResponse(AppointmentBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
