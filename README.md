# 🎓 Cursalo - Plataforma de Gestión de Cursos

[![FastAPI](https://img.shields.io/badge/FastAPI-0.118.0-009688.svg?style=flat&logo=FastAPI)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.13+-3776ab.svg?style=flat&logo=Python&logoColor=white)](https://python.org)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0+-4ea94b.svg?style=flat&logo=MongoDB&logoColor=white)](https://mongodb.com)
[![Beanie](https://img.shields.io/badge/Beanie-2.0.0-orange.svg?style=flat)](https://beanie-odm.dev)

**Cursalo** es una API REST moderna construida con FastAPI para la gestión integral de cursos online. Permite administrar estudiantes, profesores, clases y autenticacion con autenticación JWT.

## 🚀 Características Principales

- 🔐 **Autenticación y Autorización** con JWT
- 👥 **Gestión de Usuarios** (Estudiantes y Profesores)
- 📚 **Administración de Clases** con inscripciones
- 🎫 **Sistema de Vouchers** para descuentos
- 📊 **Base de Datos NoSQL** con MongoDB
- 🔄 **ODM Moderno** usando Beanie
- 📖 **Documentación Automática** con Swagger UI
- 🏗️ **Arquitectura Hexagonal** bien estructurada

## 🛠️ Stack Tecnológico

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **FastAPI** | 0.118.0 | Framework web asíncrono |
| **Python** | 3.13+ | Lenguaje de programación |
| **MongoDB** | 6.0+ | Base de datos NoSQL |
| **Beanie** | 2.0.0 | ODM para MongoDB |
| **PyJWT** | 2.10.1 | Manejo de tokens JWT |
| **Uvicorn** | 0.37.0 | Servidor ASGI |
| **Pydantic** | 2.11.10 | Validación de datos |
| **Argon2** | 23.1.0 | Hash de contraseñas |

## 🔧 Instalación y Configuración

### Prerrequisitos

- Python 3.13+
- MongoDB 6.0+
- pip (gestor de paquetes de Python)

### 1. Clonar el Repositorio

```bash
git clone https://github.com/xan-develop/cursalo-fastapi.git
cd cursalo-fastapi
```

### 2. Crear Entorno Virtual

```bash
python -m venv venv

# En Windows
venv\Scripts\activate

# En Linux/macOS  
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Crear un archivo `.env` en la raíz del proyecto:

```env
# Base de datos
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=cursalo_db

# JWT
SECRET_KEY=tu_clave_secreta_super_segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Configuración del servidor
HOST=0.0.0.0
PORT=8000
```

### 5. Ejecutar la Aplicación

```bash
# Modo desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Modo producción
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 🚀 Uso de la API

### Acceder a la Documentación

Una vez ejecutada la aplicación, puedes acceder a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Endpoints Principales

#### 🔐 Autenticación (`/auth`)

```http
POST /auth/register/teacher    # Registrar profesor
POST /auth/register/student    # Registrar estudiante  
POST /auth/login              # Iniciar sesión
POST /auth/refresh-token      # Renovar token
GET  /auth/me                 # Obtener usuario actual
```

#### 📚 Clases (`/classes`)

```http
GET    /classes               # Listar todas las clases
POST   /classes               # Crear nueva clase (solo profesores)
GET    /classes/{id}          # Obtener clase específica
PUT    /classes/{id}          # Actualizar clase
DELETE /classes/{id}          # Eliminar clase
POST   /classes/{id}/enroll   # Inscribirse en clase
```

#### 👨‍🎓 Estudiantes (`/students`)

```http
GET    /students              # Listar estudiantes
GET    /students/{id}         # Obtener estudiante específico
PUT    /students/{id}         # Actualizar perfil de estudiante
GET    /students/{id}/classes # Clases del estudiante
```

#### 👨‍🏫 Profesores (`/teachers`)

```http
GET    /teachers              # Listar profesores
GET    /teachers/{id}         # Obtener profesor específico
PUT    /teachers/{id}         # Actualizar perfil de profesor
GET    /teachers/{id}/classes # Clases del profesor
```


## 🏗️ Arquitectura

La aplicación sigue principios de **Arquitectura Hexagonal** (Ports & Adapters):

- **Models**: Entidades de dominio con validaciones Pydantic
- **Repositories**: Capa de acceso a datos (MongoDB con Beanie)
- **Services**: Lógica de negocio y casos de uso
- **Routes**: Controladores HTTP y validación de entrada
- **Security**: Autenticación JWT y autorización basada en roles

## 🔐 Seguridad

- **Autenticación JWT** con tokens de acceso y renovación
- **Hash de contraseñas** usando Argon2
- **Autorización basada en roles** (estudiante, profesor)
- **Validación de datos** con Pydantic en todas las entradas
- **Protección CORS** configurable

## 📊 Base de Datos

El sistema utiliza **MongoDB** con las siguientes colecciones:

- **users**: Usuarios base con herencia (estudiantes y profesores)
- **classes**: Información de clases y cursos
- **enrollments**: Inscripciones de estudiantes
- **vouchers**: Sistema de descuentos y vouchers

Ver [dbdesing.md](dbdesing.md) para más detalles del esquema.

## 👨‍💻 Autor

**Alexander** - [xan-develop](https://github.com/xan-develop)

## 🔗 Enlaces Útiles

- [Documentación de FastAPI](https://fastapi.tiangolo.com/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Beanie ODM](https://beanie-odm.dev/)
- [JWT.io](https://jwt.io/)

---

