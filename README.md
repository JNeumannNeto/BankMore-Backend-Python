# BankMore - Sistema Bancário com Microserviços (Python Django)

Sistema bancário completo implementado com arquitetura de microserviços usando Django REST Framework, seguindo os padrões DDD (Domain-Driven Design) e CQRS (Command Query Responsibility Segregation).

## 🏗️ Arquitetura

```
BankMore - Sistema Bancário (Python Django)
│
├── 📁 bankmore_project/          # Projeto Django principal
│   ├── settings/                 # Configurações por ambiente
│   ├── urls.py                   # URLs principais
│   └── wsgi.py                   # WSGI application
│
├── 📁 shared/                    # Biblioteca compartilhada
│   ├── models/                   # Modelos compartilhados
│   ├── services/                 # Serviços compartilhados (JWT)
│   ├── utils/                    # Utilitários (CPF, Hash)
│   └── middleware/               # Middleware personalizado
│
├── 🏦 account_api/               # API de Contas (Porta 8001)
│   ├── models.py                 # Modelos de domínio
│   ├── views.py                  # ViewSets REST
│   ├── serializers.py            # Serializers DRF
│   ├── services.py               # Serviços de aplicação
│   └── urls.py                   # URLs da API
│
├── 💸 transfer_api/              # API de Transferências (Porta 8002)
│   ├── models.py                 # Modelos de domínio
│   ├── views.py                  # ViewSets REST
│   ├── serializers.py            # Serializers DRF
│   ├── services.py               # Serviços de aplicação
│   └── urls.py                   # URLs da API
│
├── 💰 fee_api/                   # API de Tarifas (Porta 8003)
│   ├── models.py                 # Modelos de domínio
│   ├── views.py                  # ViewSets REST
│   ├── serializers.py            # Serializers DRF
│   ├── services.py               # Serviços de aplicação
│   └── urls.py                   # URLs da API
│
├── 🧪 tests/
│   ├── test_account_api/         # Testes da API de contas
│   ├── test_transfer_api/        # Testes da API de transferências
│   └── test_fee_api/             # Testes da API de tarifas
│
├── 🗄️ database/
│   └── init.sql                  # Script de inicialização do banco
│
├── 🐳 docker-compose.yml         # Orquestração dos serviços
├── 📋 manage.py                  # Django management
└── 📖 README.md                  # Documentação
```

### Fluxo de Comunicação:
```
[Cliente] 
    ↓ HTTP/JWT
[Account API] ←→ [SQLite Database]
    ↓ Kafka (Transfer Events)
[Transfer API] ←→ [SQLite Database]
    ↓ Kafka (Fee Events)
[Fee API] ←→ [SQLite Database]
```

O sistema é composto por 3 microserviços principais:

### 1. **Account API** (Porta 8001)
- Cadastro e autenticação de usuários
- Movimentações na conta corrente (depósitos e saques)
- Consulta de saldo
- Inativação de contas

### 2. **Transfer API** (Porta 8002)
- Transferências entre contas da mesma instituição
- Processamento de transferências com validações
- Comunicação assíncrona via Kafka

### 3. **Fee API** (Porta 8003)
- Processamento de tarifas de transferência
- Consumo de mensagens Kafka
- Cobrança automática de tarifas

## 🛠️ Tecnologias Utilizadas

- **Python 3.11+**: Linguagem principal
- **Django 4.2**: Framework web
- **Django REST Framework**: APIs REST
- **SQLite**: Banco de dados
- **JWT**: Autenticação e autorização
- **Kafka**: Mensageria assíncrona
- **Celery**: Processamento assíncrono
- **Redis**: Cache e broker do Celery
- **Docker**: Containerização
- **Swagger**: Documentação das APIs

## 🔧 Funcionalidades Implementadas

### Requisitos Funcionais ✅
- [x] Cadastro e autenticação de usuários
- [x] Realização de movimentações (depósitos e saques)
- [x] Transferências entre contas
- [x] Consulta de saldo
- [x] Sistema de tarifas

### Requisitos Técnicos ✅
- [x] **DDD**: Estrutura de domínio bem definida
- [x] **CQRS**: Separação de comandos e consultas
- [x] **JWT**: Autenticação em todos os endpoints
- [x] **Idempotência**: Prevenção de operações duplicadas
- [x] **Kafka**: Comunicação assíncrona
- [x] **Cache**: Implementado com Redis
- [x] **Validações**: CPF, senhas, valores, etc.
- [x] **Docker**: Containerização completa

### Diferenciais Implementados ✅
- [x] **Microserviços**: Arquitetura distribuída
- [x] **Cache**: Otimização de consultas
- [x] **Kafka**: Comunicação assíncrona
- [x] **Testes**: Estrutura preparada para testes
- [x] **Swagger**: Documentação completa

## 🚀 Como Executar

### Pré-requisitos
- Python 3.11+
- Docker e Docker Compose instalados

### Instalação Local

1. **Clone o repositório**
```bash
git clone <repository-url>
cd BankMore-Backend-Python
```

2. **Crie e ative o ambiente virtual**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Execute as migrações**
```bash
python manage.py migrate
```

