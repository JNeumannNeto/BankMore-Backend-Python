# Instruções de Execução - BankMore Backend Python

## Pré-requisitos

- Python 3.11+
- Docker e Docker Compose
- Git

## Execução Local (Desenvolvimento)

### 1. Clonar o repositório
```bash
git clone <repository-url>
cd BankMore-Backend-Python
```

### 2. Configurar ambiente virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente
```bash
cp .env.example .env
# Edite o arquivo .env conforme necessário
```

### 5. Executar migrações
```bash
python manage.py migrate
```

### 6. Executar os serviços individualmente

#### Terminal 1 - Account API
```bash
python manage.py runserver 8001
```

#### Terminal 2 - Transfer API
```bash
python manage.py runserver 8002
```

#### Terminal 3 - Fee API
```bash
python manage.py runserver 8003
```

#### Terminal 4 - Fee Consumer (Kafka)
```bash
python manage.py consume_transfer_events
```

### 7. Acessar as APIs
- Account API: http://localhost:8001/swagger/
- Transfer API: http://localhost:8002/swagger/
- Fee API: http://localhost:8003/swagger/

## Execução com Docker Compose (Recomendado)

### 1. Executar todos os serviços
```bash
docker-compose up --build
```

### 2. Aguardar inicialização
Aguarde todos os serviços subirem. Os logs mostrarão quando estiverem prontos.

### 3. Acessar as APIs
- Account API: http://localhost:8001/swagger/
- Transfer API: http://localhost:8002/swagger/
- Fee API: http://localhost:8003/swagger/

### 4. Parar os serviços
```bash
docker-compose down
```

## Testando as APIs

### 1. Criar uma conta
```bash
curl -X POST http://localhost:8001/api/account/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "cpf": "12345678901",
    "name": "João Silva",
    "password": "senha123"
  }'
```

### 2. Fazer login
```bash
curl -X POST http://localhost:8001/api/account/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "cpf": "12345678901",
    "password": "senha123"
  }'
```

### 3. Fazer uma movimentação (usar o token do login)
```bash
curl -X POST http://localhost:8001/api/account/movement/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -d '{
    "request_id": "unique-id-123",
    "account_number": "NUMERO_DA_CONTA",
    "amount": 100.00,
    "type": "C"
  }'
```

### 4. Consultar saldo
```bash
curl -X GET http://localhost:8001/api/account/balance/ \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### 5. Fazer uma transferência
```bash
curl -X POST http://localhost:8002/api/transfer/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -d '{
    "request_id": "transfer-id-123",
    "destination_account_number": "CONTA_DESTINO",
    "amount": 50.00
  }'
```

## Estrutura dos Serviços

### Account API (Porta 8001)
- Cadastro de contas
- Autenticação (JWT)
- Movimentações (depósitos/saques)
- Consulta de saldo

### Transfer API (Porta 8002)
- Transferências entre contas
- Validações de saldo
- Comunicação com Account API
- Publicação de eventos no Kafka

### Fee API (Porta 8003)
- Consulta de tarifas
- Processamento automático de tarifas
- Consumo de eventos do Kafka

## Monitoramento

### Logs
Os logs são salvos na pasta `logs/` e também exibidos no console.

### Kafka
- Zookeeper: localhost:2181
- Kafka: localhost:9092

### Redis
- Redis: localhost:6379

### Banco de Dados
- SQLite: `database/bankmore.db`

## Troubleshooting

### Erro de conexão com Kafka
Aguarde o Kafka inicializar completamente antes de executar os serviços.

### Erro de migração
Execute `python manage.py migrate` antes de iniciar os serviços.

### Porta já em uso
Verifique se as portas 8001, 8002, 8003 estão livres.

### Problemas com Docker
```bash
docker-compose down -v
docker-compose up --build
```

## Desenvolvimento

### Executar testes
```bash
python manage.py test
```

### Criar migrações
```bash
python manage.py makemigrations
```

### Acessar shell Django
```bash
python manage.py shell
```

## Produção

Para produção, configure adequadamente:
- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS`
- Banco de dados PostgreSQL
- Redis externo
- Kafka cluster
