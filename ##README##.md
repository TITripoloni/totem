# 🚀 API de Heartbeat - Guia Completo de Instalação

## 📋 Índice
1. [Pré-requisitos](#pré-requisitos)
2. [Estrutura do Projeto](#estrutura-do-projeto)
3. [Configuração do Banco de Dados](#configuração-do-banco-de-dados)
4. [Instalação](#instalação)
5. [Configuração](#configuração)
6. [Execução](#execução)
7. [Testando a API](#testando-a-api)
8. [Endpoints Disponíveis](#endpoints-disponíveis)
9. [Logs e Monitoramento](#logs-e-monitoramento)
10. [Solução de Problemas](#solução-de-problemas)

---

## 🔧 Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- **Python 3.8+**
- **PostgreSQL 12+**
- **pip** (gerenciador de pacotes Python)
- **Git** (opcional, para controle de versão)

### Verificando as instalações:

```bash
python --version
psql --version
pip --version
```

---

## 📁 Estrutura do Projeto

Crie a seguinte estrutura de diretórios:

```
heartbeat-api/
│
├── app.py                  # API Flask principal
├── device-check.py         # Script de validação
├── test_api.py            # Script para testar a API
├── requirements.txt       # Dependências Python
├── .env                   # Configurações (não commitar!)
├── .env.example          # Exemplo de configurações
├── device-check.log      # Logs do script (gerado automaticamente)
└── README.md             # Este arquivo
```

---

## 🗄️ Configuração do Banco de Dados

### 1. Criar o Banco de Dados

Conecte-se ao PostgreSQL:

```bash
psql -U postgres
```

Crie o banco de dados:

```sql
CREATE DATABASE heartbeat_db;
\c heartbeat_db
```

### 2. Criar a Tabela

Execute o seguinte comando SQL:

```sql
CREATE TABLE heartbeat (
    id BIGSERIAL PRIMARY KEY,
    data_de_criacao VARCHAR(255),
    event VARCHAR(50),
    router_identity VARCHAR(255),
    router_serial VARCHAR(255),
    router_version VARCHAR(255),
    username VARCHAR(50),
    certificado VARCHAR(255),
    assigned_ip VARCHAR(255),
    server_local_ip VARCHAR(255),
    raw JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar índice para melhor performance
CREATE INDEX idx_router_identity ON heartbeat(router_identity);
CREATE INDEX idx_event ON heartbeat(event);
CREATE INDEX idx_created_at ON heartbeat(created_at);
```

### 3. Verificar a Tabela

```sql
\d heartbeat
SELECT * FROM heartbeat;
```

---

## 📦 Instalação

### 1. Criar Ambiente Virtual (Recomendado)

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# No Windows:
venv\Scripts\activate

# No Linux/Mac:
source venv/bin/activate
```

### 2. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 3. Dar Permissão de Execução aos Scripts

```bash
# Linux/Mac
chmod +x device-check.py
chmod +x test_api.py
```

---

## ⚙️ Configuração

### 1. Criar arquivo .env

Copie o arquivo de exemplo:

```bash
cp .env.example .env
```

### 2. Editar o arquivo .env

Abra o arquivo `.env` e configure suas credenciais:

```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=heartbeat_db
DB_USER=postgres
DB_PASSWORD=sua_senha_aqui
```

**⚠️ IMPORTANTE**: Nunca commite o arquivo `.env` para repositórios públicos!

---

## 🚀 Execução

### 1. Iniciar o Servidor Flask

```bash
python app.py
```

Você deve ver algo como:

```
* Running on http://0.0.0.0:5000
* Restarting with stat
* Debugger is active!
```

### 2. Servidor em Produção (Opcional)

Para produção, use o Gunicorn:

```bash
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 🧪 Testando a API

### Opção 1: Usar o Script de Teste

```bash
python test_api.py
```

### Opção 2: Usar cURL

```bash
curl -X POST http://localhost:5000/api/devices/heartbeat \
  -H "Content-Type: application/json" \
  -d '{
    "data_de_criacao": "2024-01-06T10:30:00",
    "event": "connect",
    "router_identity": "Router-Office-001",
    "router_serial": "SN123456789",
    "router_version": "v2.5.1",
    "username": "admin",
    "certificado": "CERT-ABC-123",
    "assigned_ip": "192.168.1.100",
    "server_local_ip": "10.0.0.1"
  }'
```

### Opção 3: Usar Postman ou Insomnia

1. Crie uma nova requisição POST
2. URL: `http://localhost:5000/api/devices/heartbeat`
3. Headers: `Content-Type: application/json`
4. Body: Use o JSON de exemplo acima

---

## 🔌 Endpoints Disponíveis

### 1. POST /api/devices/heartbeat

Recebe e armazena dados de heartbeat.

**Requisição:**

```json
{
  "data_de_criacao": "2024-01-06T10:30:00",
  "event": "connect",
  "router_identity": "Router-Office-001",
  "router_serial": "SN123456789",
  "router_version": "v2.5.1",
  "username": "admin",
  "certificado": "CERT-ABC-123",
  "assigned_ip": "192.168.1.100",
  "server_local_ip": "10.0.0.1"
}
```

**Resposta de Sucesso (201):**

```json
{
  "success": true,
  "message": "Heartbeat armazenado com sucesso",
  "data": {
    "id": 1,
    "data_de_criacao": "2024-01-06 10:30:00",
    "router_identity": "Router-Office-001",
    "event": "connect"
  },
  "trigger": {
    "success": true,
    "message": "Script executado com sucesso",
    "output": "..."
  },
  "log": {
    "timestamp": "2024-01-06T10:30:05.123456",
    "endpoint": "/api/devices/heartbeat",
    "method": "POST",
    "status": "success",
    "details": {
      "inserted_id": 1,
      "processing_time_seconds": 0.234
    }
  }
}
```

**Resposta de Erro (400/500):**

```json
{
  "success": false,
  "error": "Descrição do erro",
  "details": "Detalhes técnicos",
  "log": {
    "status": "error",
    "details": {...}
  }
}
```

### 2. GET /api/health

Verifica a saúde da API e conexão com o banco.

**Resposta de Sucesso (200):**

```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-01-06T10:30:00"
}
```

---

## 📊 Logs e Monitoramento

### Logs da API

A API utiliza o módulo `logging` do Python e exibe logs no console:

- ✅ Operações bem-sucedidas
- ⚠️ Avisos
- ❌ Erros
- 📥 Dados recebidos
- 💾 Operações no banco

### Logs do device-check.py

O script `device-check.py` gera logs em:

- **Console**: Output em tempo real
- **Arquivo**: `device-check.log`

Exemplo de log:

```
2024-01-06 10:30:00 - __main__ - INFO - 🔍 Iniciando análise do heartbeat ID: 1
2024-01-06 10:30:00 - __main__ - INFO - ✅ Router identity válido: Router-Office-001
2024-01-06 10:30:00 - __main__ - INFO - ✅ Serial do router válido: SN123456789
```

### Monitorar Logs em Tempo Real

```bash
# API
python app.py

# Logs do device-check (em outro terminal)
tail -f device-check.log
```

---

## 🔍 Solução de Problemas

### Problema: "Erro ao conectar ao banco de dados"

**Solução:**

1. Verifique se o PostgreSQL está rodando:
   ```bash
   # Linux
   sudo systemctl status postgresql
   
   # Mac
   brew services list
   ```

2. Verifique as credenciais no arquivo `.env`
3. Teste a conexão manualmente:
   ```bash
   psql -h localhost -U postgres -d heartbeat_db
   ```

### Problema: "Script device-check.py não encontrado"

**Solução:**

1. Verifique se o arquivo existe:
   ```bash
   ls -la device-check.py
   ```

2. Dê permissão de execução:
   ```bash
   chmod +x device-check.py
   ```

3. Verifique o caminho no código (se necessário)

### Problema: "ModuleNotFoundError"

**Solução:**

Reinstale as dependências:

```bash
pip install -r requirements.txt
```

### Problema: "Port 5000 already in use"

**Solução:**

1. Mude a porta no `app.py`:
   ```python
   app.run(host='0.0.0.0', port=5001, debug=True)
   ```

2. Ou mate o processo na porta 5000:
   ```bash
   # Linux/Mac
   lsof -ti:5000 | xargs kill -9
   
   # Windows
   netstat -ano | findstr :5000
   taskkill /PID <PID> /F
   ```

---

## 📝 Notas Importantes

1. **Segurança**: Em produção, use HTTPS e autenticação
2. **Performance**: Configure pool de conexões para alto volume
3. **Backup**: Faça backup regular do banco de dados
4. **Logs**: Configure rotação de logs em produção
5. **Monitoramento**: Use ferramentas como Prometheus/Grafana

---

## 🎯 Próximos Passos

- [ ] Implementar autenticação JWT
- [ ] Adicionar rate limiting
- [ ] Criar dashboard de monitoramento
- [ ] Implementar alertas por email/SMS
- [ ] Adicionar testes unitários
- [ ] Configurar CI/CD

---

## 📞 Suporte

Se encontrar problemas, verifique:

1. Os logs da aplicação
2. Os logs do PostgreSQL
3. O arquivo `device-check.log`
4. As permissões dos arquivos

---

**Desenvolvido com ❤️ usando Flask e PostgreSQL**