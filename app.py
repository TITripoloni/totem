from flask import Flask, request, jsonify
from datetime import datetime
import psycopg
from psycopg.rows import dict_row
import json
import logging
import os
<<<<<<< HEAD
from functools import wraps

# =========================
# CONFIGURAÇÕES
# =========================
=======
import subprocess
import secrets
from functools import wraps

from dotenv import load_dotenv

load_dotenv()  # isso carrega as variáveis do .env

# =========================
# CONFIGURAÇÕES
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
SCRIPT_PATH = os.path.join(BASE_DIR, "device-check.py")

os.makedirs(LOG_DIR, exist_ok=True)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "totem"),
    "user": os.getenv("DB_USER", "totem_api"),
    "password": os.getenv("DB_PASSWORD")
}

# =========================
# LOGGING
# =========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "api.log")),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("TOTEM-API")
>>>>>>> 2392876 (versao 3)

API_TOKEN = os.getenv("API_TOKEN", "TOKEN_FIXO_PARA_SEMPRE")

<<<<<<< HEAD
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'seu_banco'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'sua_senha')
}
=======
# =========================
# BANCO
# =========================
>>>>>>> 2392876 (versao 3)

# =========================
# LOGGING
# =========================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# =========================
# AUTENTICAÇÃO
# =========================

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({'error': 'Token ausente'}), 401

        token = auth_header.replace("Bearer ", "").strip()

        if token != API_TOKEN:
            return jsonify({'error': 'Token inválido'}), 401

        return f(*args, **kwargs)
    return decorated


@app.route('/api/auth', methods=['POST'])
def auth():
    """Retorna o token fixo"""
    return jsonify({
        'token': API_TOKEN,
        'type': 'Bearer'
    })


# =========================
# BANCO DE DADOS
# =========================

def get_db_connection():
<<<<<<< HEAD
    try:
        conn = psycopg.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            dbname=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar no banco: {e}")
        raise


# =========================
# VALIDAÇÃO
# =========================

def validate_heartbeat_data(data):
    required_fields = [
        'event', 'router_identity', 'router_serial',
        'router_version', 'username', 'certificado',
        'assigned_ip', 'server_local_ip'
    ]

    errors = []
    for field in required_fields:
        if field not in data:
            errors.append(f"Campo obrigatório ausente: {field}")

    return errors
=======
    return psycopg.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        dbname=DB_CONFIG["database"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"]
    )

# =========================
# TOKEN FIXO PERSISTENTE
# =========================

def get_or_create_token():
    conn = get_db_connection()
    cur = conn.cursor(row_factory=dict_row)

    cur.execute("SELECT token FROM api_tokens LIMIT 1")
    row = cur.fetchone()

    if row:
        token = row["token"]
        logger.info("Token existente carregado do banco")
    else:
        token = secrets.token_hex(32)
        cur.execute(
            "INSERT INTO api_tokens (token) VALUES (%s)",
            (token,)
        )
        conn.commit()
        logger.info("Token criado e salvo no banco")

    cur.close()
    conn.close()
    return token

API_TOKEN = get_or_create_token()

# =========================
# AUTH DECORATOR
# =========================

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization")

        if not auth or not auth.startswith("Bearer "):
            logger.warning("Token ausente")
            return jsonify({"error": "Token ausente"}), 401

        token = auth.replace("Bearer ", "").strip()

        if token != API_TOKEN:
            logger.warning("Token inválido")
            return jsonify({"error": "Token inválido"}), 401

        return f(*args, **kwargs)
    return decorated

# =========================
# AUTH
# =========================

@app.route("/api/auth", methods=["POST"])
def auth():
    logger.info("Token solicitado")
    return jsonify({
        "token": API_TOKEN,
        "type": "Bearer",
        "persistent": True
    })

# =========================
# DEVICE CHECK
# =========================
>>>>>>> 2392876 (versao 3)


# =========================
# SCRIPT EXTERNO
# =========================

