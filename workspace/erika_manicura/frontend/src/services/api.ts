const API_URL = 'http://localhost:8000';

export const api = {
  // Services
  getServices: async () => {
    try {
      const response = await fetch(`${API_URL}/services/`);
      if (!response.ok) return [];
      return await response.json();
    } catch {
      return [];
    }
  },

  createService: async (data: any) => {
    const response = await fetch(`${API_URL}/services/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return response.json();
  },
  
  // Appointments
  createAppointment: async (data: any) => {
    const response = await fetch(`${API_URL}/appointments/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return response.json();
  },
  
  getAppointments: async () => {
    try {
      const response = await fetch(`${API_URL}/appointments/`);
      if (!response.ok) return [];
      return await response.json();
    } catch {
      return [];
    }
  },

  updateAppointmentStatus: async (id: string, status: string) => {
    const response = await fetch(`${API_URL}/appointments/${id}/status?status=${encodeURIComponent(status)}`, {
      method: 'PUT'
    });
    return response.json();
  },

  // Clients
  createClient: async (data: any) => {
    const response = await fetch(`${API_URL}/clients/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return response.json();
  },

  getClients: async () => {
    try {
      const response = await fetch(`${API_URL}/clients/`);
      if (!response.ok) return [];
      return await response.json();
    } catch {
      return [];
    }
  },

  updateClient: async (id: string, data: any) => {
    const response = await fetch(`${API_URL}/clients/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return response.json();
  },

  deleteClient: async (id: string) => {
    const response = await fetch(`${API_URL}/clients/${id}`, {
      method: 'DELETE'
    });
    return response.json();
  },
  
  // Campaigns
  getCampaigns: async () => {
    try {
      const response = await fetch(`${API_URL}/campaigns/`);
      if (!response.ok) return [];
      return await response.json();
    } catch {
      return [];
    }
  },
  
  createCampaign: async (data: any) => {
    const response = await fetch(`${API_URL}/campaigns/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return response.json();
  },
  
  publishToMeta: async (campaignId: string) => {
    const response = await fetch(`${API_URL}/meta/publish/${campaignId}`, { method: 'POST' });
    return response.json();
  }
};
