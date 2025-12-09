# DATABASE_SETUP.md - Guía de Instalación de Base de Datos

## Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Instalación Paso a Paso](#instalación-paso-a-paso)
3. [Verificación de la Instalación](#verificación-de-la-instalación)
4. [Configuración de Credenciales](#configuración-de-credenciales)
5. [Troubleshooting](#troubleshooting)
6. [Scripts de Mantenimiento](#scripts-de-mantenimiento)

---

## Requisitos Previos

### Software Necesario

- **PostgreSQL 16+** instalado y corriendo
- **Python 3.9+** instalado
- **psql** (cliente de PostgreSQL) en PATH
- **Git** (para clonar el repositorio)

### Verificar Instalación de PostgreSQL

```bash
# Verificar versión de PostgreSQL
psql --version

# Verificar que el servicio está corriendo
# Windows:
sc query postgresql-x64-16

# Linux:
sudo systemctl status postgresql

# Mac:
brew services list | grep postgresql
```

### Permisos Necesarios

- Acceso a usuario `postgres` (superusuario de PostgreSQL)
- Permisos para crear bases de datos y roles
- Permisos para instalar extensiones (pgvector)

---

## Instalación Paso a Paso

### Paso 1: Preparar el Entorno

```bash
# 1. Clonar el repositorio (si aún no lo has hecho)
git clone git@github.com:Ospino89/-backend-fapi-bdi-smart_health.git
cd -backend-fapi-bdi-smart_health

# 2. Navegar al directorio de pipelines
cd pipelines

# 3. Crear entorno virtual de Python
python -m venv venv

# 4. Activar el entorno virtual
# Windows:
.\venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# 5. Instalar dependencias necesarias
pip install psycopg2-binary tqdm python-dotenv
```

**Confirmación:** Deberías ver `(venv)` al inicio de tu terminal.

---

### Paso 2: Configurar Contraseñas

Antes de ejecutar los scripts, necesitas configurar las contraseñas en varios archivos.

#### Archivos a Modificar:

1. **pipelines/01-create-database/script-01.py**
```python
# Buscar y modificar:
password="sm2025"  # Cambiar por tu contraseña
```

2. **pipelines/01-create-database/script-02.py**
```python
# Buscar y modificar:
password="sm2025"  # Cambiar por tu contraseña
```

3. **pipelines/02-insert-data/create-tables.py**
```python
# Buscar y modificar:
password="sm2025"  # Cambiar por tu contraseña
```

4. **Archivo .env en la raíz del proyecto**
```env
DB_PASSWORD=sm2025  # Debe coincidir con los scripts
```

**IMPORTANTE:** Todas las contraseñas deben ser IDÉNTICAS.

---

### Paso 3: Limpiar Base de Datos Anterior (Si Existe)

Este paso es necesario si ya tienes una instalación previa.

```bash
# 1. Abrir una nueva terminal (NO cerrar la del entorno virtual)

# 2. Conectar a PostgreSQL como superusuario
psql -U postgres -d postgres

# 3. Dentro de psql, ejecutar estos comandos:
```

```sql
-- Terminar conexiones activas a la base de datos
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'smarthdb'
  AND pid <> pg_backend_pid();

-- Eliminar base de datos si existe
DROP DATABASE IF EXISTS smarthdb;

-- Eliminar rol si existe
DROP ROLE IF EXISTS sm_admin;

-- Verificar que se eliminaron
\l        -- Lista bases de datos (no debería aparecer smarthdb)
\du       -- Lista roles (no debería aparecer sm_admin)

-- Salir de psql
\q
```

**Confirmación:** No deberías ver errores. Si los hay, anótalos para el troubleshooting.

---

### Paso 4: Crear Base de Datos y Usuario

Vuelve a la terminal con el entorno virtual activado.

```bash
# 1. Asegurarte de estar en pipelines/01-create-database/
cd pipelines/01-create-database

# 2. Ejecutar el primer script
python script-01.py
```

**Salida Esperada:**
```
Conectando a PostgreSQL...
Creando base de datos 'smarthdb'...
Creando rol 'sm_admin'...
Base de datos creada exitosamente.
```

**Si hay errores:** Ir a la sección de [Troubleshooting](#troubleshooting).

---

### Paso 5: Otorgar Permisos de Superusuario

Este paso es CRÍTICO para poder instalar la extensión pgvector.

```bash
# 1. Volver a la terminal de psql
psql -U postgres -d postgres

# 2. Conectar a la nueva base de datos
\c smarthdb

# 3. Otorgar permisos de superusuario
ALTER USER sm_admin WITH SUPERUSER;

# 4. Verificar que se otorgaron los permisos
\du
```

**Salida Esperada:**
```
                                   List of roles
 Role name |                         Attributes                         
-----------+------------------------------------------------------------
 sm_admin  | Superuser                                                 
 postgres  | Superuser, Create role, Create DB, Replication, Bypass RLS
```

**Confirmación:** `sm_admin` debe tener el atributo "Superuser".

```sql
-- Salir de psql (DEJAR ESTA TERMINAL ABIERTA para pasos siguientes)
\q
```

---

### Paso 6: Instalar Extensión pgvector

Vuelve a la terminal con el entorno virtual.

```bash
# 1. Ejecutar el segundo script
python script-02.py
```

**Salida Esperada:**
```
Conectando a PostgreSQL...
Instalando extensión pgvector...
Extensión pgvector instalada exitosamente.
```

**Verificar instalación de pgvector:**

En la terminal de psql:
```sql
\c smarthdb
\dx
```

**Salida Esperada:**
```
                                     List of installed extensions
  Name   | Version |   Schema   |                        Description                        
---------+---------+------------+-----------------------------------------------------------
 pgvector| 0.5.1   | public     | vector data type and ivfflat and hnsw access methods
 plpgsql | 1.0     | pg_catalog | PL/pgSQL procedural language
```

---

### Paso 7: Crear Esquema y Tablas

```bash
# 1. Cambiar al directorio de inserción de datos
cd ../02-insert-data

# 2. Verificar que estás en el directorio correcto
pwd
# Deberías ver: .../pipelines/02-insert-data

# 3. Ejecutar script de creación de tablas
python create-tables.py
```

**Salida Esperada:**
```
Conectando a PostgreSQL...
Creando esquema smart_health...
Creando tabla patients...
Creando tabla doctors...
Creando tabla appointments...
... (más tablas)
Tablas creadas exitosamente.
```

---

### Paso 8: Insertar Datos de Ejemplo

```bash
# Ejecutar script de inserción de datos
python script-02.py
```

**Salida Esperada:**
```
Conectando a PostgreSQL...
Insertando datos en patients...
Progreso: 100%|████████████████████| 100/100
Insertando datos en doctors...
Progreso: 100%|████████████████████| 50/50
... (más tablas)
Datos insertados exitosamente.
```

**IMPORTANTE:** Este proceso puede tardar varios minutos dependiendo de la cantidad de datos.

---

### Paso 9: Generar Embeddings (Opcional pero Recomendado)

Si quieres usar la búsqueda vectorial con datos reales:

```bash
# 1. Volver a la raíz del proyecto
cd ../../

# 2. Asegurarte de tener OpenAI configurado en .env
# Verificar que OPENAI_API_KEY está configurada

# 3. Ejecutar script de generación de embeddings
cd src
python -m app.services.generate_embeddings
```

**Salida Esperada:**
```
Iniciando generación de embeddings...
Actualizando medical records: 100/100
Actualizando patients: 50/50
Actualizando doctors: 25/25
...
Proceso completado exitosamente.
```

**NOTA:** Este proceso consume créditos de OpenAI. Solo ejecutar si tienes créditos disponibles.

---

## Verificación de la Instalación

### Verificaciones Esenciales

#### 1. Verificar Base de Datos

```sql
-- Conectar a PostgreSQL
psql -U sm_admin -d smarthdb

-- Listar esquemas (debe aparecer smart_health)
\dn

-- Salida esperada:
--     List of schemas
--      Name       |  Owner   
-- ----------------+----------
--  public         | postgres
--  smart_health   | sm_admin
```

#### 2. Verificar Tablas

```sql
-- Listar todas las tablas del esquema smart_health
\dt smart_health.*

-- Salida esperada (13 tablas):
--  smart_health | appointments
--  smart_health | audit_logs
--  smart_health | diagnoses
--  smart_health | doctors
--  smart_health | doctor_specialties
--  smart_health | medications
--  smart_health | medical_records
--  smart_health | patients
--  smart_health | prescriptions
--  smart_health | record_diagnoses
--  smart_health | rooms
--  smart_health | specialties
--  smart_health | users
```

#### 3. Verificar Datos

```sql
-- Contar registros en cada tabla
SELECT 
    schemaname,
    tablename,
    n_live_tup as row_count
FROM pg_stat_user_tables
WHERE schemaname = 'smart_health'
ORDER BY tablename;

-- Verificar pacientes
SELECT COUNT(*) FROM smart_health.patients;
-- Debe retornar > 0

-- Verificar usuarios
SELECT COUNT(*) FROM smart_health.users;
-- Debe retornar > 0
```

#### 4. Verificar Extensiones

```sql
-- Verificar que pgvector está instalado
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Salida esperada:
--  oid  | extname | extowner | extnamespace | extrelocatable | extversion 
-- ------+---------+----------+--------------+----------------+------------
-- 16390 | vector  |       10 |         2200 | f              | 0.5.1
```

#### 5. Verificar Columnas de Embeddings

```sql
-- Verificar que las columnas de embeddings existen
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_schema = 'smart_health' 
  AND column_name LIKE '%embedding%';

-- Salida esperada:
--     column_name      | data_type 
-- ---------------------+-----------
--  summary_embedding   | USER-DEFINED (vector)
--  fullname_embedding  | USER-DEFINED (vector)
--  reason_embedding    | USER-DEFINED (vector)
--  ...
```

---

## Configuración de Credenciales

### Archivo .env

Crear/modificar el archivo `.env` en la raíz del proyecto:

```env
# Base de datos
DB_HOST=localhost
DB_PORT=5432
DB_NAME=smarthdb
DB_USER=sm_admin
DB_PASSWORD=sm2025

# Seguridad
SECRET_KEY=tu_clave_secreta_generada_con_secrets_token_hex_32

# OpenAI (solo si vas a usar embeddings)
OPENAI_API_KEY=sk-tu-api-key-aqui

# Configuración LLM
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=2000
LLM_TIMEOUT=30
```

### Verificar Conexión desde Python

```python
# test_connection.py
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://sm_admin:sm2025@localhost:5432/smarthdb"
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM smart_health.patients"))
        count = result.scalar()
        print(f"Conexión exitosa. Pacientes en la base de datos: {count}")
except Exception as e:
    print(f"Error de conexión: {e}")
```

---

## Troubleshooting

### Error: "role sm_admin already exists"

**Causa:** El rol ya existe de una instalación anterior.

**Solución:**
```sql
psql -U postgres -d postgres
DROP ROLE IF EXISTS sm_admin;
\q
```

---

### Error: "database smarthdb already exists"

**Causa:** La base de datos ya existe de una instalación anterior.

**Solución:**
```sql
psql -U postgres -d postgres

-- Cerrar conexiones activas
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'smarthdb';

DROP DATABASE IF EXISTS smarthdb;
\q
```

---

### Error: "permission denied to create extension pgvector"

**Causa:** El usuario `sm_admin` no tiene permisos de superusuario.

**Solución:**
```sql
psql -U postgres -d smarthdb
ALTER USER sm_admin WITH SUPERUSER;
\du
\q
```

---

### Error: "psycopg2 not found" o "No module named 'psycopg2'"

**Causa:** La librería psycopg2 no está instalada.

**Solución:**
```bash
# Asegurarse de tener el entorno virtual activado
pip install psycopg2-binary

# Si persiste el error:
pip uninstall psycopg2 psycopg2-binary
pip install psycopg2-binary
```

---

### Error: "password authentication failed for user sm_admin"

**Causa:** Las contraseñas no coinciden entre los scripts y PostgreSQL.

**Solución:**
```sql
-- 1. Resetear contraseña en PostgreSQL
psql -U postgres
ALTER USER sm_admin WITH PASSWORD 'sm2025';
\q

-- 2. Verificar que todos los archivos usen la misma contraseña:
-- - pipelines/01-create-database/script-01.py
-- - pipelines/01-create-database/script-02.py
-- - pipelines/02-insert-data/create-tables.py
-- - .env
```

---

### Error: "could not connect to server"

**Causa:** PostgreSQL no está corriendo.

**Solución:**
```bash
# Windows:
net start postgresql-x64-16

# Linux:
sudo systemctl start postgresql

# Mac:
brew services start postgresql@16
```

---

### Error: "extension vector does not exist"

**Causa:** La extensión pgvector no se instaló correctamente.

**Solución:**
```sql
-- 1. Verificar que sm_admin tiene permisos
psql -U postgres -d smarthdb
\du

-- 2. Intentar instalar manualmente
CREATE EXTENSION IF NOT EXISTS vector;

-- 3. Si falla, verificar que pgvector está instalado en el sistema
-- Ver: https://github.com/pgvector/pgvector#installation
```

---

### Error: "relation smart_health.patients does not exist"

**Causa:** Las tablas no se crearon correctamente.

**Solución:**
```bash
# Verificar que el script de creación se ejecutó
cd pipelines/02-insert-data
python create-tables.py

# Verificar en psql
psql -U sm_admin -d smarthdb
\dt smart_health.*
```

---

### Problema: Scripts de Python muy lentos

**Causa:** Gran cantidad de datos a insertar.

**Solución:**
- Esperar pacientemente (puede tardar 5-10 minutos)
- Reducir cantidad de datos en los scripts si es necesario
- Verificar que la barra de progreso se está moviendo

---

## Scripts de Mantenimiento

### Backup de la Base de Datos

```bash
# Crear backup completo
pg_dump -U sm_admin -d smarthdb -F c -b -v -f "smarthdb_backup_$(date +%Y%m%d).backup"

# Restaurar desde backup
pg_restore -U sm_admin -d smarthdb -v "smarthdb_backup_20251209.backup"
```

### Limpiar Base de Datos

```bash
# Script para limpiar todos los datos pero mantener estructura
psql -U sm_admin -d smarthdb << EOF
TRUNCATE TABLE smart_health.audit_logs CASCADE;
TRUNCATE TABLE smart_health.prescriptions CASCADE;
TRUNCATE TABLE smart_health.record_diagnoses CASCADE;
TRUNCATE TABLE smart_health.medical_records CASCADE;
TRUNCATE TABLE smart_health.appointments CASCADE;
TRUNCATE TABLE smart_health.patients CASCADE;
TRUNCATE TABLE smart_health.doctor_specialties CASCADE;
TRUNCATE TABLE smart_health.doctors CASCADE;
TRUNCATE TABLE smart_health.users CASCADE;
EOF
```

### Recrear Base de Datos Completa

```bash
# Script completo para reinstalar
cd pipelines
./reinstall_database.sh  # Linux/Mac
# o
reinstall_database.bat   # Windows
```

**Contenido del script:**
```bash
#!/bin/bash
# reinstall_database.sh

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}Reinstalando base de datos SmartHealth...${NC}"

# 1. Limpiar
echo "Limpiando base de datos anterior..."
psql -U postgres -d postgres -c "DROP DATABASE IF EXISTS smarthdb;"
psql -U postgres -d postgres -c "DROP ROLE IF EXISTS sm_admin;"

# 2. Crear
echo "Creando base de datos..."
cd 01-create-database
python script-01.py

# 3. Permisos
echo "Otorgando permisos..."
psql -U postgres -d smarthdb -c "ALTER USER sm_admin WITH SUPERUSER;"

# 4. Extensión
echo "Instalando pgvector..."
python script-02.py

# 5. Tablas
echo "Creando tablas..."
cd ../02-insert-data
python create-tables.py

# 6. Datos
echo "Insertando datos..."
python script-02.py

echo -e "${GREEN}Instalación completada exitosamente.${NC}"
```

---

## Próximos Pasos

Una vez completada la instalación:

1. **Iniciar la API**:
```bash
cd src
uvicorn app.main:app --reload --port 8088
```

2. **Probar la conexión**:
```bash
curl http://localhost:8088/health
```

3. **Crear un usuario**:
```bash
curl -X POST "http://localhost:8088/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@smarthealth.com",
    "password": "SecurePass123!",
    "first_name": "Admin",
    "first_surname": "User"
  }'
```

4. **Generar embeddings** (opcional):
```bash
cd src
python -m app.services.generate_embeddings
```

---

## Recursos Adicionales

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [psycopg2 Documentation](https://www.psycopg.org/docs/)

---

**Última actualización:** Diciembre 2025  
**Autor:** Equipo SmartHealth