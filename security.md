# SECURITY.md - Guía de Seguridad

## Tabla de Contenidos

1. [Principios de Seguridad](#principios-de-seguridad)
2. [Configuración Segura](#configuración-segura)
3. [Autenticación y Autorización](#autenticación-y-autorización)
4. [Protección de Datos](#protección-de-datos)
5. [Rate Limiting](#rate-limiting)
6. [Validación de Inputs](#validación-de-inputs)
7. [Logging y Auditoría](#logging-y-auditoría)
8. [Despliegue Seguro](#despliegue-seguro)
9. [Reporte de Vulnerabilidades](#reporte-de-vulnerabilidades)

---

## Principios de Seguridad

El proyecto SmartHealth sigue los siguientes principios de seguridad:

1. **Defense in Depth**: Múltiples capas de seguridad
2. **Least Privilege**: Mínimos permisos necesarios
3. **Secure by Default**: Configuración segura por defecto
4. **Fail Secure**: Fallar de forma segura
5. **Keep It Simple**: Simplicidad en la implementación de seguridad

---

## Configuración Segura

### Variables de Entorno

**CRÍTICO**: Nunca commitear el archivo `.env` al repositorio.

#### Generación de SECRET_KEY Segura

```python
import secrets
print(secrets.token_hex(32))
```

La SECRET_KEY debe:
- Tener al menos 32 caracteres
- Ser completamente aleatoria
- Ser única por entorno (dev, staging, prod)
- Rotarse periódicamente (cada 90 días)

#### Variables Sensibles

Las siguientes variables NUNCA deben compartirse:

- `SECRET_KEY`: Clave de firma JWT
- `DB_PASSWORD`: Contraseña de base de datos
- `OPENAI_API_KEY`: API key de OpenAI
- Cualquier otra credencial o token

#### Checklist de Configuración

- [ ] `.env` está en `.gitignore`
- [ ] `SECRET_KEY` tiene al menos 32 caracteres
- [ ] `DB_PASSWORD` es fuerte (16+ caracteres, mixto)
- [ ] `OPENAI_API_KEY` es válida y tiene límites configurados
- [ ] `APP_ENV` está configurado correctamente
- [ ] CORS está configurado restrictivamente en producción

---

## Autenticación y Autorización

### Requisitos de Contraseñas

Las contraseñas deben cumplir:

- Mínimo 8 caracteres
- Al menos 1 letra mayúscula
- Al menos 1 letra minúscula
- Al menos 1 número
- Al menos 1 carácter especial

Ejemplo de contraseña válida: `SecurePass123!`

### Hashing de Contraseñas

- Algoritmo: **bcrypt**
- Factor de costo: **12** (configurado en passlib)
- Nunca almacenar contraseñas en texto plano

### Tokens JWT

**Configuración:**
- Algoritmo: HS256
- Expiración: 30 minutos (configurable)
- Payload incluye: user_id, email, is_active

**Buenas prácticas:**
- Validar token en cada request protegido
- Verificar expiración
- Renovar token antes de expirar
- Invalidar tokens al logout (implementar blacklist si es necesario)

### Flujo de Autenticación

```
1. Usuario envía credenciales a /auth/login
2. Sistema valida credenciales
3. Si es válido, genera JWT
4. Cliente almacena JWT (localStorage/sessionStorage)
5. Cliente envía JWT en header Authorization: Bearer <token>
6. Sistema valida JWT en cada request
```

---

## Protección de Datos

### Datos en Tránsito

**Producción:**
- HTTPS/TLS obligatorio
- Certificados válidos
- TLS 1.2+ mínimo
- Perfect Forward Secrecy (PFS)

**Headers de Seguridad:**
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
```

### Datos en Reposo

**Base de Datos:**
- Encriptación del disco (full-disk encryption)
- Backups encriptados
- Contraseñas hasheadas (bcrypt)
- Datos sensibles encriptados (si aplica)

**Logs:**
- No loggear contraseñas
- No loggear tokens completos
- Sanitizar datos sensibles
- Rotar logs periódicamente

---

## Rate Limiting

### Límites Implementados

**WebSocket:**
- 20 mensajes/minuto por usuario
- Implementado en `ConnectionManager`

**API REST (Producción):**
- 100 requests/minuto por IP
- Implementado en `RateLimitMiddleware`

### Configuración

Ajustar en `.env`:
```env
WEBSOCKET_RATE_LIMIT=20
GLOBAL_RATE_LIMIT=100
```

### Respuestas de Rate Limit

HTTP Status: `429 Too Many Requests`

```json
{
  "detail": "Too many requests"
}
```

---

## Validación de Inputs

### Principios

1. **Whitelist, no Blacklist**: Validar lo permitido, no lo prohibido
2. **Validar en el servidor**: Nunca confiar en validación del cliente
3. **Sanitizar siempre**: Limpiar todos los inputs

### Implementación

**Ejemplo de sanitización:**

```python
def sanitize_input(text: str, max_length: int = 1000) -> str:
    # Eliminar caracteres de control
    sanitized = ''.join(char for char in text if char.isprintable() or char in '\n\r')
    
    # Truncar si es muy largo
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized.strip()
```

### Validaciones Aplicadas

- **Email**: Formato válido con regex
- **Contraseñas**: Requisitos de complejidad
- **Números de documento**: Tipo y formato válidos
- **Preguntas**: Longitud mínima/máxima
- **IDs**: Tipos correctos y rangos válidos

---

## Logging y Auditoría

### Qué Loggear

**SI loggear:**
- Intentos de login (éxito y fallo)
- Acciones de usuarios autenticados
- Errores y excepciones
- Cambios en configuración
- Acceso a datos sensibles

**NO loggear:**
- Contraseñas (nunca)
- Tokens completos
- Números de tarjetas
- Información médica sin anonimizar

### Niveles de Log

```python
DEBUG: Información detallada para debugging
INFO: Eventos normales del sistema
WARNING: Situaciones inusuales pero manejables
ERROR: Errores que requieren atención
CRITICAL: Errores críticos del sistema
```

### Formato de Logs

```
2025-12-09 10:30:45 - app.services.auth_service - INFO - Login exitoso: user@example.com
```

### Rotación de Logs

- Tamaño máximo: 100MB
- Mantener: 30 días
- Comprimir logs antiguos
- Eliminar logs > 90 días

---

## Despliegue Seguro

### Checklist Pre-Deployment

#### Configuración

- [ ] `SECRET_KEY` única y segura
- [ ] `APP_ENV=production`
- [ ] HTTPS/TLS configurado
- [ ] CORS restrictivo
- [ ] Rate limiting habilitado
- [ ] Logs configurados
- [ ] Backups automáticos

#### Base de Datos

- [ ] Contraseña fuerte
- [ ] Firewall configurado
- [ ] Solo localhost o IPs específicas
- [ ] Encriptación habilitada
- [ ] Backups configurados

#### Aplicación

- [ ] Documentación API deshabilitada (`/docs`, `/redoc`)
- [ ] OpenAPI spec deshabilitada
- [ ] Debug mode deshabilitado
- [ ] Error messages genéricos
- [ ] Dependencies actualizadas

#### Infraestructura

- [ ] Firewall configurado
- [ ] SSH con key-based auth
- [ ] Fail2ban o similar
- [ ] Monitoreo activo
- [ ] Alertas configuradas

### Docker Security

**Dockerfile seguro:**

```dockerfile
FROM python:3.9-slim

# No ejecutar como root
RUN useradd -m -u 1000 appuser

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

# Cambiar a usuario no privilegiado
USER appuser

EXPOSE 8088
CMD ["gunicorn", "src.app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8088"]
```

**Docker Compose seguro:**

```yaml
version: '3.8'

services:
  api:
    build: .
    environment:
      - APP_ENV=production
    env_file:
      - .env
    ports:
      - "127.0.0.1:8088:8088"  # Solo localhost
    restart: unless-stopped
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
    cap_drop:
      - ALL
```

---

## Mantenimiento de Seguridad

### Actualizaciones

**Frecuencia:**
- Dependencies: Mensual
- Python: Cada 6 meses
- Sistema operativo: Semanal (patches de seguridad)

**Comando para actualizar:**

```bash
pip list --outdated
pip install --upgrade pip
pip install --upgrade -r requirements.txt
```

### Auditorías

**Herramientas:**

```bash
# Vulnerabilidades en dependencias
pip install safety
safety check

# Análisis estático de código
pip install bandit
bandit -r src/

# Linting de seguridad
pip install pylint
pylint src/
```

### Rotación de Credenciales

**Calendario:**
- `SECRET_KEY`: Cada 90 días
- `DB_PASSWORD`: Cada 180 días
- `OPENAI_API_KEY`: Al detectar uso anómalo
- Certificados TLS: Antes de expirar

---

## Reporte de Vulnerabilidades

### Proceso

1. **NO crear issue público** con detalles de vulnerabilidad
2. Enviar email a: security@smarthealth.com (ejemplo)
3. Incluir:
   - Descripción de la vulnerabilidad
   - Pasos para reproducir
   - Impacto potencial
   - Versión afectada

### Respuesta Esperada

- Confirmación: 24 horas
- Análisis inicial: 3 días
- Fix y release: 7-14 días
- Crédito al reporter (si lo desea)

### Recompensas

Consideramos implementar un programa de bug bounty para:
- Vulnerabilidades críticas
- Bypass de autenticación
- Inyección SQL
- XSS persistente
- Escalada de privilegios

---

## Recursos Adicionales

### Documentación de Seguridad

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)

### Herramientas Recomendadas

- **Safety**: Escaneo de vulnerabilidades
- **Bandit**: Análisis de seguridad
- **SAST**: Static Application Security Testing
- **DAST**: Dynamic Application Security Testing
- **SonarQube**: Análisis de código

### Contacto

Para consultas de seguridad:
- Email: security@smarthealth.com
- PGP Key: [Incluir fingerprint]

---

## Política de Divulgación

SmartHealth sigue una política de **divulgación responsable**:

1. Reporter notifica en privado
2. Confirmamos y analizamos (3 días)
3. Desarrollamos fix (7-14 días)
4. Publicamos fix y advisory
5. Damos crédito al reporter (opcional)

---

**Última actualización**: Diciembre 2025  