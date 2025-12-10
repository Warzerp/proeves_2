"""
SmartHealth API - Suite de Pruebas de Seguridad v2.1
=====================================================
Ejecutar: python test_security.py

Verifica:
1. Autenticación JWT
2. Headers de seguridad
3. CORS
4. Validación de inputs (Anti-Jailbreak)
5. WebSocket security
6. SQL Injection protection
"""

import sys
from pathlib import Path

# ✅ Rutas absolutas para despliegue
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

import requests
import json
import time
from typing import Dict, Optional
import websockets
import asyncio

# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_URL = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000"

# Colores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_test(name: str):
    """Imprime el nombre del test"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}━━━ {name} ━━━{Colors.RESET}")

def print_pass(message: str):
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN} PASS:{Colors.RESET} {message}")

def print_fail(message: str):
    """Imprime mensaje de fallo"""
    print(f"{Colors.RED} FAIL:{Colors.RESET} {message}")

def print_info(message: str):
    """Imprime información"""
    print(f"{Colors.YELLOW}ℹ  INFO:{Colors.RESET} {message}")

# ============================================================
# TESTS DE AUTENTICACIÓN JWT
# ============================================================

def test_jwt_authentication():
    """Verifica el sistema de autenticación JWT"""
    print_test("AUTENTICACIÓN JWT")
    
    # 1. Registro de usuario
    print("\n 1 Probando registro de usuario...")
    register_data = {
        "email": f"security_test_{int(time.time())}@test.com",
        "password": "SecurePass123!",
        "first_name": "Security",
        "first_surname": "Test"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if response.status_code == 201:
            print_pass("Usuario registrado correctamente")
        else:
            print_fail(f"Error en registro: {response.status_code}")
            return None
    except Exception as e:
        print_fail(f"Error conectando: {e}")
        return None
    
    # 2. Login y obtención de token
    print("\n 2 Probando login...")
    login_data = {
        "email": register_data["email"],
        "password": register_data["password"]
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        token = response.json().get("access_token")
        print_pass(f"Login exitoso. Token: {token[:20]}...")
    else:
        print_fail(f"Error en login: {response.status_code}")
        return None
    
    # 3. Acceso sin token (debe fallar)
    print("\n 3 Intentando acceso sin token...")
    response = requests.get(f"{BASE_URL}/users/me")
    if response.status_code == 401 or response.status_code == 403:
        print_pass("Acceso correctamente denegado sin token")
    else:
        print_fail(f"Acceso permitido sin token (código: {response.status_code})")
    
    # 4. Acceso con token válido
    print("\n 4 Intentando acceso con token válido...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    if response.status_code == 200:
        print_pass("Acceso permitido con token válido")
    else:
        print_fail(f"Acceso denegado con token válido (código: {response.status_code})")
    
    # 5. Acceso con token inválido
    print("\n 5 Intentando acceso con token inválido...")
    bad_headers = {"Authorization": "Bearer token_falso_123"}
    response = requests.get(f"{BASE_URL}/users/me", headers=bad_headers)
    if response.status_code == 401 or response.status_code == 403:
        print_pass("Acceso correctamente denegado con token inválido")
    else:
        print_fail(f"Acceso permitido con token inválido (código: {response.status_code})")
    
    # 6. Login con credenciales incorrectas
    print("\n 6 Probando login con credenciales incorrectas...")
    bad_login = {
        "email": register_data["email"],
        "password": "PasswordIncorrecta123!"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=bad_login)
    if response.status_code == 401:
        print_pass("Login correctamente rechazado con credenciales incorrectas")
    else:
        print_fail(f"Login aceptado con credenciales incorrectas (código: {response.status_code})")
    
    return token

# ============================================================
# TESTS DE VALIDACIÓN DE INPUTS (ANTI-JAILBREAK)
# ============================================================

def test_input_validation():
    """Verifica la validación de inputs y protección contra jailbreak"""
    print_test("VALIDACIÓN DE INPUTS Y ANTI-JAILBREAK")
    
    # 1. Email inválido
    print("\n 1 Probando registro con email inválido...")
    bad_email = {
        "email": "esto_no_es_un_email",
        "password": "Pass123!",
        "first_name": "Test",
        "first_surname": "User"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=bad_email)
    if response.status_code == 422:
        print_pass("Email inválido correctamente rechazado")
    else:
        print_fail(f"Email inválido aceptado (código: {response.status_code})")
    
    # 2. Contraseña corta
    print("\n 2 Probando registro con contraseña corta...")
    short_pass = {
        "email": "test@test.com",
        "password": "123",
        "first_name": "Test",
        "first_surname": "User"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=short_pass)
    if response.status_code == 422 or response.status_code == 400:
        print_pass("Contraseña corta correctamente rechazada")
    else:
        print_fail(f"Contraseña corta aceptada (código: {response.status_code})")
    
    # 3. SQL Injection en número de documento
    print("\n 3 Probando SQL Injection en documento...")
    sql_injection_query = {
        "user_id": "1",
        "session_id": "test-123",
        "document_type_id": 1,
        "document_number": "123' OR '1'='1",
        "question": "¿Historial del paciente?"
    }
    response = requests.post(f"{BASE_URL}/query/", json=sql_injection_query)
    if response.status_code in [400, 422]:
        print_pass("SQL Injection en documento bloqueado")
    else:
        data = response.json()
        if data.get("status") == "error" and "INVALID_INPUT" in data.get("error", {}).get("code", ""):
            print_pass("SQL Injection detectado y rechazado")
        else:
            print_fail(f"SQL Injection no bloqueado (código: {response.status_code})")
    
    # 4. Documento con caracteres peligrosos
    print("\n 4 Probando documento con caracteres especiales...")
    dangerous_doc = {
        "user_id": "1",
        "session_id": "test-123",
        "document_type_id": 1,
        "document_number": "123;DROP TABLE--",
        "question": "¿Historial del paciente?"
    }
    response = requests.post(f"{BASE_URL}/query/", json=dangerous_doc)
    if response.status_code in [400, 422]:
        print_pass("Documento peligroso rechazado")
    else:
        data = response.json()
        if data.get("status") == "error":
            print_pass("Caracteres peligrosos sanitizados")
        else:
            print_info("Request procesado - verificar sanitización")
    
    # 5. Pregunta muy larga
    print("\n 5 Probando pregunta muy larga (>1000 chars)...")
    long_question = {
        "user_id": "1",
        "session_id": "test-123",
        "document_type_id": 1,
        "document_number": "123456",
        "question": "A" * 1500
    }
    response = requests.post(f"{BASE_URL}/query/", json=long_question)
    if response.status_code in [400, 422]:
        print_pass("Pregunta muy larga rechazada")
    else:
        data = response.json()
        if data.get("status") == "error" and "INVALID_INPUT" in data.get("error", {}).get("code", ""):
            print_pass("Pregunta muy larga detectada y rechazada")
        else:
            print_fail(f"Pregunta muy larga aceptada")
    
    # 6. Tipo de documento inválido
    print("\n 6 Probando tipo de documento inválido...")
    invalid_doc_type = {
        "user_id": "1",
        "session_id": "test-123",
        "document_type_id": 99,  # X Solo 1-8 son válidos
        "document_number": "123456",
        "question": "¿Historial del paciente?"
    }
    response = requests.post(f"{BASE_URL}/query/", json=invalid_doc_type)
    if response.status_code in [400, 422]:
        print_pass("Tipo de documento inválido rechazado")
    else:
        data = response.json()
        if data.get("status") == "error":
            print_pass("Tipo de documento inválido detectado")
        else:
            print_fail(f"Tipo de documento inválido aceptado")

# ============================================================
# TESTS DE HEADERS DE SEGURIDAD
# ============================================================

def test_security_headers():
    """Verifica que los headers de seguridad estén presentes"""
    print_test("HEADERS DE SEGURIDAD")
    
    response = requests.get(f"{BASE_URL}/")
    headers = response.headers
    
    print("\n Headers recibidos:")
    
    # Headers esperados en producción
    security_headers = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
    }
    
    for header, expected_value in security_headers.items():
        if header in headers:
            if headers[header] == expected_value:
                print_pass(f"{header}: {headers[header]}")
            else:
                print_info(f"{header}: {headers[header]} (esperado: {expected_value})")
        else:
            print_info(f"{header}: No presente (normal en desarrollo)")
    
    # CORS headers
    if "Access-Control-Allow-Origin" in headers:
        print_pass(f"CORS configurado: {headers['Access-Control-Allow-Origin']}")
    else:
        print_info("CORS: No headers en GET simple (normal)")

# ============================================================
# TEST DE HEALTH CHECK
# ============================================================

def test_health_endpoint():
    """Verifica el endpoint de health"""
    print_test("HEALTH CHECK")
    
    response = requests.get(f"{BASE_URL}/health")
    
    if response.status_code == 200:
        print_pass("Endpoint /health responde correctamente")
        
        data = response.json()
        print(f"\n Estado del sistema:")
        print(f"   Versión: {data.get('version', 'N/A')}")
        print(f"   Status: {data.get('status')}")
        print(f"   Environment: {data.get('environment')}")
        
        services = data.get('services', {})
        for service, status in services.items():
            icon = "OK" if status in ["connected", "ready", "enabled"] else "X"
            print(f"   {icon} {service}: {status}")
    else:
        print_fail(f"Endpoint /health falló: {response.status_code}")

# ============================================================
# TESTS DE WEBSOCKET
# ============================================================

async def test_websocket_security(token: Optional[str]):
    """Verifica la seguridad del WebSocket"""
    print_test("SEGURIDAD WEBSOCKET")
    
    if not token:
        print_info("No hay token disponible, saltando test de WebSocket")
        return
    
    # 1. Conexión sin token
    print("\n 1 Intentando conexión WebSocket sin token...")
    try:
        async with websockets.connect(f"{WS_URL}/ws/chat") as ws:
            print_fail("Conexión WebSocket permitida sin token")
    except Exception:
        print_pass("Conexión WebSocket bloqueada sin token")
    
    # 2. Conexión con token inválido
    print("\n 2 Intentando conexión WebSocket con token inválido...")
    try:
        async with websockets.connect(f"{WS_URL}/ws/chat?token=token_falso") as ws:
            print_fail("Conexión WebSocket permitida con token inválido")
    except Exception:
        print_pass("Conexión WebSocket bloqueada con token inválido")
    
    # 3. Conexión con token válido
    print("\n 3 Intentando conexión WebSocket con token válido...")
    try:
        async with websockets.connect(f"{WS_URL}/ws/chat?token={token}") as ws:
            welcome = await asyncio.wait_for(ws.recv(), timeout=5)
            data = json.loads(welcome)
            if data.get("type") == "connected":
                print_pass("Conexión WebSocket exitosa con token válido")
            else:
                print_fail("Conexión establecida pero respuesta inesperada")
    except asyncio.TimeoutError:
        print_fail("Timeout esperando mensaje de bienvenida")
    except Exception as e:
        print_fail(f"Error en conexión: {e}")

# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================

async def run_all_tests():
    """Ejecuta todos los tests de seguridad"""
    print(f"\n{Colors.BOLD}{'='*60}")
    print(" SMARTHEALTH v2.1 - SUITE DE PRUEBAS DE SEGURIDAD")
    print(f"{'='*60}{Colors.RESET}\n")
    
    print(f"URL Base: {BASE_URL}")
    print(f"WebSocket: {WS_URL}")
    print(f" Directorio: {PROJECT_ROOT}")
    
    # Test de conectividad
    print_test("CONECTIVIDAD")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print_pass(f"Servidor accesible (código: {response.status_code})")
    except Exception as e:
        print_fail(f"No se puede conectar al servidor: {e}")
        print(f"\n{Colors.RED}❌ Asegúrate de que el servidor esté corriendo:{Colors.RESET}")
        print(f"   cd src")
        print(f"   uvicorn app.main:app --reload --port 8088")
        return
    
    # Ejecutar tests
    token = test_jwt_authentication()
    test_security_headers()
    test_input_validation()
    await test_websocket_security(token)
    test_health_endpoint()
    
    # Resumen
    print(f"\n{Colors.BOLD}{'='*60}")
    print(" PRUEBAS COMPLETADAS")
    print(f"{'='*60}{Colors.RESET}\n")
    
    print(f"{Colors.YELLOW}💡 MEJORAS IMPLEMENTADAS:{Colors.RESET}")
    print("    Variable ENVIRONMENT en .env")
    print("    Max tokens actualizado a 2024")
    print("    Logs SQL deshabilitados por defecto")
    print("    Validación anti-jailbreak en queries")
    print("    Rutas absolutas en tests")
    print("    8 tipos de documento en HTML\n")

if __name__ == "__main__":
    try:
        asyncio.run(run_all_tests())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}  Tests interrumpidos por el usuario{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED} Error ejecutando tests: {e}{Colors.RESET}")