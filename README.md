# BACKEND-FAPI-BDI-SMART_HEALTH
# SmartHealth - Clinical Query System with RAG

**Desarrolladores**: Ivan Ospino, Gisell Anaya, Jhoan Smith, Jeison Mendez, Jhon Mantilla  
**Creado**: 22-Noviembre-2025  
**Última actualización**: 07-Diciembre-2025

---

## Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Características Principales](#características-principales)
3. [Arquitectura del Sistema](#arquitectura-del-sistema)
4. [Requisitos del Sistema](#requisitos-del-sistema)
5. [Instalación Completa](#instalación-completa)
   - [5.1 Instalación de PostgreSQL](#51-instalación-de-postgresql)
   - [5.2 Configuración de la Base de Datos](#52-configuración-de-la-base-de-datos)
   - [5.3 Instalación del Backend](#53-instalación-del-backend)
   - [5.4 Configuración de Variables de Entorno](#54-configuración-de-variables-de-entorno)
6. [Seguridad](#seguridad)
   - [6.1 Principios de Seguridad](#61-principios-de-seguridad)
   - [6.2 Autenticación y Autorización](#62-autenticación-y-autorización)
   - [6.3 Protección de Datos](#63-protección-de-datos)
   - [6.4 Rate Limiting](#64-rate-limiting)
   - [6.5 Validación de Inputs](#65-validación-de-inputs)
7. [Configuración y Uso](#configuración-y-uso)
   - [7.1 Iniciar el Servidor](#71-iniciar-el-servidor)
   - [7.2 Documentación de la API](#72-documentación-de-la-api)
   - [7.3 WebSocket Chat](#73-websocket-chat)
8. [API Endpoints](#api-endpoints)
9. [Testing](#testing)
10. [Troubleshooting Completo](#troubleshooting-completo)
11. [Despliegue en Producción](#despliegue-en-producción)
12. [Mantenimiento](#mantenimiento)
13. [Contribución](#contribución)
14. [Soporte](#soporte)

---

## Descripción General

SmartHealth es un sistema backend desarrollado en **FastAPI** para la consulta inteligente de información clínica de pacientes utilizando el patrón **RAG (Retrieval-Augmented Generation)**. El sistema utiliza **PostgreSQL con pgvector** como base de datos vectorial y está diseñado con una arquitectura modular que facilita la escalabilidad y el mantenimiento.

### ¿Qué hace SmartHealth?

- Permite consultar historias clínicas completas de pacientes
- Utiliza IA (OpenAI GPT) para generar respuestas inteligentes
- Realiza búsqueda semántica en citas, diagnósticos, prescripciones y registros médicos
- Proporciona chat en tiempo real con streaming de respuestas
- Implementa autenticación segura con JWT
- Registra todas las consultas para auditoría

---

## Características Principales

### Funcionalidades Core

- **Autenticación JWT**: Sistema seguro de registro y login
- **Chat en Tiempo Real**: WebSocket con streaming token por token
- **RAG Inteligente**: Búsqueda vectorial + LLM para respuestas precisas
- **Búsqueda Semántica**: Encuentra información relevante usando embeddings
- **API REST + WebSocket**: Máxima flexibilidad de integración
- **Logging y Auditoría**: Registro completo de todas las operaciones

### Seguridad Implementada

- Rate limiting por usuario y global
- Validación exhaustiva de inputs
- Sanitización de datos
- Headers de seguridad (HSTS, CSP, X-Frame-Options)
- Contraseñas con requisitos estrictos
- Tokens JWT con expiración
- Protección contra inyección SQL
- CORS configurable por entorno

### Tecnologías Utilizadas

- **Backend**: FastAPI 0.111.0 + Python 3.9+
- **Base de Datos**: PostgreSQL 16 + pgvector
- **IA**: OpenAI GPT-4o-mini + text-embedding-3-small
- **Autenticación**: JWT (python-jose)
- **ORM**: SQLAlchemy 2.0
- **Validación**: Pydantic 2.8
- **Servidor**: Uvicorn + Gunicorn

---

## Arquitectura del Sistema

```
┌─────────────────┐
│   Cliente Web   │
│   (Frontend)    │
└────────┬────────┘
         │ HTTP/WS
         ▼
┌─────────────────────────────────────┐
│       FastAPI Backend               │
│  ┌─────────────────────────────┐   │
│  │   Auth (JWT)                │   │
│  │   Rate Limiting             │   │
│  │   CORS                      │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │   Routers                   │   │
│  │   - Auth                    │   │
│  │   - Users                   │   │
│  │   - Query (RAG)             │   │
│  │   - WebSocket Chat          │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │   Services                  │   │
│  │   - Clinical Service        │   │
│  │   - Vector Search           │   │
│  │   - LLM Service             │   │
│  │   - Auth Service            │   │
│  └─────────────────────────────┘   │
└───────────┬─────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│   PostgreSQL + pgvector             │
│   - Datos clínicos                  │
│   - Embeddings (vectores)           │
│   - Usuarios y sesiones             │
└─────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│   OpenAI API                        │
│   - GPT-4o-mini (respuestas)        │
│   - text-embedding-3-small          │
└─────────────────────────────────────┘
```

### Flujo de una Consulta RAG

1. Usuario envía pregunta sobre un paciente
2. Sistema busca al paciente en PostgreSQL
3. Realiza búsqueda vectorial de información relevante
4. Construye contexto combinando datos directos + vectoriales
5. Envía contexto + pregunta a GPT-4o-mini
6. LLM genera respuesta inteligente
7. Sistema envía respuesta al usuario (streaming en WebSocket)
8. Registra consulta en audit_logs

---

## Requisitos del Sistema

### Software Requerido

- **Python**: 3.9 o superior
- **PostgreSQL**: 16 o superior
- **pgvector**: Extensión para PostgreSQL
- **pip**: Gestor de paquetes de Python
- **Git**: Para clonar el repositorio

### Recursos de Hardware Recomendados

#### Desarrollo
- CPU: 2 cores
- RAM: 4 GB
- Disco: 10 GB libre

#### Producción
- CPU: 4+ cores
- RAM: 8+ GB
- Disco: 50+ GB (dependiendo de los datos)

### Cuentas Externas

- **OpenAI Account**: Para API key (GPT y embeddings)
  - Obtener en: https://platform.openai.com/api-keys
  - Necesita créditos disponibles

---

## Instalación Completa

### 5.1 Instalación de PostgreSQL

#### Windows

1. Descargar PostgreSQL 16 desde: https://www.postgresql.org/download/windows/
2. Ejecutar el instalador
3. Durante la instalación:
   - Recordar la contraseña del usuario `postgres`
   - Puerto por defecto: 5432
   - Locale: Spanish_Colombia.UTF-8 (o el de tu región)
4. Verificar instalación:
```bash
psql --version
# Salida esperada: psql (PostgreSQL) 16.x
```

#### Linux (Ubuntu/Debian)

```bash
# Actualizar repositorios
sudo apt update

# Instalar PostgreSQL
sudo apt install postgresql postgresql-contrib

# Iniciar servicio
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verificar instalación
psql --version
```

#### macOS

```bash
# Usando Homebrew
brew install postgresql@16

# Iniciar servicio
brew services start postgresql@16

# Verificar instalación
psql --version
```

#### Instalar pgvector

**Linux:**
```bash
# Clonar repositorio
cd /tmp
git clone https://github.com/pgvector/pgvector.git
cd pgvector

# Compilar e instalar
make
sudo make install
```

**Windows:**
```bash
# Descargar binarios precompilados desde:
# https://github.com/pgvector/pgvector/releases

# O usar vcpkg:
vcpkg install pgvector
```

**macOS:**
```bash
brew install pgvector
```

**Verificar instalación de pgvector:**
```sql
-- Conectar a PostgreSQL
psql -U postgres

-- Crear extensión de prueba
CREATE DATABASE test_pgvector;
\c test_pgvector
CREATE EXTENSION vector;

-- Si no hay errores, pgvector está instalado correctamente
DROP DATABASE test_pgvector;
\q
```

---

### 5.2 Configuración de la Base de Datos

#### Opción A: Instalación Automatizada con Scripts (RECOMENDADO)

Esta es la forma más fácil y rápida de configurar la base de datos.

**Paso 1: Clonar el Repositorio**

```bash
git clone git@github.com:Ospino89/-backend-fapi-bdi-smart_health.git
cd -backend-fapi-bdi-smart_health
```

**Paso 2: Preparar Entorno Python**

```bash
# Navegar al directorio de pipelines
cd pipelines

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
.\venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install psycopg2-binary tqdm python-dotenv
```

**Paso 3: Configurar Contraseñas**

Editar los siguientes archivos y cambiar la contraseña:

1. `pipelines/01-create-database/script-01.py`
```python
# Buscar esta línea y cambiar:
password="****"  # Tu contraseña aquí
```

2. `pipelines/01-create-database/script-02.py`
```python
password="****"  # La misma contraseña
```

3. `pipelines/02-insert-data/create-tables.py`
```python
password="****"  # La misma contraseña
```

**IMPORTANTE**: Usa la misma contraseña en todos los archivos.

**Paso 4: Limpiar Base de Datos Anterior (Si Existe)**

Abrir una terminal nueva y ejecutar:

```bash
# Conectar a PostgreSQL como superusuario
psql -U postgres -d postgres
```

Dentro de psql:
```sql
-- Cerrar conexiones activas
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'smarthdb'
  AND pid <> pg_backend_pid();

-- Eliminar base de datos si existe
DROP DATABASE IF EXISTS smarthdb;

-- Eliminar rol si existe
DROP ROLE IF EXISTS sm_admin;

-- Verificar
\l   -- No debe aparecer smarthdb
\du  -- No debe aparecer sm_admin

-- DEJAR ESTA TERMINAL ABIERTA
```

**Paso 5: Crear Base de Datos**

Volver a la terminal con el entorno virtual activado:

```bash
# Asegurarse de estar en pipelines/01-create-database/
cd pipelines/01-create-database

# Ejecutar primer script
python script-01.py
```

**Salida esperada:**
```
Conectando a PostgreSQL...
Creando base de datos 'smarthdb'...
Creando rol 'sm_admin'...
Base de datos creada exitosamente.
```

**Paso 6: Otorgar Permisos de Superusuario**

En la terminal de psql (que dejamos abierta):

```sql
-- Conectar a la nueva base de datos
\c smarthdb

-- Otorgar permisos SUPERUSER (necesario para pgvector)
ALTER USER sm_admin WITH SUPERUSER;

-- Verificar permisos
\du

-- Debe aparecer:
-- sm_admin | Superuser
```

**Paso 7: Instalar Extensión pgvector**

Volver a la terminal con el entorno virtual:

```bash
# Ejecutar segundo script
python script-02.py
```

**Salida esperada:**
```
Conectando a PostgreSQL...
Instalando extensión pgvector...
Extensión instalada correctamente.
```

**Verificar en psql:**
```sql
\c smarthdb
\dx

-- Debe aparecer vector en la lista
```

**Paso 8: Crear Esquema y Tablas**

```bash
# Cambiar al directorio de inserción
cd ../02-insert-data

# Ejecutar script de creación de tablas
python create-tables.py
```

**Salida esperada:**
```
Creando esquema smart_health...
Creando tabla patients...
Creando tabla doctors...
... (más tablas)
Tablas creadas exitosamente.
```

**Paso 9: Insertar Datos de Ejemplo**

```bash
# Ejecutar script de inserción
python script-02.py
```

**Salida esperada:**
```
Insertando datos en patients...
100%|████████████████| 100/100
Insertando datos en doctors...
50%|████████████████| 50/50
...
Datos insertados correctamente.
```

**NOTA**: Este proceso puede tardar 5-10 minutos.

**Paso 10: Verificar Instalación**

En psql:
```sql
-- Conectar
\c smarthdb

-- Ver esquemas
\dn
-- Debe aparecer: smart_health

-- Ver tablas
\dt smart_health.*
-- Deben aparecer 13 tablas

-- Contar registros
SELECT 
    tablename,
    (SELECT COUNT(*) FROM ('SELECT * FROM smart_health.' || tablename || ' LIMIT 1000')::text) as count
FROM pg_tables
WHERE schemaname = 'smart_health'
ORDER BY tablename;
```

#### Opción B: Instalación Manual con SQL

Si prefieres ejecutar los scripts SQL directamente:

```bash
psql -U postgres

-- Crear base de datos
CREATE DATABASE smarthdb;
CREATE USER sm_admin WITH PASSWORD '****';
GRANT ALL PRIVILEGES ON DATABASE smarthdb TO sm_admin;

\c smarthdb
ALTER USER sm_admin WITH SUPERUSER;
CREATE EXTENSION vector;

-- Ejecutar scripts SQL
\i path/to/01-create-tables.sql
\i path/to/02-insert-data.sql
\i path/to/03-create-embeddings.sql
```

---

### 5.3 Instalación del Backend

**Paso 1: Navegar a la Raíz del Proyecto**

```bash
cd ../..  # Desde pipelines/02-insert-data volver a raíz
```

**Paso 2: Crear Entorno Virtual para el Backend**

```bash
# Crear nuevo entorno virtual
python -m venv venv

# Activar
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

**Paso 3: Instalar Dependencias del Backend**

```bash
pip install -r requirements.txt
```

**Dependencias principales instaladas:**
- fastapi==0.111.0
- uvicorn==0.30.1
- sqlalchemy==2.0.29
- psycopg2-binary==2.9.9
- python-jose[cryptography]==3.3.0
- passlib[bcrypt]==1.7.4
- pydantic==2.8.0
- openai>=1.12.0
- pgvector==0.4.1
- gunicorn==21.2.0

**Verificar instalación:**
```bash
pip list | grep fastapi
# Debe aparecer: fastapi 0.111.0
```

---

### 5.4 Configuración de Variables de Entorno

**Paso 1: Crear Archivo .env**

En la raíz del proyecto, crear archivo `.env`:

```bash
# Windows:
copy nul .env

# Linux/Mac:
touch .env
```

**Paso 2: Configurar Variables**

Editar `.env` con el siguiente contenido:

```env
# ===================================================================
# BASE DE DATOS
# ===================================================================
DB_HOST=localhost
DB_PORT=5432
DB_NAME=smarthdb
DB_USER=sm_admin
DB_PASSWORD=****

# ===================================================================
# SEGURIDAD - CRÍTICO
# ===================================================================
# IMPORTANTE: Genera una clave segura con:
# python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=GENERA_UNA_CLAVE_SEGURA_DE_64_CARACTERES_AQUI

# Entorno: development, staging, production
APP_ENV=development

# ===================================================================
# OPENAI API
# ===================================================================
# Obtener en: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-TU_API_KEY_AQUI

# ===================================================================
# CONFIGURACIÓN LLM
# ===================================================================
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=2000
LLM_TIMEOUT=30

# ===================================================================
# WEBSOCKET (Opcional)
# ===================================================================
WEBSOCKET_TIMEOUT=300
WEBSOCKET_RATE_LIMIT=20
WEBSOCKET_MAX_MESSAGE_SIZE=10485760

# ===================================================================
# JWT (Opcional)
# ===================================================================
JWT_EXPIRATION_MINUTES=30
JWT_ALGORITHM=HS256

# ===================================================================
# CORS (Producción)
# ===================================================================
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# ===================================================================
# RATE LIMITING (Producción)
# ===================================================================
GLOBAL_RATE_LIMIT=100
```

**Paso 3: Generar SECRET_KEY Segura**

```bash
python -c "import secrets; print(secrets.token_hex(32))"

# Salida ejemplo:
# 7c92e93af3218c22c0eb3a65871cebd2eede4f7455f64e82fbc7282f29a01be4

# Copiar este valor y ponerlo en SECRET_KEY del .env
```

**Paso 4: Obtener OpenAI API Key**

1. Ir a: https://platform.openai.com/api-keys
2. Crear cuenta o iniciar sesión
3. Click en "Create new secret key"
4. Copiar la key (comienza con `sk-`)
5. Pegar en `OPENAI_API_KEY` del `.env`

**IMPORTANTE**: No compartir nunca tu API key.

**Paso 5: Verificar .env**

```bash
# Verificar que el archivo existe
# Windows:
dir .env

# Linux/Mac:
ls -la .env

# IMPORTANTE: Verificar que .env está en .gitignore
cat .gitignore | grep .env
# Debe aparecer: .env
```

---

## Seguridad

### 6.1 Principios de Seguridad

SmartHealth implementa seguridad en múltiples capas:

1. **Defense in Depth**: Múltiples capas de protección
2. **Least Privilege**: Mínimos permisos necesarios
3. **Secure by Default**: Configuración segura por defecto
4. **Fail Secure**: Fallar de forma segura
5. **Zero Trust**: Nunca confiar, siempre verificar

### 6.2 Autenticación y Autorización

#### Requisitos de Contraseñas

Las contraseñas DEBEN cumplir:

- **Mínimo 8 caracteres**
- **Al menos 1 letra MAYÚSCULA**
- **Al menos 1 letra minúscula**
- **Al menos 1 número**
- **Al menos 1 carácter especial** (!@#$%^&*(),.?":{}|<>)

**Ejemplo de contraseña válida**: `SecurePass123!`

**Ejemplo de contraseña inválida**: `password` (no cumple requisitos)

#### Hashing de Contraseñas

- **Algoritmo**: bcrypt
- **Factor de costo**: 12 (aprox. 250ms por hash)
- **Nunca** se almacenan contraseñas en texto plano
- **Nunca** se transmiten contraseñas sin cifrar

#### Tokens JWT

**Configuración**:
- Algoritmo: HS256
- Expiración: 30 minutos (configurable)
- Payload incluye: user_id, email, is_active
- Firmado con SECRET_KEY

**Buenas prácticas**:
```javascript
// Almacenar token en cliente
localStorage.setItem('token', token);

// Incluir en requests
fetch('http://localhost:8088/users/me', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

// Renovar antes de expirar
if (tokenExpiresSoon()) {
  refreshToken();
}
```

#### Flujo de Autenticación

```
1. Usuario → POST /auth/register (email, password)
   ↓
2. Backend → Valida datos
   ↓
3. Backend → Hash password con bcrypt
   ↓
4. Backend → Guarda usuario en DB
   ↓
5. Usuario → POST /auth/login (email, password)
   ↓
6. Backend → Verifica credenciales
   ↓
7. Backend → Genera JWT
   ↓
8. Usuario ← Recibe token
   ↓
9. Usuario → Request con Authorization: Bearer <token>
   ↓
10. Backend → Valida token
    ↓
11. Backend → Procesa request
```

### 6.3 Protección de Datos

#### Datos en Tránsito

**Desarrollo**:
- HTTP permitido (localhost)
- Sin certificados

**Producción** (OBLIGATORIO):
- HTTPS/TLS únicamente
- Certificados válidos (Let's Encrypt recomendado)
- TLS 1.2+ mínimo
- Perfect Forward Secrecy (PFS)

#### Headers de Seguridad

El sistema añade automáticamente estos headers:

```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
```

#### Datos en Reposo

**Base de Datos**:
- Contraseñas hasheadas (bcrypt)
- Datos sensibles encriptados si es necesario
- Backups encriptados

**Logs**:
- No loggear contraseñas
- No loggear tokens completos
- Sanitizar datos sensibles
- Rotar logs cada 30 días

### 6.4 Rate Limiting

#### Límites Implementados

**WebSocket**:
- **20 mensajes/minuto** por usuario
- Implementado en `ConnectionManager`
- Respuesta: Mensaje de error + espera de 60 segundos

**API REST (Solo en Producción)**:
- **100 requests/minuto** por IP
- Implementado en `RateLimitMiddleware`
- Respuesta: HTTP 429 Too Many Requests

#### Configuración

En `.env`:
```env
WEBSOCKET_RATE_LIMIT=20
GLOBAL_RATE_LIMIT=100
```

#### Respuesta de Rate Limit

```json
{
  "type": "error",
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Has excedido el límite de mensajes por minuto"
  }
}
```

### 6.5 Validación de Inputs

#### Principios

1. **Whitelist, no Blacklist**: Validar lo permitido
2. **Validar en servidor**: Nunca confiar en cliente
3. **Sanitizar siempre**: Limpiar todos los inputs
4. **Tipos estrictos**: Usar Pydantic para validación

#### Validaciones Aplicadas

**Email**:
```python
# Formato válido con regex
^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$

# Normalizado a minúsculas
"User@Example.COM" → "user@example.com"
```

**Contraseñas**:
- Longitud: 8-100 caracteres
- Complejidad: Ver sección 6.2
- No permitir contraseñas comunes

**Números de Documento**:
- Solo caracteres permitidos: A-Z, 0-9, guiones
- Longitud máxima: 50 caracteres
- Sanitización: Eliminar espacios y caracteres especiales

**Preguntas (Query)**:
- Longitud mínima: 5 caracteres
- Longitud máxima: 1000 caracteres
- Sanitización: Eliminar caracteres de control

**IDs**:
- Solo enteros positivos
- Validación de rango según tipo

#### Ejemplo de Sanitización

```python
def sanitize_input(text: str, max_length: int = 1000) -> str:
    # Eliminar caracteres de control excepto \n y \r
    sanitized = ''.join(
        char for char in text 
        if char.isprintable() or char in '\n\r'
    )
    
    # Truncar si es muy largo
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized.strip()

# Uso
user_input = "   Hola\x00\x01Mundo   "
clean_input = sanitize_input(user_input)
# Resultado: "HolaMundo"
```

---

## Configuración y Uso

### 7.1 Iniciar el Servidor

#### Modo Desarrollo

```bash
# Asegurarse de tener el entorno virtual activado
cd src

# Iniciar con auto-reload
uvicorn app.main:app --reload --port 8088

# Salida esperada:
# INFO:     Uvicorn running on http://127.0.0.1:8088
# INFO:     Application startup complete.
```

**Ventajas**:
- Auto-reload al cambiar código
- Logs detallados
- Documentación API habilitada

#### Modo Producción

```bash
cd src

# Con Gunicorn (recomendado)
gunicorn app.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8088 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log

# Con Uvicorn (alternativa)
uvicorn app.main:app --host 0.0.0.0 --port 8088 --workers 4
```

**Parámetros importantes**:
- `-w 4`: 4 workers (ajustar según CPU cores)
- `--bind 0.0.0.0`: Escuchar en todas las interfaces
- `--access-logfile`: Log de accesos
- `--error-logfile`: Log de errores

### 7.2 Documentación de la API

#### Swagger UI (Desarrollo)

URL: http://localhost:8088/docs

Características:
- Interfaz interactiva
- Probar endpoints directamente
- Ver schemas de datos
- Generar código de ejemplo

#### ReDoc (Desarrollo)

URL: http://localhost:8088/redoc

Características:
- Documentación más limpia
- Mejor para lectura
- Exportar a PDF

**IMPORTANTE**: En producción, estas URLs están deshabilitadas por seguridad.

### 7.3 WebSocket Chat

#### Características

- Autenticación JWT obligatoria
- Streaming token por token
- Búsqueda vectorial en tiempo real
- Rate limiting (20 msg/min)
- Keep-alive (ping/pong)
- Timeout configurable (5 min)

#### Conectar al WebSocket

**URL**: `ws://localhost:8088/ws/chat?token=<JWT_TOKEN>`

**Paso 1: Obtener Token**

```bash
curl -X POST "http://localhost:8088/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@ejemplo.com",
    "password": "SecurePass123!"
  }'

# Respuesta:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "token_type": "bearer"
# }
```

**Paso 2: Conectar con JavaScript**

```javascript
// Copiar el token del paso anterior
const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...";

// Conectar
const ws = new WebSocket(`ws://localhost:8088/ws/chat?token=${token}`);

// Evento: Conexión establecida
ws.onopen = () => {
  console.log('Conectado');
};

// Evento: Mensaje recibido
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Mensaje:', data);
  
  switch(data.type) {
    case 'connected':
      console.log('Bienvenida:', data.message);
      break;
    case 'token':
      // Token de respuesta (streaming)
      process.stdout.write(data.token);
      break;
    case 'complete':