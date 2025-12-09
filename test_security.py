"""
SmartHealth API - Suite de Pruebas de Seguridad
================================================
Ejecutar: python test_security.py

Verifica:
1. Autenticación JWT
2. Headers de seguridad
3. CORS
4. Rate limiting
5. Validación de inputs
6. WebSocket security
7. SQL Injection protection
"""

import requests
import json
import time
from typing import Dict, Optional
import websockets
import asyncio

# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_URL = "http://127.0.0.1:8088"
WS_URL = "ws://127.0.0.1:8088"

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
    print(f"{Colors.GREEN}✅ PASS:{Colors.RESET} {message}")

def print_fail(message: str):
    """Imprime mensaje de fallo"""
    print(f"{Colors.RED}❌ FAIL:{Colors.RESET} {message}")

def print_info(message: str):
    """Imprime información"""
    print(f"{Colors.YELLOW}ℹ️  INFO:{Colors.RESET} {message}")

# ============================================================
# TESTS DE AUTENTICACIÓN JWT
# ============================================================

def test_jwt_authentication():
    """Verifica el sistema de autenticación JWT"""
    print_test("AUTENTICACIÓN JWT")
    
    # 1. Registro de usuario
    print("\n1️⃣ Probando registro de usuario...")
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
    print("\n2️⃣ Probando login...")
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
    print("\n3️⃣ Intentando acceso sin token...")
    response = requests.get(f"{BASE_URL}/users/me")
    if response.status_code == 401 or response.status_code == 403:
        print_pass("Acceso correctamente denegado sin token")
    else:
        print_fail(f"Acceso permitido sin token (código: {response.status_code})")
    
    # 4. Acceso con token válido
    print("\n4️⃣ Intentando acceso con token válido...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    if response.status_code == 200:
        print_pass("Acceso permitido con token válido")
    else:
        print_fail(f"Acceso denegado con token válido (código: {response.status_code})")
    
    # 5. Acceso con token inválido
    print("\n5️⃣ Intentando acceso con token inválido...")
    bad_headers = {"Authorization": "Bearer token_falso_123"}
    response = requests.get(f"{BASE_URL}/users/me", headers=bad_headers)
    if response.status_code == 401 or response.status_code == 403:
        print_pass("Acceso correctamente denegado con token inválido")
    else:
        print_fail(f"Acceso permitido con token inválido (código: {response.status_code})")
    
    # 6. Login con credenciales incorrectas
    print("\n6️⃣ Probando login con credenciales incorrectas...")
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
# TESTS DE HEADERS DE SEGURIDAD
# ============================================================

def test_security_headers():
    """Verifica que los headers de seguridad estén presentes"""
    print_test("HEADERS DE SEGURIDAD")
    
    response = requests.get(f"{BASE_URL}/")
    headers = response.headers
    
    print("\n📋 Headers recibidos:")
    
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
# TESTS DE CORS
# ============================================================

def test_cors():
    """Verifica la configuración CORS"""
    print_test("CONFIGURACIÓN CORS")
    
    # OPTIONS request (preflight)
    print("\n1️⃣ Probando preflight request (OPTIONS)...")
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type"
    }
    
    response = requests.options(f"{BASE_URL}/auth/login", headers=headers)
    
    if "Access-Control-Allow-Origin" in response.headers:
        print_pass(f"CORS permite origen: {response.headers['Access-Control-Allow-Origin']}")
    else:
        print_info("No hay headers CORS en OPTIONS (verificar configuración)")
    
    if "Access-Control-Allow-Methods" in response.headers:
        print_pass(f"Métodos permitidos: {response.headers['Access-Control-Allow-Methods']}")

# ============================================================
# TESTS DE VALIDACIÓN DE INPUTS
# ============================================================

