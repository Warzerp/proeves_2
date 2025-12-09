# 🔌 WebSocket - SmartHealth API

## 📋 Resumen

Este proyecto incluye un endpoint WebSocket para realizar consultas RAG (Retrieval-Augmented Generation) en tiempo real con streaming de respuestas token por token.

---

## 🎯 Características

- ✅ **Autenticación JWT** mediante query params o headers
- ✅ **Streaming en tiempo real** de respuestas del LLM
- ✅ **Búsqueda vectorial** integrada
- ✅ **Manejo de timeouts** configurables
- ✅ **Keep-alive con ping/pong**
- ✅ **Manejo robusto de errores**
- ✅ **Múltiples sesiones simultáneas**

---

## 📦 Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Verificar variables de entorno

Asegúrate de que tu `.env` contenga:

```env
OPENAI_API_KEY=sk-...
DB_HOST=localhost
DB_PORT=5432
DB_NAME=smarthealth
DB_USER=postgres
DB_PASSWORD=tu_password
SECRET_KEY=tu_clave_secreta
```

### 3. Iniciar el servidor

```bash
cd src
uvicorn app.main:app --reload --port 8088
```

Verifica que el servidor esté corriendo:
```
✅ WebSocket disponible en: ws://localhost:8088/ws/chat
```

---

## 🔐 Autenticación

### Obtener un token JWT

```bash
curl -X POST "http://localhost:8088/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "tu@email.com",
    "password": "tupassword"
  }'
```

Respuesta:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### Conectar al WebSocket

**Opción 1: Token en query params (recomendado)**
```
ws://localhost:8088/ws/chat?token=TU_TOKEN_JWT
```

**Opción 2: Token en header Authorization**
```javascript
const ws = new WebSocket('ws://localhost:8088/ws/chat', {
  headers: {
    'Authorization': 'Bearer TU_TOKEN_JWT'
  }
});
```

---

## 📨 Protocolo de Mensajes

### Mensajes del Cliente → Servidor

#### 1. Query (Consulta médica)

```json
{
  "type": "query",
  "session_id": "uuid-v4",
  "document_type_id": 8,
  "document_number": "30995750",
  "question": "¿Cuál es el historial médico del paciente?"
}
```

**Campos:**
- `type`: Siempre "query"
- `session_id`: UUID único para la sesión (generado por el cliente)
- `document_type_id`: Tipo de documento (1=CC, 8=CD, etc.)
- `document_number`: Número de documento del paciente
- `question`: Pregunta en lenguaje natural

#### 2. Ping (Keep-alive)

```json
{
  "type": "ping"
}
```

---

### Mensajes del Servidor → Cliente

#### 1. Connected (Bienvenida)

```json
{
  "type": "connected",
  "user_id": 123,
  "message": "✅ Conectado exitosamente al chat médico"
}
```

#### 2. Status (Actualizaciones de progreso)

```json
{
  "type": "status",
  "status": "searching_patient",
  "message": "🔍 Buscando datos del paciente..."
}
```

**Valores de `status`:**
- `searching_patient`: Buscando paciente en BD
- `vector_search`: Realizando búsqueda semántica
- `building_context`: Construyendo contexto clínico
- `generating`: Generando respuesta con LLM

#### 3. Stream Start (Inicio del streaming)

```json
{
  "type": "stream_start",
  "session_id": "uuid",
  "timestamp": "2024-12-08T10:30:00Z"
}
```

#### 4. Token (Cada token del LLM)

```json
{
  "type": "token",
  "token": "El ",
  "session_id": "uuid"
}
```

#### 5. Stream End (Fin del streaming)

```json
{
  "type": "stream_end",
  "session_id": "uuid",
  "timestamp": "2024-12-08T10:30:15Z"
}
```

#### 6. Complete (Respuesta completa)

```json
{
  "type": "complete",
  "session_id": "uuid",
  "timestamp": "2024-12-08T10:30:15Z",
  "patient_info": {
    "patient_id": 1,
    "full_name": "Laura Morales",
    "document_type": "CD",
    "document_number": "30995750"
  },
  "answer": {
    "text": "Respuesta completa del LLM...",
    "confidence": 0.85,
    "model_used": "gpt-4o-mini"
  },
  "metadata": {
    "total_records_analyzed": 25,
    "vector_chunks_used": 5
  }
}
```

#### 7. Error

```json
{
  "type": "error",
  "error": {
    "code": "PATIENT_NOT_FOUND",
    "message": "No se encontró paciente con documento CD 30995750"
  }
}
```

