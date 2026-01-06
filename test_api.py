#!/usr/bin/env python3
"""
Script para testar a API de heartbeat
"""

import requests
import json
from datetime import datetime

# URL da API (ajuste conforme necessário)
API_URL = "http://localhost:5000/api/devices/heartbeat"

# Dados de exemplo para o heartbeat
heartbeat_data = {
    "data_de_criacao": datetime.now().isoformat(),
    "event": "connect",
    "router_identity": "Router-Office-001",
    "router_serial": "SN123456789",
    "router_version": "v2.5.1",
    "username": "admin",
    "certificado": "CERT-ABC-123-XYZ",
    "assigned_ip": "192.168.1.100",
    "server_local_ip": "10.0.0.1"
}

def test_heartbeat():
    """Testa o endpoint de heartbeat"""
    print("=" * 80)
    print("🧪 TESTANDO API DE HEARTBEAT")
    print("=" * 80)
    print(f"\n📤 Enviando dados para: {API_URL}")
    print(f"\n📋 Payload:")
    print(json.dumps(heartbeat_data, indent=2))
    print("\n" + "-" * 80)
    
    try:
        response = requests.post(
            API_URL,
            json=heartbeat_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"\n📥 Resposta recebida!")
        print(f"Status Code: {response.status_code}")
        print(f"\n📄 Resposta completa:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
        if response.status_code == 201:
            print("\n✅ TESTE PASSOU! Heartbeat armazenado com sucesso!")
        else:
            print(f"\n❌ TESTE FALHOU! Status code: {response.status_code}")
        
        print("\n" + "=" * 80)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERRO: Não foi possível conectar à API.")
        print("Verifique se o servidor Flask está rodando em http://localhost:5000")
    except requests.exceptions.Timeout:
        print("\n❌ ERRO: Timeout ao conectar à API")
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {str(e)}")

def test_health():
    """Testa o endpoint de health check"""
    print("\n" + "=" * 80)
    print("🏥 TESTANDO HEALTH CHECK")
    print("=" * 80)
    
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        print(f"\nStatus: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            print("\n✅ API está saudável!")
        else:
            print("\n⚠️ API pode estar com problemas")
            
    except Exception as e:
        print(f"\n❌ Erro no health check: {str(e)}")

if __name__ == "__main__":
    # Testa health check primeiro
    test_health()
    
    # Aguarda um momento
    print("\n⏳ Aguardando 2 segundos...\n")
    import time
    time.sleep(2)
    
    # Testa o endpoint principal
    test_heartbeat()