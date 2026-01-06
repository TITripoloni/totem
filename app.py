from flask import Flask, request, jsonify
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import logging
import subprocess
import os

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configurações do banco de dados
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'seu_banco'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'sua_senha')
}

def get_db_connection():
    """Estabelece conexão com o banco de dados"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        logger.info("✅ Conexão com banco de dados estabelecida com sucesso")
        return conn
    except Exception as e:
        logger.error(f"❌ Erro ao conectar ao banco de dados: {str(e)}")
        raise

def validate_heartbeat_data(data):
    """Valida os dados recebidos"""
    required_fields = [
        'data_de_criacao', 'event', 'router_identity', 
        'router_serial', 'router_version', 'username',
        'certificado', 'assigned_ip', 'server_local_ip'
    ]
    
    errors = []
    for field in required_fields:
        if field not in data:
            errors.append(f"Campo obrigatório ausente: {field}")
    
    return errors

def trigger_device_check(heartbeat_id, heartbeat_data):
    """Dispara o script device-check.py"""
    try:
        script_path = os.path.join(os.path.dirname(__file__), 'device-check.py')
        
        if not os.path.exists(script_path):
            logger.warning(f"⚠️ Script device-check.py não encontrado em {script_path}")
            return {
                'success': False,
                'message': 'Script device-check.py não encontrado'
            }
        
        # Prepara os dados para passar ao script
        script_input = json.dumps({
            'heartbeat_id': heartbeat_id,
            'data': heartbeat_data
        })
        
        # Executa o script de forma assíncrona
        process = subprocess.Popen(
            ['python', script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=script_input, timeout=30)
        
        if process.returncode == 0:
            logger.info(f"✅ Script device-check.py executado com sucesso para heartbeat ID: {heartbeat_id}")
            return {
                'success': True,
                'message': 'Script executado com sucesso',
                'output': stdout
            }
        else:
            logger.error(f"❌ Erro na execução do script: {stderr}")
            return {
                'success': False,
                'message': f'Erro na execução: {stderr}'
            }
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Timeout na execução do script device-check.py")
        return {
            'success': False,
            'message': 'Timeout na execução do script'
        }
    except Exception as e:
        logger.error(f"❌ Erro ao disparar script device-check.py: {str(e)}")
        return {
            'success': False,
            'message': str(e)
        }

@app.route('/api/devices/heartbeat', methods=['POST'])
def receive_heartbeat():
    """Endpoint para receber heartbeat de dispositivos"""
    start_time = datetime.now()
    log_details = {
        'timestamp': start_time.isoformat(),
        'endpoint': '/api/devices/heartbeat',
        'method': 'POST',
        'status': None,
        'details': {}
    }
    
    try:
        # Validação: verifica se há dados no body
        if not request.is_json:
            log_details['status'] = 'error'
            log_details['details']['error'] = 'Content-Type deve ser application/json'
            logger.error(f"❌ {log_details['details']['error']}")
            return jsonify({
                'success': False,
                'error': 'Content-Type deve ser application/json',
                'log': log_details
            }), 400
        
        data = request.get_json()
        log_details['details']['received_data'] = data
        logger.info(f"📥 Dados recebidos: {json.dumps(data, indent=2)}")
        
        # Validação dos campos obrigatórios
        validation_errors = validate_heartbeat_data(data)
        if validation_errors:
            log_details['status'] = 'validation_error'
            log_details['details']['validation_errors'] = validation_errors
            logger.error(f"❌ Erros de validação: {validation_errors}")
            return jsonify({
                'success': False,
                'errors': validation_errors,
                'log': log_details
            }), 400
        
        # Conexão com banco de dados
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Preparação dos dados para inserção
        insert_query = """
            INSERT INTO heartbeat (
                data_de_criacao, event, router_identity, router_serial,
                router_version, username, certificado, assigned_ip,
                server_local_ip, raw
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, data_de_criacao
        """
        
        raw_json = json.dumps(data)
        
        values = (
            data.get('data_de_criacao'),
            data.get('event'),
            data.get('router_identity'),
            data.get('router_serial'),
            data.get('router_version'),
            data.get('username'),
            data.get('certificado'),
            data.get('assigned_ip'),
            data.get('server_local_ip'),
            raw_json
        )
        
        logger.info("💾 Executando INSERT no banco de dados...")
        cursor.execute(insert_query, values)
        result = cursor.fetchone()
        conn.commit()
        
        heartbeat_id = result['id']
        log_details['details']['inserted_id'] = heartbeat_id
        log_details['details']['inserted_at'] = result['data_de_criacao']
        
        logger.info(f"✅ Heartbeat inserido com sucesso! ID: {heartbeat_id}")
        
        # Disparar gatilho para device-check.py
        logger.info("🔄 Disparando script device-check.py...")
        trigger_result = trigger_device_check(heartbeat_id, data)
        log_details['details']['trigger_result'] = trigger_result
        
        # Fechar conexão
        cursor.close()
        conn.close()
        
        # Log de sucesso final
        log_details['status'] = 'success'
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        log_details['details']['processing_time_seconds'] = processing_time
        
        logger.info(f"✅ Processamento completo em {processing_time:.3f} segundos")
        
        return jsonify({
            'success': True,
            'message': 'Heartbeat armazenado com sucesso',
            'data': {
                'id': heartbeat_id,
                'data_de_criacao': str(result['data_de_criacao']),
                'router_identity': data.get('router_identity'),
                'event': data.get('event')
            },
            'trigger': trigger_result,
            'log': log_details
        }), 201
        
    except psycopg2.Error as e:
        log_details['status'] = 'database_error'
        log_details['details']['error'] = str(e)
        log_details['details']['error_type'] = type(e).__name__
        logger.error(f"❌ Erro no banco de dados: {str(e)}")
        
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        
        return jsonify({
            'success': False,
            'error': 'Erro ao armazenar no banco de dados',
            'details': str(e),
            'log': log_details
        }), 500
        
    except Exception as e:
        log_details['status'] = 'server_error'
        log_details['details']['error'] = str(e)
        log_details['details']['error_type'] = type(e).__name__
        logger.error(f"❌ Erro inesperado: {str(e)}")
        
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'details': str(e),
            'log': log_details
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de verificação de saúde da API"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)