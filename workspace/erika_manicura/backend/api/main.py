from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from repository.database import engine, Base, get_db
from repository import models
from domain import client, service, appointment, gallery, payment, marketing, social
from service import operations

# Crear las tablas en la BD
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Erika Manicura API",
    description="API para gestión de clientes, agendamiento, catálogo, marketing y finanzas",
    version="1.0.0"
)

# Configurar CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todos los orígenes en desarrollo (e.g., localhost:3000)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Clients ---
@app.post("/clients/", response_model=client.ClientResponse, tags=["Clients"])
def create_client(client_in: client.ClientCreate, db: Session = Depends(get_db)):
    return operations.create_client(db=db, client_in=client_in)

@app.get("/clients/", response_model=List[client.ClientResponse], tags=["Clients"])
def read_clients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return operations.get_clients(db, skip=skip, limit=limit)

@app.put("/clients/{client_id}", response_model=client.ClientResponse, tags=["Clients"])
def update_client(client_id: str, client_in: client.ClientCreate, db: Session = Depends(get_db)):
    db_client = operations.update_client(db=db, client_id=client_id, client_in=client_in)
    if not db_client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return db_client

@app.delete("/clients/{client_id}", tags=["Clients"])
def delete_client(client_id: str, db: Session = Depends(get_db)):
    success = operations.delete_client(db=db, client_id=client_id)
    if not success:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return {"status": "success", "message": "Cliente eliminado exitosamente"}

# --- Services ---
@app.post("/services/", response_model=service.ServiceResponse, tags=["Services"])
def create_service(service_in: service.ServiceCreate, db: Session = Depends(get_db)):
    return operations.create_service(db=db, service_in=service_in)

@app.get("/services/", response_model=List[service.ServiceResponse], tags=["Services"])
def read_services(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return operations.get_services(db, skip=skip, limit=limit)

# --- Appointments ---
@app.post("/appointments/", response_model=appointment.AppointmentResponse, tags=["Appointments"])
def create_appointment(appointment_in: appointment.AppointmentCreate, db: Session = Depends(get_db)):
    return operations.create_appointment(db=db, appointment_in=appointment_in)

@app.get("/appointments/", response_model=List[appointment.AppointmentResponse], tags=["Appointments"])
def read_appointments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return operations.get_appointments(db, skip=skip, limit=limit)

@app.post("/appointments/{appointment_id}/cancel", response_model=appointment.AppointmentResponse, tags=["Appointments"])
def cancel_appointment(appointment_id: str, db: Session = Depends(get_db)):
    result = operations.cancel_appointment(db=db, appointment_id=appointment_id)
    if not result:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    return result

@app.put("/appointments/{appointment_id}/status", response_model=appointment.AppointmentResponse, tags=["Appointments"])
def update_appointment_status(appointment_id: str, status: str, db: Session = Depends(get_db)):
    result = operations.update_appointment_status(db=db, appointment_id=appointment_id, status=status)
    if not result:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    return result

# --- Gallery (Book de Fotos) ---
@app.post("/gallery/", response_model=gallery.PhotoResponse, tags=["Gallery"])
def add_photo(photo_in: gallery.PhotoCreate, db: Session = Depends(get_db)):
    return operations.add_photo(db=db, photo_in=photo_in)

# --- Payments & Transfer Info ---
@app.post("/transfer-info/", response_model=payment.TransferInfoResponse, tags=["Payments"])
def set_transfer_info(info_in: payment.TransferInfoCreate, db: Session = Depends(get_db)):
    return operations.set_transfer_info(db=db, info_in=info_in)

@app.get("/transfer-info/", response_model=payment.TransferInfoResponse, tags=["Payments"])
def get_transfer_info(db: Session = Depends(get_db)):
    info = operations.get_transfer_info(db)
    if not info:
        raise HTTPException(status_code=404, detail="Información de transferencia no encontrada")
    return info

# --- Marketing Campaigns ---
@app.post("/campaigns/", response_model=marketing.MarketingCampaignResponse, tags=["Marketing"])
def create_campaign(campaign_in: marketing.MarketingCampaignCreate, db: Session = Depends(get_db)):
    return operations.create_campaign(db=db, campaign_in=campaign_in)

@app.get("/campaigns/", response_model=List[marketing.MarketingCampaignResponse], tags=["Marketing"])
def read_campaigns(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return operations.get_campaigns(db, skip=skip, limit=limit)