5. **Execute os serviços**
```bash
# Account API
python manage.py runserver 8001

# Transfer API (em outro terminal)
python manage.py runserver 8002 --settings=bankmore_project.settings.transfer

# Fee API (em outro terminal)
python manage.py runserver 8003 --settings=bankmore_project.settings.fee
```

### Executando com Docker Compose

1. **Execute o sistema completo**
```bash
docker-compose up --build
```

2. **Aguarde a inicialização**
- Kafka: http://localhost:9092
- Account API: http://localhost:8001
- Transfer API: http://localhost:8002
- Fee API: http://localhost:8003

### Acessando as APIs

- **Account API Swagger**: http://localhost:8001/swagger/
- **Transfer API Swagger**: http://localhost:8002/swagger/
- **Fee API Swagger**: http://localhost:8003/swagger/

## 📋 Endpoints Principais

### Account API

#### POST `/api/account/register/`
Cadastra uma nova conta corrente
```json
{
  "cpf": "12345678901",
  "name": "João Silva",
  "password": "senha123"
}
```

#### POST `/api/account/login/`
Realiza login e retorna JWT token
```json
{
  "cpf": "12345678901",
  "password": "senha123"
}
```

#### POST `/api/account/movement/`
Realiza movimentação na conta (requer autenticação)
```json
{
  "request_id": "uuid-unique",
  "account_number": "123456",
  "amount": 100.00,
  "type": "C"
}
```

#### GET `/api/account/balance/`
Consulta saldo da conta (requer autenticação)

### Transfer API

#### POST `/api/transfer/`
Realiza transferência entre contas (requer autenticação)
```json
{
  "request_id": "uuid-unique",
  "destination_account_number": "654321",
  "amount": 50.00
}
```

### Fee API

#### GET `/api/fee/{account_number}/`
Consulta tarifas por número da conta

#### GET `/api/fee/detail/{id}/`
Consulta tarifa específica por ID

## 🗄️ Estrutura do Banco de Dados

### Modelos Principais

- **Account**: Dados das contas
- **Movement**: Movimentações financeiras
- **Transfer**: Histórico de transferências
- **Fee**: Registro de tarifas cobradas
- **IdempotencyKey**: Controle de idempotência

## 🔒 Segurança

### Autenticação JWT
- Todos os endpoints protegidos requerem token JWT
- Token contém informações da conta logada
- Validação de expiração e assinatura

### Validações Implementadas
- **CPF**: Validação completa com dígitos verificadores
- **Senhas**: Hash com salt único por usuário
- **Valores**: Apenas valores positivos
- **Contas**: Verificação de existência e status ativo

## 🔄 Fluxo de Transferência

1. **Validações iniciais** (conta origem, destino, valor)
2. **Verificação de saldo** na conta origem
3. **Débito na conta origem** via Account API
4. **Crédito na conta destino** via Account API
5. **Registro da transferência** no banco de dados
6. **Publicação no Kafka** para cobrança de tarifa
7. **Fee API**: Processa tarifa e debita automaticamente

## 📊 Monitoramento e Logs

- Logs estruturados em todos os serviços
- Rastreamento de operações via request_id
- Métricas de performance disponíveis

## 🧪 Testes

### Executando Testes
```bash
python manage.py test
```

## 🐳 Docker

### Serviços no Docker Compose
- **zookeeper**: Coordenação do Kafka
- **kafka**: Broker de mensagens
- **redis**: Cache e broker do Celery
- **sqlite-db**: Banco de dados compartilhado
- **account-api**: API de contas
- **transfer-api**: API de transferências
- **fee-api**: API de tarifas

## 🔧 Configurações

### Variáveis de Ambiente
- `DATABASE_URL`: URL do banco de dados
- `KAFKA_BOOTSTRAP_SERVERS`: Servidores Kafka
- `JWT_SECRET_KEY`: Chave secreta JWT
- `REDIS_URL`: URL do Redis
- `TRANSFER_FEE_AMOUNT`: Valor da tarifa

## 📈 Escalabilidade

### Preparado para Kubernetes
- Dockerfiles otimizados
- Configurações externalizadas
- Health checks implementados
- Múltiplas réplicas suportadas

### Cache e Performance
- Cache Redis para consultas frequentes
- Índices otimizados no banco
- Conexões de banco eficientes

## 🚨 Tratamento de Erros

### Códigos de Erro Padronizados
- `INVALID_DOCUMENT`: CPF inválido
- `USER_UNAUTHORIZED`: Credenciais inválidas
- `INVALID_ACCOUNT`: Conta não encontrada
- `INACTIVE_ACCOUNT`: Conta inativa
- `INVALID_VALUE`: Valor inválido
- `INVALID_TYPE`: Tipo de operação inválido

### Respostas HTTP Consistentes
- 200: Sucesso
- 201: Criado com sucesso
- 204: Sucesso sem conteúdo
- 400: Dados inválidos
- 401: Não autorizado
- 403: Token inválido/expirado

## 📝 Próximos Passos

### Melhorias Futuras
- [ ] Testes de carga
- [ ] Métricas com Prometheus
- [ ] Logs centralizados (ELK Stack)
- [ ] Circuit Breaker
- [ ] Rate Limiting
- [ ] Criptografia de dados sensíveis

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

---

**Desenvolvido com ❤️ seguindo as melhores práticas de arquitetura de software**
