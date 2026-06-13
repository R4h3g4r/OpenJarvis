import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';

const Home: React.FC = () => {
  const [services, setServices] = useState<any[]>([]);
  const [showModal, setShowModal] = useState(false);

  // Form states
  const [clientName, setClientName] = useState('');
  const [clientPhone, setClientPhone] = useState('');
  const [selectedService, setSelectedService] = useState('');
  const [appointmentDate, setAppointmentDate] = useState('');

  useEffect(() => {
    // Fetch active services
    api.getServices().then(data => {
      // Si la bd está vacía, mostramos servicios por defecto con IDs tipo UUID válidos
      if (data.length === 0) {
        setServices([
          { id: 'e08fc52b-c0bf-4074-bcf2-b9cf6d2b31a3', name: 'Manicura Rusa', price: 25000, description: 'Limpieza profunda y esmaltado permanente.' },
          { id: 'f2a1b94e-28f3-4a11-b062-84df12a7bf24', name: 'Uñas Acrílicas', price: 35000, description: 'Esculpido en acrílico con diseño a elección.' },
          { id: 'd597df64-f6df-49bc-8068-bb6452df3bfa', name: 'Kapping Gel', price: 28000, description: 'Baño de gel sobre uña natural para fortalecer.' },
        ]);
      } else {
        setServices(data);
      }
    });
  }, []);

  const handleBookingSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!clientName || !clientPhone || !selectedService || !appointmentDate) {
      alert("Por favor, completa todos los campos.");
      return;
    }

    try {
      // 1. Crear el cliente en la base de datos (CRM)
      // Omitimos enviar email y handle de instagram en null para evitar fallos de validación en Pydantic
      const newClient = await api.createClient({
        name: clientName,
        phone: clientPhone,
        notes: "Registrado vía reserva web"
      });

      if (!newClient || !newClient.id) {
        throw new Error("No se pudo registrar el cliente en el backend.");
      }

      // Si el servicio seleccionado es de los por defecto y no existe en BD, lo creamos primero para evitar FK errors
      let serviceId = selectedService;
      const dbServices = await api.getServices();
      const serviceExists = dbServices.some((s: any) => s.id === selectedService);
      
      if (!serviceExists) {
        const fallbackService = services.find(s => s.id === selectedService);
        if (fallbackService) {
          const createdService = await api.createService({
            name: fallbackService.name,
            description: fallbackService.description,
            price: fallbackService.price,
            duration_minutes: 60,
            is_active: true
          });
          serviceId = createdService.id;
        }
      }

      // 2. Crear la cita enlazada con el cliente y el servicio real
      await api.createAppointment({
        client_id: newClient.id,
        service_id: serviceId,
        appointment_date: new Date(appointmentDate).toISOString(),
        status: 'pending',
        notes: "Reserva en línea"
      });

      alert("¡Solicitud de reserva enviada con éxito! Nos contactaremos contigo a la brevedad para realizar el abono y confirmar tu reserva.");
      setShowModal(false);

      // Limpiar campos
      setClientName('');
      setClientPhone('');
      setSelectedService('');
      setAppointmentDate('');
    } catch (error) {
      console.error(error);
      alert("Ocurrió un error al procesar tu reserva. Asegúrate de tener el backend corriendo.");
    }
  };

  return (
    <div className="home-container">
      {/* Header */}
      <header className="header">
        <div className="logo">Erika Manicura</div>
        <nav className="nav">
          <a href="#services">Servicios</a>
          <a href="#gallery">Book de Fotos</a>
          <a href="#contact">Contacto</a>
          <button className="btn-book" onClick={() => setShowModal(true)}>Reserva tu hora</button>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <h1>Elegancia y detalle en tus manos.</h1>
          <p>Especialistas en Manicura Rusa, Acrílicas y Kapping. Un espacio diseñado para tu bienestar.</p>
          <button className="btn-primary" onClick={() => setShowModal(true)}>Agendar Cita</button>
        </div>
      </section>

      {/* Services Section */}
      <section id="services" className="services-section">
        <h2>Nuestros Servicios</h2>
        <div className="services-grid">
          {services.map(srv => (
            <div key={srv.id} className="service-card">
              <h3>{srv.name}</h3>
              <p>{srv.description}</p>
              <span className="price">${srv.price.toLocaleString()}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer id="contact" className="footer">
        <p>© 2026 Erika Manicura. Todos los derechos reservados.</p>
        <div className="social-links">
          <a href="#">Instagram</a> | <a href="#">WhatsApp</a> | <Link to="/admin" style={{ color: 'var(--accent-color)', opacity: 0.6, textDecoration: 'none' }}>Acceso Admin</Link>
        </div>
      </footer>

      {/* Appointment Modal */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal">
            <button className="close-btn" onClick={() => setShowModal(false)}>×</button>
            <h2>Reserva tu hora</h2>
            <form className="booking-form" onSubmit={handleBookingSubmit}>
              <input 
                type="text" 
                placeholder="Nombre completo" 
                required 
                value={clientName} 
                onChange={(e) => setClientName(e.target.value)} 
              />
              <input 
                type="tel" 
                placeholder="Teléfono" 
                required 
                value={clientPhone} 
                onChange={(e) => setClientPhone(e.target.value)} 
              />
              <select 
                required 
                value={selectedService} 
                onChange={(e) => setSelectedService(e.target.value)}
              >
                <option value="">Selecciona un servicio</option>
                {services.map(srv => <option key={srv.id} value={srv.id}>{srv.name}</option>)}
              </select>
              <input 
                type="datetime-local" 
                required 
                value={appointmentDate} 
                onChange={(e) => setAppointmentDate(e.target.value)} 
              />
              <button type="submit" className="btn-primary">Confirmar Reserva</button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Home;
