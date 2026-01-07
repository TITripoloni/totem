#!/bin/bash
echo "🚀 Instalando dependências..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv postgresql

echo "📁 Criando estrutura..."
mkdir -p ~/heartbeat-api
cd ~/heartbeat-api

echo "🐍 Criando ambiente virtual..."
python3 -m venv venv
source venv/bin/activate

echo "📦 Instalando pacotes Python..."
pip install Flask psycopg2-binary python-dotenv

echo "✅ Instalação concluída!"
echo "📝 Próximos passos:"
echo "1. Configure o PostgreSQL"
echo "2. Crie os arquivos .env, app.py, device-check.py"
echo "3. Execute: python3 app.py"
