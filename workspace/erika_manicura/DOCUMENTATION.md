# Erika Manicura - Sistema Integral de Gestión (v1.1.0)

Este proyecto es una solución integral para "Erika Manicura", diseñada para gestionar citas, clientes, catálogo de servicios, finanzas y campañas de marketing (incluyendo planificación de Reels, contenidos de Feed y su conexión con Meta).

El sistema se divide en dos componentes principales:
1. **Backend:** Construido con FastAPI y SQLAlchemy (Arquitectura de 4 capas).
2. **Frontend:** Construido con React, TypeScript, Material UI (MUI) para el Panel Administrativo y Vanilla CSS para la landing page principal de clientes.

---

## 1. Arquitectura del Backend

El backend sigue un patrón de diseño de 4 capas:

- **`/domain`**: Modelos de datos y esquemas de validación construidos con `Pydantic`. Aquí se define la estructura de negocio (Clientes, Servicios, Citas, Campañas, etc.).
- **`/repository`**: Capa de acceso a datos. Contiene la conexión a la base de datos (`database.py` - SQLite por defecto) y los modelos ORM de `SQLAlchemy` (`models.py`).
- **`/service`**: Capa de lógica de negocio (`operations.py`). Conecta los repositorios con las rutas de la API, realizando validaciones, gestión de estados, cancelación de citas y la lógica de publicación de Meta.
- **`/api`**: Endpoints RESTful expuestos con `FastAPI` (`main.py`).

### Requisitos del Backend
- Python 3.10+ o Python 3.13 (usando `uv`)
- FastAPI
- SQLAlchemy
- Uvicorn

### Instalación y Ejecución del Backend (con `uv`)

1. Dirígete a la carpeta `backend`:
   ```bash
   cd workspace/erika_manicura/backend
   ```
2. Crea el entorno virtual de forma instantánea usando `uv`:
   ```bash
   uv venv --clear
   ```
3. Activa el entorno:
   ```bash
   source .venv/bin/activate
   ```
4. Instala las dependencias:
   ```bash
   uv pip install -r requirements.txt
   ```
5. Ejecuta el servidor de desarrollo:
   ```bash
   python run.py
   ```
   *La API estará disponible en `http://localhost:8000` y la documentación interactiva Swagger en `http://localhost:8000/docs`.*

---

## 2. Arquitectura del Frontend

El frontend combina una landing page de alta fidelidad con un panel administrativo profesional:

- **`/src/pages/Home.tsx`**: Landing page pública elegante inspirada en "Nails Divine". Ofrece navegación fluida, listado interactivo de servicios obtenidos del backend y un modal de reservas de citas. Cuenta con un enlace sutil de "Acceso Admin" en el pie de página.
- **`/src/pages/Admin.tsx`**: Panel administrativo de alta fidelidad maquetado completamente en **Material UI (MUI)**. Emula el estilo del Dashboard Creative Tim (barra lateral oscura, tarjetas de estado destacadas, tablas elegantes de datos). Permite:
  - Ver el total de citas y listarlas.
  - **Cancelar citas** con actualización de estado reactiva en el backend.
  - Ver la base de clientes (CRM) conectada al backend.
  - Diseñar campañas de marketing y feeds.
  - **Publicar en Meta** con un clic para vincular el contenido con Facebook e Instagram.
  - **Cerrar Sesión ("Salir al Home")** limpiando el estado de autenticación y redirigiendo al portal público con animación fluida.
- **`/src/services/api.ts`**: Cliente API centralizado que realiza las peticiones `fetch` al backend de FastAPI (`http://localhost:8000`).

### Instalación y Ejecución del Frontend

1. Dirígete a la carpeta `frontend`:
   ```bash
   cd workspace/erika_manicura/frontend
   ```
2. Instala los paquetes (incluyendo Material UI y react-router):
   ```bash
   npm install
   ```
3. Inicia el servidor de desarrollo Vite:
   ```bash
   npm run dev
   ```
   *El frontend estará operativo en `http://localhost:3000`.*

---

## 3. Integración con Meta (Facebook & Instagram)

### ¿Cómo funciona la conexión en Local?
Dado que para interactuar con la API real de Meta se requieren tokens de producción y una App validada en Facebook Developers, el sistema cuenta con un **módulo simulador de integración con Meta en local** completamente funcional para pruebas de desarrollo.

1. **Flujo de Publicación:**
   - La administradora diseña un feed/campaña en el panel de **Campañas & Meta** introduciendo un Título y Descripción.
   - El contenido se registra en el backend de FastAPI con estado `draft` (borrador).
   - En la lista de campañas listas para publicar, el panel de administración muestra el botón **"Publicar en Meta"**.
   - Al presionarlo, el frontend invoca el endpoint `POST /meta/publish/{campaign_id}`.
   - El backend procesa el contenido, simula la comunicación exitosa con la Graph API de Meta, cambia el estado de la campaña en base de datos a `active` (publicada) y retorna un mensaje de confirmación exitoso.
   - El frontend recibe la confirmación y refresca el listado, mostrando la campaña como publicada y deshabilitando el botón de publicación repetida.

