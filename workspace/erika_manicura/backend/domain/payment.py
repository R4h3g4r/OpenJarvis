from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class TransferInfoBase(BaseModel):
    bank_name: str = Field(..., description="Nombre del banco")
    account_type: str = Field(..., description="Tipo de cuenta (Corriente, Vista, RUT, etc.)")
    account_number: str = Field(..., description="Número de cuenta")
    rut: str = Field(..., description="RUT o DNI asociado a la cuenta")
    email: Optional[str] = Field(None, description="Email para comprobantes")
    owner_name: str = Field(..., description="Nombre del titular")

class TransferInfoCreate(TransferInfoBase):
    pass

class TransferInfoResponse(TransferInfoBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ReservationPaymentBase(BaseModel):
    appointment_id: UUID = Field(..., description="ID de la cita reservada")
    amount: float = Field(..., description="Monto transferido por reserva")
    proof_image_url: Optional[str] = Field(None, description="URL del comprobante de pago")
    is_verified: bool = Field(False, description="Indica si el pago fue verificado")

class ReservationPaymentCreate(ReservationPaymentBase):
    pass

class ReservationPaymentResponse(ReservationPaymentBase):
    id: UUID
    created_at: datetime
    verified_at: Optional[datetime]

    class Config:
        from_attributes = True
