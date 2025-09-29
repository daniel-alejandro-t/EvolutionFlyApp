# Evolution Fly App 🛫

Una aplicación para gestionar pedidos de vuelo construida con Django 5 y React 19.

## 🚀 Características

### Funcionalidades Principales
- **Sistema de usuarios con roles**: Cliente, Operador y Administrador
- **Solicitud de vuelos**: Los clientes pueden solicitar vuelos a destinos específicos
- **Gestión de solicitudes**: Los operadores pueden revisar y reservar solicitudes
- **Gestión de destinos**: Los administradores pueden gestionar las ciudades disponibles
- **Notificaciones automáticas**: Envío de emails 2 días antes del vuelo
- **Cache con Redis**: Lista de destinos cacheada para mejor rendimiento

### Tecnologías Utilizadas

#### Backend
- **Django 5.2.6**: Framework web principal
- **Django REST Framework**: API REST
- **PostgreSQL**: Base de datos principal
- **Redis**: Cache y broker de Celery
- **Celery**: Tareas asíncronas y programadas
- **Celery Beat**: Programador de tareas
- **CORS Headers**: Manejo de CORS para el frontend

#### Frontend
- **React 19**: Biblioteca de interfaz de usuario
- **TypeScript**: Tipado estático
- **React Router**: Enrutamiento
- **React Bootstrap**: Componentes UI
- **Axios**: Cliente HTTP
- **React DatePicker**: Selector de fechas
- **React Toastify**: Notificaciones

#### Infraestructura
- **Docker & Docker Compose**: Containerización
- **Gunicorn**: Servidor WSGI para producción
- **Nginx**: Servidor web para frontend
- **Pytest**: Framework de testing

## 📋 Requisitos

- Python 3.12+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker y Docker Compose (opcional)

## 🛠️ Instalación y Configuración

### Opción 1: Usando Docker (Recomendado)

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd evolutionflyapp
   ```

2. **Configurar variables de entorno**
   ```bash
   cp .env.docker .env
   # Editar .env con tus configuraciones
   ```

3. **Levantar los servicios**
   ```bash
   docker-compose up --build
   ```

4. **Crear superusuario**
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

5. **Cargar destinos iniciales**
   ```bash
   docker-compose exec backend python manage.py load_destinations
   ```

### Opción 2: Instalación Manual

#### Backend Setup

1. **Crear entorno virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # o
   venv\Scripts\activate  # Windows
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar base de datos PostgreSQL**
   ```bash
   createdb evolutionflyapp
   ```

4. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   # Editar .env con tus configuraciones
   ```

5. **Ejecutar migraciones**
   ```bash
   python manage.py migrate
   ```

6. **Crear superusuario**
   ```bash
   python manage.py createsuperuser
   ```

7. **Cargar destinos iniciales**
   ```bash
   python manage.py load_destinations
   ```

8. **Ejecutar servidor de desarrollo**
   ```bash
   python manage.py runserver
   ```

#### Frontend Setup

1. **Navegar al directorio frontend**
   ```bash
   cd frontend
   ```

2. **Instalar dependencias**
   ```bash
   npm install
   ```

3. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   # Verificar REACT_APP_API_URL
   ```

4. **Ejecutar servidor de desarrollo**
   ```bash
   npm start
   ```

#### Celery Setup

En terminales separadas:

1. **Worker de Celery**
   ```bash
   celery -A evolutionflyapp worker --loglevel=info
   ```

2. **Celery Beat (programador)**
   ```bash
   celery -A evolutionflyapp beat --loglevel=info
   ```

## 🎯 Uso de la Aplicación

### Roles de Usuario

#### Cliente
- Registrarse en la aplicación
- Solicitar vuelos a destinos disponibles
- Ver el estado de sus solicitudes
- Recibir notificaciones por email

#### Operador
- Ver todas las solicitudes pendientes
- Reservar solicitudes de vuelo
- Gestionar destinos (CRUD)
- Ver reportes de vuelos

#### Administrador
- Todas las funcionalidades del operador
- Gestión completa de usuarios
- Configuración del sistema

### Flujo de Trabajo

1. **Registro de Usuario**: Los usuarios se registran eligiendo su rol
2. **Solicitud de Vuelo**: Los clientes solicitan vuelos con destino y fecha
3. **Gestión por Operador**: Los operadores revisan y reservan solicitudes
4. **Confirmación**: El sistema envía email de confirmación
5. **Recordatorio**: 2 días antes del vuelo, se envía recordatorio automático

## 📊 API Endpoints

### Autenticación
- `POST /api/auth/register/` - Registro de usuario
- `POST /api/auth/login/` - Inicio de sesión
- `POST /api/auth/logout/` - Cerrar sesión
- `GET/PUT /api/auth/profile/` - Perfil de usuario

### Destinos
- `GET /api/destinations/destinations/` - Listar destinos
- `GET /api/destinations/destinations/active_destinations/` - Destinos activos (cached)
- `POST /api/destinations/destinations/` - Crear destino (admin)
- `PUT /api/destinations/destinations/{id}/` - Actualizar destino (admin)
- `DELETE /api/destinations/destinations/{id}/` - Eliminar destino (admin)

### Solicitudes de Vuelo
- `GET /api/flight-requests/flight-requests/` - Listar solicitudes del usuario
- `POST /api/flight-requests/flight-requests/` - Crear solicitud
- `GET /api/flight-requests/flight-requests/pending/` - Solicitudes pendientes (operadores)
- `POST /api/flight-requests/flight-requests/{id}/reserve/` - Reservar solicitud
- `PUT /api/flight-requests/flight-requests/{id}/` - Actualizar solicitud

## 🧪 Testing

### Ejecutar todas las pruebas
```bash
# Con Django test runner
python manage.py test

