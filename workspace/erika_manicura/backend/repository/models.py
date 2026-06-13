from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Client(Base):
    __tablename__ = "clients"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    name = Column(String, index=True, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, index=True, nullable=True)
    instagram_handle = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    appointments = relationship("Appointment", back_populates="client")

class Service(Base):
    __tablename__ = "services"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    appointments = relationship("Appointment", back_populates="service")

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    client_id = Column(String, ForeignKey("clients.id"))
    service_id = Column(String, ForeignKey("services.id"))
    appointment_date = Column(DateTime, nullable=False)
    status = Column(String, default="pending")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    client = relationship("Client", back_populates="appointments")
    service = relationship("Service", back_populates="appointments")
    payment = relationship("ReservationPayment", back_populates="appointment", uselist=False)

class ReservationPayment(Base):
    __tablename__ = "reservation_payments"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    appointment_id = Column(String, ForeignKey("appointments.id"))
    amount = Column(Float, nullable=False)
    proof_image_url = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    verified_at = Column(DateTime, nullable=True)

    appointment = relationship("Appointment", back_populates="payment")

class GalleryPhoto(Base):
    __tablename__ = "gallery_photos"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String, nullable=False)
    service_id = Column(String, ForeignKey("services.id"), nullable=True)
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class TransferInfo(Base):
    __tablename__ = "transfer_info"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    bank_name = Column(String, nullable=False)
    account_type = Column(String, nullable=False)
    account_number = Column(String, nullable=False)
    rut = Column(String, nullable=False)
    email = Column(String, nullable=True)
    owner_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MarketingCampaign(Base):
    __tablename__ = "marketing_campaigns"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    discount_percentage = Column(Float, nullable=True)
    status = Column(String, default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ReelContent(Base):
    __tablename__ = "reel_contents"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    title = Column(String, nullable=False)
    script_or_notes = Column(Text, nullable=True)
    audio_trend = Column(String, nullable=True)
    status = Column(String, default="idea")
    url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ContactSocial(Base):
    __tablename__ = "contact_socials"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    type = Column(String, nullable=False) # 'address', 'whatsapp', 'email', 'instagram', 'tiktok', etc.
    value = Column(String, nullable=False)
    url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
