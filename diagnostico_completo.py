"""
SmartHealth - Diagnóstico Completo del Sistema
===============================================
Ejecutar: python diagnostico_completo.py

Verifica:
1. Base de datos PostgreSQL
2. Extensión pgvector
3. Variables de entorno
4. API FastAPI
5. Conexión OpenAI
"""

import os
import sys
from pathlib import Path

# Agregar el directorio src al path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir / "src"))

# Colores
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.RESET}")

# =============================================================================
# 1. VERIFICAR VARIABLES DE ENTORNO
# =============================================================================

def test_environment_variables():
    print_header("1. VARIABLES DE ENTORNO")
    
    # Cargar .env
    try:
        from dotenv import load_dotenv
        env_path = root_dir / ".env"
        
        if not env_path.exists():
            print_error(f"Archivo .env no encontrado en: {env_path}")
            print_info("Crea el archivo .env en la raíz del proyecto")
            return False
        
        load_dotenv(env_path)
        print_success(f"Archivo .env encontrado: {env_path}")
        
    except ImportError:
        print_error("python-dotenv no está instalado")
        print_info("Instalar con: pip install python-dotenv")
        return False
    
    # Variables requeridas
    required_vars = {
        "DB_HOST": "Host de PostgreSQL",
        "DB_PORT": "Puerto de PostgreSQL",
        "DB_NAME": "Nombre de la base de datos",
        "DB_USER": "Usuario de PostgreSQL",
        "DB_PASSWORD": "Contraseña de PostgreSQL",
        "SECRET_KEY": "Clave secreta para JWT",
        "OPENAI_API_KEY": "API Key de OpenAI"
    }
    
    all_present = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            if var in ["DB_PASSWORD", "SECRET_KEY", "OPENAI_API_KEY"]:
                masked = value[:10] + "..." if len(value) > 10 else "***"
                print_success(f"{var}: {masked}")
            else:
                print_success(f"{var}: {value}")
        else:
            print_error(f"{var}: NO CONFIGURADA - {description}")
            all_present = False
    
    if not all_present:
        print_error("\nFaltan variables de entorno críticas")
        return False
    
    return True

# =============================================================================
# 2. VERIFICAR CONEXIÓN A POSTGRESQL
# =============================================================================