# Con pytest (recomendado)
pytest

# Con coverage
coverage run -m pytest
coverage report
coverage html
```

### Pruebas específicas
```bash
# Modelos
pytest users/tests.py destinations/tests.py flight_requests/tests.py

# API
pytest tests/test_api.py

# Tareas de Celery
pytest tests/test_tasks.py
```

## 📧 Configuración de Email

Para habilitar las notificaciones por email, configura las siguientes variables de entorno:

```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
```

**Nota**: Para Gmail, necesitas generar una "App Password" en lugar de usar tu contraseña normal.

## 🚀 Despliegue en Producción

### Usando Docker

1. **Configurar variables de producción**
   ```bash
   cp .env.docker .env.prod
   # Editar con configuraciones de producción
   # Especialmente SECRET_KEY, DEBUG=False, ALLOWED_HOSTS
   ```

2. **Construir y desplegar**
   ```bash
   docker-compose -f docker-compose.prod.yml up --build -d
   ```

### Consideraciones de Producción

- Usar un `SECRET_KEY` único y seguro
- Configurar `DEBUG=False`
- Especificar `ALLOWED_HOSTS` correctamente
- Usar HTTPS en producción
- Configurar un servidor de email real
- Implementar monitoreo y logs
- Configurar backups de base de datos

## 🔧 Comandos Útiles

### Django Management Commands

```bash
# Cargar destinos iniciales
python manage.py load_destinations

# Crear superusuario
python manage.py createsuperuser

# Limpiar cache
python manage.py shell -c "from django.core.cache import cache; cache.clear()"

# Ejecutar migraciones
python manage.py migrate

# Recopilar archivos estáticos
python manage.py collectstatic
```

### Docker Commands

```bash
# Ver logs
docker-compose logs backend
docker-compose logs celery

# Ejecutar comandos en contenedor
docker-compose exec backend python manage.py shell

# Reiniciar servicios
docker-compose restart backend celery

# Limpiar y rebuilder
docker-compose down -v
docker-compose up --build
```

## 📁 Estructura del Proyecto

```
evolutionflyapp/
├── evolutionflyapp/        # Configuración principal de Django
│   ├── settings.py         # Configuraciones
│   ├── urls.py            # URLs principales
│   ├── celery.py          # Configuración de Celery
│   └── wsgi.py            # WSGI application
├── users/                  # App de usuarios
├── destinations/           # App de destinos
├── flight_requests/        # App de solicitudes de vuelo
├── templates/              # Templates de email
├── tests/                  # Tests de integración
├── frontend/               # Aplicación React
│   ├── src/
│   │   ├── components/     # Componentes React
│   │   ├── contexts/       # Context API
│   │   ├── services/       # Servicios API
│   │   └── types/          # Tipos TypeScript
│   └── public/
├── logs/                   # Archivos de log
├── docker-compose.yml      # Configuración Docker
├── requirements.txt        # Dependencias Python
└── README.md              # Este archivo
```

## 🤝 Contributing

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

Si tienes preguntas o necesitas ayuda:

1. Abre un issue en GitHub
2. Revisa la documentación de Django y React
3. Consulta los logs de la aplicación

---

Desarrollado con ❤️ para Evolution Fly App