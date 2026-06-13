from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID

from repository import models
from domain import client, service, appointment, gallery, payment, marketing, social

# Client Services
def create_client(db: Session, client_in: client.ClientCreate):
    db_client = models.Client(**client_in.dict())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

def get_clients(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Client).offset(skip).limit(limit).all()

def update_client(db: Session, client_id: str, client_in: client.ClientCreate):
    db_client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if db_client:
        db_client.name = client_in.name
        db_client.phone = client_in.phone
        db_client.email = client_in.email
        db_client.instagram_handle = client_in.instagram_handle
        db_client.notes = client_in.notes
        db.commit()
        db.refresh(db_client)
    return db_client

def delete_client(db: Session, client_id: str):
    db_client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if db_client:
        # Primero eliminar citas asociadas si existieran para evitar errores de FK
        db.query(models.Appointment).filter(models.Appointment.client_id == client_id).delete()
        db.delete(db_client)
        db.commit()
        return True
    return False

# Service Services
def create_service(db: Session, service_in: service.ServiceCreate):
    db_service = models.Service(**service_in.dict())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

def get_services(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Service).offset(skip).limit(limit).all()

# Appointment Services
def create_appointment(db: Session, appointment_in: appointment.AppointmentCreate):
    db_appointment = models.Appointment(
        client_id=str(appointment_in.client_id),
        service_id=str(appointment_in.service_id),
        appointment_date=appointment_in.appointment_date,
        status=appointment_in.status.value,
        notes=appointment_in.notes
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

def get_appointments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Appointment).offset(skip).limit(limit).all()

def update_appointment_status(db: Session, appointment_id: str, status: str):
    db_appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if db_appointment:
        db_appointment.status = status
        db.commit()
        db.refresh(db_appointment)
    return db_appointment

# Gallery Services
def add_photo(db: Session, photo_in: gallery.PhotoCreate):
    db_photo = models.GalleryPhoto(
        title=photo_in.title,
        description=photo_in.description,
        image_url=str(photo_in.image_url),
        service_id=str(photo_in.service_id) if photo_in.service_id else None,
        is_public=photo_in.is_public
    )
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)
    return db_photo

# Payment Services
def set_transfer_info(db: Session, info_in: payment.TransferInfoCreate):
    db_info = models.TransferInfo(**info_in.dict())
    db.add(db_info)
    db.commit()
    db.refresh(db_info)
    return db_info

def get_transfer_info(db: Session):
    return db.query(models.TransferInfo).filter(models.TransferInfo.is_active == True).first()

# Marketing Services
def create_campaign(db: Session, campaign_in: marketing.MarketingCampaignCreate):
    db_camp = models.MarketingCampaign(
        title=campaign_in.title,
        description=campaign_in.description,
        start_date=campaign_in.start_date,
        end_date=campaign_in.end_date,
        discount_percentage=campaign_in.discount_percentage,
        status=campaign_in.status.value
    )
    db.add(db_camp)
    db.commit()
    db.refresh(db_camp)
    return db_camp

def get_campaigns(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.MarketingCampaign).offset(skip).limit(limit).all()

def publish_to_meta(db: Session, campaign_id: str):
    # Simulación de llamada a Graph API de Meta (Facebook/Instagram)
    # Aquí iría requests.post('https://graph.facebook.com/v19.0/me/feed', data={...})
    db_camp = db.query(models.MarketingCampaign).filter(models.MarketingCampaign.id == campaign_id).first()
    if db_camp:
        db_camp.status = "active"
        db.commit()
        db.refresh(db_camp)
    return {"status": "success", "message": f"Campaña y feed '{db_camp.title if db_camp else ''}' publicados exitosamente en Facebook e Instagram"}