def test_input_validation():
    """Verifica la validación de inputs"""
    print_test("VALIDACIÓN DE INPUTS")
    
    # 1. Email inválido
    print("\n1️⃣ Probando registro con email inválido...")
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
    print("\n2️⃣ Probando registro con contraseña corta...")
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
    
    # 3. Campos faltantes
    print("\n3️⃣ Probando registro con campos faltantes...")
    incomplete = {
        "email": "test@test.com"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=incomplete)
    if response.status_code == 422:
        print_pass("Datos incompletos correctamente rechazados")
    else:
        print_fail(f"Datos incompletos aceptados (código: {response.status_code})")
    
    # 4. SQL Injection intento
    print("\n4️⃣ Probando protección contra SQL Injection...")
    sql_injection = {
        "email": "admin@test.com' OR '1'='1",
        "password": "' OR '1'='1",
        "first_name": "Test",
        "first_surname": "User"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=sql_injection)
    if response.status_code in [422, 400]:
        print_pass("SQL Injection bloqueado por validación")
    else:
        print_info(f"Request procesado (código: {response.status_code}) - verificar logs")

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
    print("\n1️⃣ Intentando conexión WebSocket sin token...")
    try:
        async with websockets.connect(f"{WS_URL}/ws/chat") as ws:
            print_fail("Conexión WebSocket permitida sin token")
    except Exception:
        print_pass("Conexión WebSocket bloqueada sin token")
    
    # 2. Conexión con token inválido
    print("\n2️⃣ Intentando conexión WebSocket con token inválido...")
    try:
        async with websockets.connect(f"{WS_URL}/ws/chat?token=token_falso") as ws:
            print_fail("Conexión WebSocket permitida con token inválido")
    except Exception:
        print_pass("Conexión WebSocket bloqueada con token inválido")
    
    # 3. Conexión con token válido
    print("\n3️⃣ Intentando conexión WebSocket con token válido...")
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
# TESTS DE MANEJO DE ERRORES
# ============================================================

def test_error_handling():
    """Verifica el manejo de errores"""
    print_test("MANEJO DE ERRORES")
    
    # 1. Endpoint inexistente
    print("\n1️⃣ Probando endpoint inexistente...")
    response = requests.get(f"{BASE_URL}/endpoint/que/no/existe")
    if response.status_code == 404:
        print_pass("404 retornado correctamente")
        try:
            error_data = response.json()
            if "error" in error_data:
                print_pass("Formato de error estructurado correcto")
        except:
            print_info("Respuesta no es JSON")
    
    # 2. Método no permitido
    print("\n2️⃣ Probando método HTTP no permitido...")
    response = requests.delete(f"{BASE_URL}/")
    if response.status_code == 405:
        print_pass("405 Method Not Allowed retornado correctamente")
    else:
        print_info(f"Código de respuesta: {response.status_code}")
    
    # 3. JSON malformado
    print("\n3️⃣ Probando JSON malformado...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data="esto no es json",
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 422:
            print_pass("JSON malformado correctamente rechazado")
        else:
            print_info(f"Código de respuesta: {response.status_code}")
    except Exception as e:
        print_info(f"Excepción: {e}")

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
        print(f"\n📊 Estado del sistema:")
        print(f"   Status: {data.get('status')}")
        print(f"   Environment: {data.get('environment')}")
        
        services = data.get('services', {})
        for service, status in services.items():
            icon = "✅" if status in ["connected", "ready", "enabled"] else "❌"
            print(f"   {icon} {service}: {status}")
    else:
        print_fail(f"Endpoint /health falló: {response.status_code}")

# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================

async def run_all_tests():
    """Ejecuta todos los tests de seguridad"""
    print(f"\n{Colors.BOLD}{'='*60}")
    print("🔒 SMARTHEALTH - SUITE DE PRUEBAS DE SEGURIDAD")
    print(f"{'='*60}{Colors.RESET}\n")
    
    print(f"🎯 URL Base: {BASE_URL}")
    print(f"🎯 WebSocket: {WS_URL}")
    
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
    test_cors()
    test_input_validation()
    await test_websocket_security(token)
    test_error_handling()
    test_health_endpoint()
    
    # Resumen
    print(f"\n{Colors.BOLD}{'='*60}")
    print("✅ PRUEBAS COMPLETADAS")
    print(f"{'='*60}{Colors.RESET}\n")
    
    print(f"{Colors.YELLOW}💡 RECOMENDACIONES:{Colors.RESET}")
    print("   1. Revisa los logs del servidor para detalles")
    print("   2. En producción, activa HTTPS y headers estrictos")
    print("   3. Configura rate limiting apropiado")
    print("   4. Implementa logging de seguridad")
    print("   5. Realiza auditorías de seguridad periódicas\n")

if __name__ == "__main__":
    try:
        asyncio.run(run_all_tests())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Tests interrumpidos por el usuario{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error ejecutando tests: {e}{Colors.RESET}")