---

## 4. Guía de Prueba Funcional en Local

Sigue estos pasos para probar todo el flujo de extremo a extremo de forma local:

### Paso 1: Inicializar los Servicios
Asegúrate de tener corriendo tanto el backend en `http://localhost:8000` como el frontend en `http://localhost:3000`.

### Paso 2: Crear un Borrador de Campaña
1. Abre tu navegador e ingresa a `http://localhost:3000/`.
2. Ve al pie de página (footer) y haz clic en **"Acceso Admin"**.
3. Loguéate con la clave **`admin123`**.
4. Dirígete a la pestaña **"Campañas & Meta"** en la barra lateral.
5. En el formulario "Generar Campaña & Feed Meta", escribe:
   - **Título:** `Súper Promo Manicura Rusa Otoño`
   - **Descripción:** `Este mes de junio, disfruta de un 20% de descuento en tu servicio de Manicura Rusa Permanente. ¡Agenda tu cita hoy!`
6. Haz clic en **"Crear Contenido"**. Esto enviará los datos a la base de datos SQLite a través del backend. Verás cómo aparece de inmediato en la lista de la derecha con estado `draft`.

### Paso 3: Probar la Publicación simulada en Meta
1. En la lista de la derecha ("Listos para Publicar"), verás tu campaña creada y el botón **"Publicar en Meta"**.
2. Haz clic en **"Publicar en Meta"**.
3. El sistema llamará a la API de FastAPI. Aparecerá una alerta en tu pantalla confirmando:
   > *"Campaña y feed 'Súper Promo Manicura Rusa Otoño' publicados exitosamente en Facebook e Instagram"*
4. Al hacer clic en aceptar, la lista se refrescará y el estado cambiará de `draft` a `active`, simulando la publicación en vivo de forma interactiva y reactiva.

---

## 5. Cómo pasar a la API Real de Meta en Producción

Para reemplazar el simulador por la publicación real en la página de Facebook e Instagram del negocio, debes seguir estos pasos técnicos:

### 1. Configuración en Meta for Developers
1. Ve a [Facebook Developers](https://developers.facebook.com/) y crea una cuenta.
2. Crea una App de tipo **"Negocios" (Business)**.
3. Agrega el producto **Graph API** y solicita los permisos:
   - `pages_manage_posts` (para publicar en Facebook Pages).
   - `instagram_basic` y `instagram_content_publish` (para publicar en Instagram).

### 2. Obtención de Identificadores y Tokens
Necesitarás:
- **`Page ID`**: El identificador numérico de la Fan Page de Facebook de Erika Manicura.
- **`Instagram Business Account ID`**: El identificador de la cuenta de Instagram comercial vinculada a la Fan Page.
- **`Page Access Token`**: Token de larga duración de Meta para autorizar publicaciones automáticas sin intervención manual.

### 3. Actualización de Código en Backend (`backend/service/operations.py`)
Reemplaza la función `publish_to_meta` simulada por una llamada HTTP real utilizando la librería `requests` o `httpx`:

```python
import requests

def publish_to_meta(db: Session, campaign_id: str):
    db_camp = db.query(models.MarketingCampaign).filter(models.MarketingCampaign.id == campaign_id).first()
    if not db_camp:
        return None

    # Configuración de Meta (Se recomienda cargarlo desde variables de entorno)
    PAGE_ID = "TU_PAGE_ID_REAL"
    PAGE_ACCESS_TOKEN = "TU_TOKEN_DE_ACCESO_DE_LARGA_DURACION"
    
    # URL de publicación en el feed de Facebook
    url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/feed"
    
    payload = {
        "message": f"{db_camp.title}\n\n{db_camp.description}",
        "access_token": PAGE_ACCESS_TOKEN
    }
    
    try:
        # Llamada real a la API de Meta
        response = requests.post(url, json=payload)
        response_data = response.json()
        
        if response.status_code == 200:
            # Publicación exitosa en Facebook
            db_camp.status = "active"
            db.commit()
            db.refresh(db_camp)
            return {
                "status": "success", 
                "message": f"Publicado en Meta de forma exitosa. ID del Post: {response_data.get('id')}"
            }
        else:
            return {
                "status": "error", 
                "message": f"Error de Meta API: {response_data.get('error', {}).get('message')}"
            }
    except Exception as e:
        return {"status": "error", "message": f"Error de conexión con Meta: {str(e)}"}
```

*Este flujo robusto e integral garantiza que el software esté preparado estructuralmente para crecer y automatizar el marketing digital de Erika Manicura con total fiabilidad.*
