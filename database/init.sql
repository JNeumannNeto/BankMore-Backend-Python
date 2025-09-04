CREATE TABLE IF NOT EXISTS contacorrente (
	id TEXT(37) PRIMARY KEY,
	numero TEXT(10) NOT NULL UNIQUE,
	nome TEXT(100) NOT NULL,
	cpf TEXT(11) NOT NULL UNIQUE,
	ativo INTEGER(1) NOT NULL default 1,
	senha TEXT(100) NOT NULL,
	salt TEXT(100) NOT NULL,
	created_at TEXT(25) NOT NULL,
	updated_at TEXT(25) NOT NULL,
	CHECK (ativo in (0,1))
);

CREATE TABLE IF NOT EXISTS movimento (
	id TEXT(37) PRIMARY KEY,
	account_id TEXT(37) NOT NULL,
	datamovimento TEXT(25) NOT NULL,
	tipomovimento TEXT(1) NOT NULL,
	valor REAL NOT NULL,
	description TEXT(255),
	idempotency_key TEXT(37),
	created_at TEXT(25) NOT NULL,
	updated_at TEXT(25) NOT NULL,
	CHECK (tipomovimento in ('C','D')),
	FOREIGN KEY(account_id) REFERENCES contacorrente(id)
);

CREATE TABLE IF NOT EXISTS tarifa (
	id TEXT(37) PRIMARY KEY,
	account_id TEXT(37) NOT NULL,
	datamovimento TEXT(25) NOT NULL,
	valor REAL NOT NULL,
	type TEXT(50) NOT NULL DEFAULT 'TRANSFER',
	description TEXT(255) NOT NULL,
	request_id TEXT(255),
	created_at TEXT(25) NOT NULL,
	updated_at TEXT(25) NOT NULL,
	FOREIGN KEY(account_id) REFERENCES contacorrente(id)
);

CREATE TABLE IF NOT EXISTS transferencia (
	id TEXT(37) PRIMARY KEY,
	origin_account_id TEXT(37) NOT NULL,
	destination_account_id TEXT(37) NOT NULL,
	datamovimento TEXT(25) NOT NULL,
	valor REAL NOT NULL,
	status INTEGER(1) NOT NULL DEFAULT 0,
	description TEXT(255),
	data_conclusao TEXT(25),
	idempotency_key TEXT(37),
	created_at TEXT(25) NOT NULL,
	updated_at TEXT(25) NOT NULL,
	CHECK (status in (0,1,2)),
	FOREIGN KEY(origin_account_id) REFERENCES contacorrente(id),
	FOREIGN KEY(destination_account_id) REFERENCES contacorrente(id)
);

CREATE TABLE IF NOT EXISTS idempotencia (
	id TEXT(37) PRIMARY KEY,
	chave_idempotencia TEXT(37) NOT NULL UNIQUE,
	requisicao TEXT(1000),
	resultado TEXT(1000),
	status TEXT(20) DEFAULT 'PENDING',
	created_at TEXT(25) NOT NULL,
	updated_at TEXT(25) NOT NULL
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_movimento_conta ON movimento(account_id);
CREATE INDEX IF NOT EXISTS idx_movimento_created ON movimento(created_at);
CREATE INDEX IF NOT EXISTS idx_movimento_idempotency ON movimento(idempotency_key);

CREATE INDEX IF NOT EXISTS idx_transferencia_origem ON transferencia(origin_account_id);
CREATE INDEX IF NOT EXISTS idx_transferencia_destino ON transferencia(destination_account_id);
CREATE INDEX IF NOT EXISTS idx_transferencia_created ON transferencia(created_at);
CREATE INDEX IF NOT EXISTS idx_transferencia_idempotency ON transferencia(idempotency_key);
CREATE INDEX IF NOT EXISTS idx_transferencia_status ON transferencia(status);

CREATE INDEX IF NOT EXISTS idx_tarifa_conta ON tarifa(account_id);
CREATE INDEX IF NOT EXISTS idx_tarifa_created ON tarifa(created_at);
CREATE INDEX IF NOT EXISTS idx_tarifa_request ON tarifa(request_id);
CREATE INDEX IF NOT EXISTS idx_tarifa_type ON tarifa(type);

CREATE INDEX IF NOT EXISTS idx_contacorrente_numero ON contacorrente(numero);
CREATE INDEX IF NOT EXISTS idx_contacorrente_cpf ON contacorrente(cpf);

CREATE INDEX IF NOT EXISTS idx_idempotencia_chave ON idempotencia(chave_idempotencia);