def trigger_device_check(heartbeat_id, heartbeat_data):
<<<<<<< HEAD
    try:
        script_path = os.path.join(os.path.dirname(__file__), 'device-check.py')

        if not os.path.exists(script_path):
            return {'success': False, 'message': 'device-check.py não encontrado'}

        payload = json.dumps({
            'heartbeat_id': heartbeat_id,
            'data': heartbeat_data
=======
    logger.info(f"Iniciando device-check | heartbeat_id={heartbeat_id}")

    if not os.path.exists(SCRIPT_PATH):
        logger.error("device-check.py não encontrado")
        return {
            "success": False,
            "message": "device-check.py não encontrado"
        }

    try:
        payload = json.dumps({
            "heartbeat_id": heartbeat_id,
            "data": heartbeat_data
>>>>>>> 2392876 (versao 3)
        })

        process = subprocess.Popen(
            ["python3", SCRIPT_PATH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = process.communicate(input=payload, timeout=30)

<<<<<<< HEAD
        if process.returncode == 0:
            return {'success': True, 'output': stdout}

        return {'success': False, 'error': stderr}

    except Exception as e:
        return {'success': False, 'error': str(e)}


# =========================
# ENDPOINT HEARTBEAT
# =========================

@app.route('/api/devices/heartbeat', methods=['POST'])
@token_required
def receive_heartbeat():
    try:
        if not request.is_json:
            return jsonify({'error': 'JSON obrigatório'}), 400

        data = request.get_json()

        errors = validate_heartbeat_data(data)
        if errors:
            return jsonify({'errors': errors}), 400

        # 🔹 DATA PADRONIZADA
        data_criacao = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        conn = get_db_connection()
        cursor = conn.cursor(row_factory=dict_row)

        query = """
            INSERT INTO heartbeat (
                data_de_criacao, event, router_identity,
                router_serial, router_version, username,
                certificado, assigned_ip, server_local_ip, raw
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING id
        """

        cursor.execute(query, (
            data_criacao,
            data['event'],
            data['router_identity'],
            data['router_serial'],
            data['router_version'],
            data['username'],
            data['certificado'],
            data['assigned_ip'],
            data['server_local_ip'],
            json.dumps(data)
        ))

        result = cursor.fetchone()
        conn.commit()

        heartbeat_id = result['id']

        trigger = trigger_device_check(heartbeat_id, data)

        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'id': heartbeat_id,
            'data_de_criacao': data_criacao,
            'trigger': trigger
        }), 201

    except Exception as e:
        logger.error(e)
        return jsonify({'error': str(e)}), 500


# =========================
# HEALTH CHECK
# =========================

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    })


# =========================
# START
# =========================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
=======
        logger.info(f"device-check exit_code={process.returncode}")

        if stdout:
            logger.info(f"device-check stdout: {stdout.strip()}")

        if stderr:
            logger.error(f"device-check stderr: {stderr.strip()}")

        if process.returncode != 0:
            return {
                "success": False,
                "exit_code": process.returncode,
                "stderr": stderr.strip()
            }

        return {
            "success": True,
            "stdout": stdout.strip()
        }

    except subprocess.TimeoutExpired:
        logger.error("Timeout device-check")
        return {
            "success": False,
            "message": "Timeout ao executar script"
        }

    except Exception as e:
        logger.exception("Erro device-check")
        return {
            "success": False,
            "error": str(e)
        }

# =========================
# VALIDATION
# =========================

def validate_heartbeat_data(data):
    required = [
        "event", "router_identity", "router_serial",
        "router_version", "username", "certificado",
        "assigned_ip", "server_local_ip"
    ]
    return [f"Campo obrigatório ausente: {f}" for f in required if f not in data]

# =========================
# HEARTBEAT
# =========================

@app.route("/api/devices/heartbeat", methods=["POST"])
@token_required
def heartbeat():
    start_time = datetime.now()

    if not request.is_json:
        return jsonify({"error": "JSON obrigatório"}), 400

    data = request.get_json()
    logger.info(f"Heartbeat recebido: {data}")

    errors = validate_heartbeat_data(data)
    if errors:
        return jsonify({"errors": errors}), 400

    data_criacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db_connection()
    cur = conn.cursor(row_factory=dict_row)

    cur.execute("""
        INSERT INTO heartbeat (
            data_de_criacao, event, router_identity,
            router_serial, router_version, username,
            certificado, assigned_ip, server_local_ip, raw
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        RETURNING id
    """, (
        data_criacao,
        data["event"],
        data["router_identity"],
        data["router_serial"],
        data["router_version"],
        data["username"],
        data["certificado"],
        data["assigned_ip"],
        data["server_local_ip"],
        json.dumps(data)
    ))

    result = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    heartbeat_id = result["id"]

    trigger = trigger_device_check(heartbeat_id, data)

    processing_time = (datetime.now() - start_time).total_seconds()

    logger.info(f"Heartbeat processado | id={heartbeat_id}")

    return jsonify({
        "success": True,
        "message": "Heartbeat armazenado com sucesso",
        "data": {
            "id": heartbeat_id,
            "data_de_criacao": data_criacao,
            "router_identity": data["router_identity"],
            "event": data["event"]
        },
        "trigger": trigger,
        "log": {
            "processing_time_seconds": processing_time
        }
    }), 201

# =========================
# HEALTH
# =========================

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    })

# =========================
# START
# =========================

if __name__ == "__main__":
    logger.info("Iniciando TOTEM API")
    app.run(host="0.0.0.0", port=5000)
>>>>>>> 2392876 (versao 3)
