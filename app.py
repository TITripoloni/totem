from flask import Flask, request, jsonify
from datetime import datetime
import psycopg
from psycopg.rows import dict_row
import json
import logging
import subprocess
import os
from functools import wraps

# =========================
# CONFIGURAÇÕES
# =========================

API_TOKEN = os.getenv("API_TOKEN", "TOKEN_FIXO_PARA_SEMPRE")

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'seu_banco'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'sua_senha')
}

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


# =========================
# SCRIPT EXTERNO
# =========================

def trigger_device_check(heartbeat_id, heartbeat_data):
    try:
        script_path = os.path.join(os.path.dirname(__file__), 'device-check.py')

        if not os.path.exists(script_path):
            return {'success': False, 'message': 'device-check.py não encontrado'}

        payload = json.dumps({
            'heartbeat_id': heartbeat_id,
            'data': heartbeat_data
        })

        process = subprocess.Popen(
            ['python', script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = process.communicate(input=payload, timeout=30)

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
