import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { 
  Box, Drawer, AppBar, Toolbar, List, Typography, Divider, IconButton, 
  ListItem, ListItemButton, ListItemIcon, ListItemText, CssBaseline, 
  Grid, Card, CardContent, Table, TableBody, TableCell, TableHead, TableRow, 
  Button, TextField, Paper, Chip, Select, MenuItem, Modal, CardActions
} from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import PeopleIcon from '@mui/icons-material/People';
import CampaignIcon from '@mui/icons-material/Campaign';
import EventBusyIcon from '@mui/icons-material/EventBusy';
import PublishIcon from '@mui/icons-material/Publish';
import LogoutIcon from '@mui/icons-material/Logout';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';

const drawerWidth = 260;

const Admin: React.FC = () => {
  const navigate = useNavigate();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState('');
  const [activeTab, setActiveTab] = useState('appointments');
  const [appointments, setAppointments] = useState<any[]>([]);
  const [clients, setClients] = useState<any[]>([]);
  const [campaigns, setCampaigns] = useState<any[]>([]);
  
  // Marketing states
  const [campTitle, setCampTitle] = useState('');
  const [campDesc, setCampDesc] = useState('');

  // Editing Client states
  const [editingClient, setEditingClient] = useState<any | null>(null);
  const [editName, setEditName] = useState('');
  const [editPhone, setEditPhone] = useState('');
  const [editEmail, setEditEmail] = useState('');
  const [editInstagram, setEditInstagram] = useState('');
  const [editNotes, setEditNotes] = useState('');

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (password === 'admin123') { 
      setIsAuthenticated(true);
      fetchData();
    } else {
      alert('Contraseña incorrecta');
    }
  };

  const fetchData = async () => {
    setAppointments(await api.getAppointments());
    setClients(await api.getClients());
    setCampaigns(await api.getCampaigns());
  };

  const handleStatusChange = async (appointmentId: string, newStatus: string) => {
    await api.updateAppointmentStatus(appointmentId, newStatus);
    fetchData();
  };

  const handleStartEditClient = (client: any) => {
    setEditingClient(client);
    setEditName(client.name);
    setEditPhone(client.phone);
    setEditEmail(client.email || '');
    setEditInstagram(client.instagram_handle || '');
    setEditNotes(client.notes || '');
  };

  const handleSaveClient = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingClient) return;
    
    const payload = {
      name: editName,
      phone: editPhone,
      email: editEmail || null,
      instagram_handle: editInstagram || null,
      notes: editNotes || null
    };

    await api.updateClient(editingClient.id, payload);
    setEditingClient(null);
    fetchData();
  };

  const handleDeleteClient = async (clientId: string) => {
    if (window.confirm("¿Seguro que deseas eliminar este cliente? Se eliminarán todas sus citas asociadas.")) {
      await api.deleteClient(clientId);
      fetchData();
    }
  };

  const handleCreateCampaign = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!campTitle || !campDesc) return;
    const payload = {
      title: campTitle,
      description: campDesc,
      start_date: new Date().toISOString(),
      end_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
      discount_percentage: 10.0,
      status: 'draft'
    };
    await api.createCampaign(payload);
    setCampTitle('');
    setCampDesc('');
    fetchData();
  };

  const handlePublishMeta = async (id: string) => {
    const res = await api.publishToMeta(id);
    alert(res.message);
    fetchData();
  };

  if (!isAuthenticated) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh" bgcolor="#f8f1ef">
        <Paper elevation={3} sx={{ p: 4, width: 350, textAlign: 'center' }}>
          <Typography variant="h5" mb={3}>Panel Administrativo</Typography>
          <form onSubmit={handleLogin}>
            <TextField fullWidth type="password" label="Contraseña" value={password} onChange={(e) => setPassword(e.target.value)} sx={{ mb: 2 }} />
            <Button fullWidth variant="contained" type="submit" sx={{ bgcolor: '#a87b6d', '&:hover': { bgcolor: '#8b6458' } }}>Ingresar</Button>
          </form>
        </Paper>
      </Box>
    );
  }

  const renderContent = () => {
    if (activeTab === 'appointments') {
      return (
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card sx={{ bgcolor: '#dcb3a6', color: '#fff' }}>
              <CardContent>
                <Typography variant="h6">Total Citas</Typography>
                <Typography variant="h3">{appointments.length}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" mb={2}>Gestión de Citas</Typography>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Fecha</TableCell>
                    <TableCell>Estado</TableCell>
                    <TableCell>Cambiar Estado</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {appointments.map(app => (
                    <TableRow key={app.id}>
                      <TableCell>{new Date(app.appointment_date).toLocaleString()}</TableCell>
                      <TableCell>
                        <Chip 
                          label={app.status} 
                          color={
                            app.status === 'cancelled' ? 'error' : 
                            app.status === 'confirmed' ? 'success' : 
                            app.status === 'completed' ? 'secondary' : 'default'
                          } 
                          size="small" 
                        />
                      </TableCell>
                      <TableCell>
                        <Select
                          size="small"
                          value={app.status}
                          onChange={(e) => handleStatusChange(app.id, e.target.value)}
                        >
                          <MenuItem value="pending">Pendiente</MenuItem>
                          <MenuItem value="confirmed">Confirmada</MenuItem>
                          <MenuItem value="cancelled">Cancelada</MenuItem>
                          <MenuItem value="completed">Completada</MenuItem>
                          <MenuItem value="no_show">Inasistencia</MenuItem>
                        </Select>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Paper>
          </Grid>
        </Grid>
      );
    }

    if (activeTab === 'clients') {
      return (
        <Grid container spacing={3}>
          <Grid item xs={12} md={editingClient ? 8 : 12}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" mb={2}>Base de Clientes</Typography>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Nombre</TableCell>
                    <TableCell>Teléfono</TableCell>
                    <TableCell>Instagram</TableCell>
                    <TableCell>Acciones</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {clients.map(cli => (
                    <TableRow key={cli.id}>
                      <TableCell>{cli.name}</TableCell>
                      <TableCell>{cli.phone}</TableCell>
                      <TableCell>{cli.instagram_handle || '-'}</TableCell>
                      <TableCell>
                        <IconButton color="primary" onClick={() => handleStartEditClient(cli)} size="small">
                          <EditIcon />
                        </IconButton>
                        <IconButton color="error" onClick={() => handleDeleteClient(cli.id)} size="small">
                          <DeleteIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Paper>
          </Grid>
          
          {editingClient && (
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" mb={2}>Editar Cliente</Typography>
                <form onSubmit={handleSaveClient}>
                  <TextField fullWidth label="Nombre" value={editName} onChange={(e) => setEditName(e.target.value)} sx={{ mb: 2 }} required />
                  <TextField fullWidth label="Teléfono" value={editPhone} onChange={(e) => setEditPhone(e.target.value)} sx={{ mb: 2 }} required />
                  <TextField fullWidth label="Email" value={editEmail} onChange={(e) => setEditEmail(e.target.value)} sx={{ mb: 2 }} />
                  <TextField fullWidth label="Instagram Handle" value={editInstagram} onChange={(e) => setEditInstagram(e.target.value)} sx={{ mb: 2 }} />
                  <TextField fullWidth multiline rows={3} label="Notas" value={editNotes} onChange={(e) => setEditNotes(e.target.value)} sx={{ mb: 2 }} />
                  <Box display="flex" gap={1}>
                    <Button variant="contained" type="submit" sx={{ bgcolor: '#a87b6d' }}>Guardar</Button>
                    <Button variant="outlined" onClick={() => setEditingClient(null)}>Cancelar</Button>
                  </Box>
                </form>
              </Paper>
            </Grid>
          )}
        </Grid>
      );
    }

    if (activeTab === 'marketing') {
      return (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" mb={2}>Generar Campaña & Feed Meta</Typography>
              <form onSubmit={handleCreateCampaign}>
                <TextField fullWidth label="Título / Idea para Feed" value={campTitle} onChange={(e) => setCampTitle(e.target.value)} sx={{ mb: 2 }} />
                <TextField fullWidth multiline rows={4} label="Descripción para el Post" value={campDesc} onChange={(e) => setCampDesc(e.target.value)} sx={{ mb: 2 }} />
                <Button variant="contained" type="submit" sx={{ bgcolor: '#a87b6d' }}>Crear Contenido</Button>
              </form>
            </Paper>
          </Grid>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" mb={2}>Listos para Publicar (Meta)</Typography>
              <List>
                {campaigns.map(camp => (
                  <ListItem key={camp.id} sx={{ bgcolor: '#f5f5f5', mb: 1, borderRadius: 1 }}>
                    <ListItemText primary={camp.title} secondary={`Estado: ${camp.status}`} />
                    {camp.status !== 'active' && (
                      <Button variant="outlined" size="small" startIcon={<PublishIcon />} onClick={() => handlePublishMeta(camp.id)}>
                        Publicar en Meta
                      </Button>
                    )}
                  </ListItem>
                ))}
              </List>
            </Paper>
          </Grid>
        </Grid>
      );
    }
  };

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <AppBar position="fixed" sx={{ width: `calc(100% - ${drawerWidth}px)`, ml: `${drawerWidth}px`, bgcolor: '#ffffff', color: '#333' }}>
        <Toolbar>
          <Typography variant="h6" noWrap component="div">Erika Dashboard</Typography>
        </Toolbar>
      </AppBar>
      <Drawer
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': { width: drawerWidth, boxSizing: 'border-box', bgcolor: '#222', color: '#fff' },
        }}
        variant="permanent"
        anchor="left"
      >
        <Toolbar>
          <Typography variant="h6" sx={{ color: '#dcb3a6', fontStyle: 'italic' }}>Erika Manicura</Typography>
        </Toolbar>
        <Divider sx={{ bgcolor: '#444' }} />
        <List>
          <ListItem disablePadding>
            <ListItemButton onClick={() => setActiveTab('appointments')} selected={activeTab === 'appointments'}>
              <ListItemIcon><DashboardIcon sx={{ color: '#fff' }} /></ListItemIcon>
              <ListItemText primary="Panel de Citas" />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={() => setActiveTab('clients')} selected={activeTab === 'clients'}>
              <ListItemIcon><PeopleIcon sx={{ color: '#fff' }} /></ListItemIcon>
              <ListItemText primary="Base de Clientes" />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={() => setActiveTab('marketing')} selected={activeTab === 'marketing'}>
              <ListItemIcon><CampaignIcon sx={{ color: '#fff' }} /></ListItemIcon>
              <ListItemText primary="Campañas & Meta" />
            </ListItemButton>
          </ListItem>
          <Divider sx={{ bgcolor: '#444', my: 2 }} />
          <ListItem disablePadding>
            <ListItemButton onClick={() => { setIsAuthenticated(false); navigate('/'); }}>
              <ListItemIcon><LogoutIcon sx={{ color: '#dcb3a6' }} /></ListItemIcon>
              <ListItemText primary="Salir al Home" sx={{ color: '#dcb3a6' }} />
            </ListItemButton>
          </ListItem>
        </List>
      </Drawer>
      <Box component="main" sx={{ flexGrow: 1, bgcolor: '#f4f4f4', p: 3, minHeight: '100vh' }}>
        <Toolbar />
        {renderContent()}
      </Box>
    </Box>
  );
};

export default Admin;