def test_postgresql_connection():
    print_header("2. CONEXIÓN A POSTGRESQL")
    
    try:
        import psycopg2
    except ImportError:
        print_error("psycopg2 no está instalado")
        print_info("Instalar con: pip install psycopg2-binary")
        return False
    
    # Obtener credenciales
    db_config = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "database": os.getenv("DB_NAME", "smarthdb"),
        "user": os.getenv("DB_USER", "sm_admin"),
        "password": os.getenv("DB_PASSWORD", "sm2025")
    }
    
    print_info(f"Intentando conectar a: {db_config['user']}@{db_config['host']}:{db_config['port']}/{db_config['database']}")
    
    try:
        conn = psycopg2.connect(**db_config)
        print_success("Conexión exitosa a PostgreSQL")
        
        # Verificar versión
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print_info(f"Versión: {version.split(',')[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print_error(f"Error de conexión: {e}")
        print_warning("\nPosibles soluciones:")
        print("   1. Verifica que PostgreSQL esté corriendo:")
        print("      - Windows: net start postgresql-x64-16")
        print("      - Linux: sudo systemctl start postgresql")
        print("   2. Verifica las credenciales en .env")
        print("   3. Verifica el puerto (default: 5432)")
        return False
    except Exception as e:
        print_error(f"Error inesperado: {type(e).__name__}: {e}")
        return False

# =============================================================================
# 3. VERIFICAR EXTENSIÓN PGVECTOR
# =============================================================================

def test_pgvector_extension():
    print_header("3. EXTENSIÓN PGVECTOR")
    
    try:
        import psycopg2
        
        db_config = {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": os.getenv("DB_PORT", "5432"),
            "database": os.getenv("DB_NAME", "smarthdb"),
            "user": os.getenv("DB_USER", "sm_admin"),
            "password": os.getenv("DB_PASSWORD", "sm2025")
        }
        
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Verificar extensión
        cursor.execute("""
            SELECT extname, extversion 
            FROM pg_extension 
            WHERE extname = 'vector';
        """)
        
        result = cursor.fetchone()
        
        if result:
            print_success(f"pgvector instalado - Versión: {result[1]}")
            cursor.close()
            conn.close()
            return True
        else:
            print_error("pgvector NO está instalado")
            print_warning("\nInstalar pgvector:")
            print("   1. Asegúrate de tener permisos de SUPERUSER:")
            print("      psql -U postgres -d smarthdb")
            print("      ALTER USER sm_admin WITH SUPERUSER;")
            print("   2. Instala la extensión:")
            print("      CREATE EXTENSION vector;")
            cursor.close()
            conn.close()
            return False
            
    except Exception as e:
        print_error(f"Error verificando pgvector: {e}")
        return False

# =============================================================================
# 4. VERIFICAR ESQUEMA Y TABLAS
# =============================================================================

def test_database_schema():
    print_header("4. ESQUEMA Y TABLAS")
    
    try:
        import psycopg2
        
        db_config = {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": os.getenv("DB_PORT", "5432"),
            "database": os.getenv("DB_NAME", "smarthdb"),
            "user": os.getenv("DB_USER", "sm_admin"),
            "password": os.getenv("DB_PASSWORD", "sm2025")
        }
        
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Verificar esquema smart_health
        cursor.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name = 'smart_health';
        """)
        
        if cursor.fetchone():
            print_success("Esquema 'smart_health' existe")
        else:
            print_error("Esquema 'smart_health' NO existe")
            print_info("Ejecuta los scripts de creación de base de datos")
            cursor.close()
            conn.close()
            return False
        
        # Contar tablas
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'smart_health';
        """)
        
        table_count = cursor.fetchone()[0]
        
        if table_count > 0:
            print_success(f"Encontradas {table_count} tablas en smart_health")
            
            # Listar tablas
            cursor.execute("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'smart_health'
                ORDER BY tablename;
            """)
            
            tables = cursor.fetchall()
            print_info("Tablas existentes:")
            for table in tables:
                print(f"   • {table[0]}")
            
        else:
            print_error("No hay tablas en el esquema smart_health")
            print_info("Ejecuta: python pipelines/02-insert-data/create-tables.py")
            cursor.close()
            conn.close()
            return False
        
        # Verificar datos
        cursor.execute("SELECT COUNT(*) FROM smart_health.patients;")
        patient_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM smart_health.users;")
        user_count = cursor.fetchone()[0]
        
        print_info(f"Registros: {patient_count} pacientes, {user_count} usuarios")
        
        if patient_count == 0:
            print_warning("No hay pacientes en la base de datos")
            print_info("Ejecuta: python pipelines/02-insert-data/script-02.py")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print_error(f"Error verificando esquema: {e}")
        return False

# =============================================================================
# 5. VERIFICAR SQLALCHEMY
# =============================================================================

def test_sqlalchemy_connection():
    print_header("5. CONEXIÓN SQLALCHEMY")
    
    try:
        from app.database.database import SessionLocal, engine
        from sqlalchemy import text
        
        print_info("Probando conexión con SQLAlchemy...")
        
        # Crear sesión
        db = SessionLocal()
        
        # Query de prueba
        result = db.execute(text("SELECT COUNT(*) FROM smart_health.patients;"))
        count = result.scalar()
        
        print_success(f"SQLAlchemy conectado correctamente")
        print_info(f"Pacientes en BD: {count}")
        
        db.close()
        return True
        
    except ImportError as e:
        print_error(f"Error importando módulos: {e}")
        print_info("Verifica que estés en el directorio correcto")
        return False
    except Exception as e:
        print_error(f"Error en SQLAlchemy: {type(e).__name__}: {e}")
        return False

# =============================================================================
# 6. VERIFICAR API FASTAPI
# =============================================================================

def test_fastapi_server():
    print_header("6. SERVIDOR FASTAPI")
    
    try:
        import requests
        
        BASE_URL = "http://localhost:8088"
        
        print_info(f"Verificando servidor en {BASE_URL}...")
        
        # Health check
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            
            if response.status_code == 200:
                print_success("Servidor FastAPI accesible")
                
                data = response.json()
                status = data.get('status')
                
                if status == 'healthy':
                    print_success("Estado del servidor: HEALTHY")
                else:
                    print_warning(f"Estado del servidor: {status}")
                
                # Verificar servicios
                services = data.get('services', {})
                print_info("Estado de servicios:")
                for service, state in services.items():
                    if state in ['connected', 'ready', 'enabled']:
                        print_success(f"  • {service}: {state}")
                    else:
                        print_error(f"  • {service}: {state}")
                
                return True
            else:
                print_error(f"Servidor responde con código: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print_error("No se puede conectar al servidor FastAPI")
            print_warning("\nPara iniciar el servidor:")
            print("   cd src")
            print("   uvicorn app.main:app --reload --port 8088")
            return False
        except requests.exceptions.Timeout:
            print_error("Timeout conectando al servidor (>5s)")
            return False
            
    except ImportError:
        print_error("requests no está instalado")
        print_info("Instalar con: pip install requests")
        return False
    except Exception as e:
        print_error(f"Error verificando FastAPI: {e}")
        return False

# =============================================================================
# 7. VERIFICAR OPENAI
# =============================================================================

def test_openai_connection():
    print_header("7. CONEXIÓN OPENAI")
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print_error("OPENAI_API_KEY no está configurada")
        return False
    
    if api_key.startswith("sk-"):
        print_success("OPENAI_API_KEY tiene formato válido")
    else:
        print_warning("OPENAI_API_KEY tiene formato inusual")
    
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key)
        
        print_info("Verificando conexión con OpenAI...")
        
        # Test simple
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'OK'"}],
            max_tokens=5
        )
        
        if response.choices[0].message.content:
            print_success("Conexión OpenAI exitosa")
            print_info(f"Modelo: {response.model}")
            print_info(f"Tokens usados: {response.usage.total_tokens}")
            return True
        else:
            print_error("Respuesta vacía de OpenAI")
            return False
            
    except ImportError:
        print_error("openai no está instalado")
        print_info("Instalar con: pip install openai")
        return False
    except Exception as e:
        print_error(f"Error conectando a OpenAI: {type(e).__name__}: {e}")
        print_warning("\nVerifica:")
        print("   1. Tu API key es válida")
        print("   2. Tienes créditos disponibles")
        print("   3. Tu conexión a internet funciona")
        return False

# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================

def main():
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  🏥 SMARTHEALTH - DIAGNÓSTICO COMPLETO DEL SISTEMA".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    print(f"{Colors.RESET}\n")
    
    results = {
        "Variables de Entorno": test_environment_variables(),
        "Conexión PostgreSQL": test_postgresql_connection(),
        "Extensión pgvector": test_pgvector_extension(),
        "Esquema y Tablas": test_database_schema(),
        "SQLAlchemy": test_sqlalchemy_connection(),
        "Servidor FastAPI": test_fastapi_server(),
        "OpenAI API": test_openai_connection()
    }
    
    # Resumen
    print_header("RESUMEN DE DIAGNÓSTICO")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, result in results.items():
        if result:
            print_success(f"{test}: OK")
        else:
            print_error(f"{test}: FALLO")
    
    print(f"\n{Colors.BOLD}Resultado: {passed}/{total} tests pasaron{Colors.RESET}\n")
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ ¡SISTEMA COMPLETAMENTE FUNCIONAL!{Colors.RESET}\n")
        print(f"{Colors.CYAN}Siguiente paso:{Colors.RESET}")
        print("   • Abre: http://localhost:8088/docs")
        print("   • O usa: smart_health_chat.html\n")
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ HAY PROBLEMAS QUE RESOLVER{Colors.RESET}\n")
        print(f"{Colors.YELLOW}Revisa los mensajes de error arriba para soluciones específicas{Colors.RESET}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Diagnóstico interrumpido{Colors.RESET}\n")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error fatal: {type(e).__name__}: {e}{Colors.RESET}\n")