**Códigos de error:**
- `INVALID_REQUEST`: Faltan campos requeridos
- `PATIENT_NOT_FOUND`: Paciente no existe
- `VECTOR_SEARCH_TIMEOUT`: Búsqueda vectorial excedió timeout
- `LLM_TIMEOUT`: LLM tardó demasiado
- `LLM_ERROR`: Error generando respuesta
- `PROCESSING_ERROR`: Error genérico
- `REQUEST_TIMEOUT`: Request completo excedió timeout

#### 8. Pong (Respuesta a ping)

```json
{
  "type": "pong"
}
```

---

## 🧪 Testing

### Opción 1: Script Python

```bash
# Edita test_websocket.py y configura el TOKEN
python test_websocket.py
```

El script incluye:
- ✅ Test completo con streaming
- ✅ Test ping/pong
- ✅ Test de autenticación
- ✅ Menú interactivo

### Opción 2: Cliente HTML

Abre `test_websocket.html` en tu navegador:
1. Pega tu token JWT
2. Configura tipo y número de documento
3. Escribe tu pregunta
4. Haz clic en "Conectar WebSocket"
5. Haz clic en "Enviar Pregunta"
6. Observa el streaming en tiempo real

---

## 🔧 Configuración de Timeouts

En `src/app/routers/websocket_chat.py`:

```python
VECTOR_SEARCH_TIMEOUT = 10  # segundos
LLM_TIMEOUT = 45            # segundos
TOTAL_REQUEST_TIMEOUT = 60  # segundos
```

---

## 📊 Ejemplo de Flujo Completo

### 1. Cliente conecta

```javascript
const ws = new WebSocket('ws://localhost:8088/ws/chat?token=...');

ws.onopen = () => console.log('Conectado');
```

### 2. Servidor responde con bienvenida

```json
{"type": "connected", "user_id": 123, "message": "✅ Conectado..."}
```

### 3. Cliente envía query

```javascript
ws.send(JSON.stringify({
  type: 'query',
  session_id: crypto.randomUUID(),
  document_type_id: 8,
  document_number: '30995750',
  question: '¿Cuál es el historial médico?'
}));
```

### 4. Servidor procesa (status updates)

```json
{"type": "status", "message": "🔍 Buscando datos..."}
{"type": "status", "message": "🔎 Búsqueda vectorial..."}
{"type": "status", "message": "🤖 Generando respuesta..."}
```

### 5. Servidor inicia streaming

```json
{"type": "stream_start", ...}
{"type": "token", "token": "El "}
{"type": "token", "token": "paciente "}
{"type": "token", "token": "tiene "}
...
{"type": "stream_end", ...}
```

### 6. Servidor envía respuesta completa

```json
{"type": "complete", "answer": {...}, "metadata": {...}}
```

---

## 🐛 Troubleshooting

### Error: "Token inválido"

**Causa:** Token expirado o mal formateado

**Solución:**
```bash
# Obtén un nuevo token
curl -X POST http://localhost:8088/auth/login ...
```

### Error: "Connection refused"

**Causa:** Servidor no está corriendo

**Solución:**
```bash
cd src
uvicorn app.main:app --reload --port 8088
```

### Error: "PATIENT_NOT_FOUND"

**Causa:** El paciente no existe en la BD

**Solución:** Verifica el tipo y número de documento

### Error: "LLM_TIMEOUT"

**Causa:** OpenAI API tardó demasiado

**Solución:** 
- Verifica tu OPENAI_API_KEY
- Aumenta LLM_TIMEOUT si es necesario
- Verifica tu conexión a internet

---

## 📚 Documentación API

Una vez el servidor esté corriendo:

- **Swagger UI:** http://localhost:8088/docs
- **ReDoc:** http://localhost:8088/redoc
- **Health Check:** http://localhost:8088/health

---

## 🔒 Seguridad

### Producción

1. **Configurar CORS específico:**

```python
# En main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tudominio.com"],  # ← Específico
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

2. **Usar HTTPS/WSS:**

```
wss://tu-servidor.com/ws/chat?token=...
```

3. **Rotar SECRET_KEY regularmente**

4. **Implementar rate limiting** (no incluido actualmente)

---

## 📞 Soporte

Para problemas o preguntas:
- 📧 Email: soporte@smarthealth.com
- 📚 Docs: https://docs.smarthealth.com
- 🐛 Issues: https://github.com/tu-repo/issues

---

## 📝 Changelog

### v2.0.0 (2024-12-08)
- ✅ WebSocket con streaming en tiempo real
- ✅ Autenticación JWT
- ✅ Búsqueda vectorial integrada
- ✅ Manejo robusto de errores
- ✅ Tests automatizados

---

## 📄 Licencia

[Tu Licencia Aquí]