CREATE TABLE client_configuration(
    id                              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    client_key                      CHAR(36) NOT NULL,
    created_at                      TIMESTAMP NOT NULL DEFAULT(NOW()),
    UNIQUE(client_key)
);

CREATE TABLE account_status(
    id                              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    enumerator                      VARCHAR(50) NOT NULL,
    created_at                      TIMESTAMP NOT NULL DEFAULT(NOW()),
    UNIQUE(enumerator)
);

INSERT INTO account_status (enumerator) VALUES
('active'),
('closed');

CREATE TABLE account(
    id                              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    account_key                     CHAR(36) NOT NULL,
    client_key                      CHAR(36) NOT NULL REFERENCES client_configuration(client_key),
    status_id                       INTEGER NOT NULL REFERENCES account_status(id),
    name                            VARCHAR(255) NOT NULL,
    document_number                 CHAR(11) NOT NULL,
    balance                         NUMERIC(15,2) NOT NULL DEFAULT(0) CHECK (balance >= 0),
    idempotency_key                 CHAR(36) NOT NULL,
    created_at                      TIMESTAMP NOT NULL DEFAULT(NOW()),
    UNIQUE(account_key),
    UNIQUE(idempotency_key)
);

CREATE TABLE account_status_event(
    id                              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    account_id                      BIGINT NOT NULL REFERENCES account(id),
    status_id                       INTEGER NOT NULL REFERENCES account_status(id),
    created_at                      TIMESTAMP NOT NULL DEFAULT(NOW())
);

CREATE TABLE transfer(
    id                              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    transfer_key                    CHAR(36) NOT NULL,
    origin_account_id               BIGINT REFERENCES account(id),
    destination_account_id          BIGINT REFERENCES account(id),
    amount                          NUMERIC(15,2) NOT NULL CHECK (amount > 0),
    idempotency_key                 CHAR(36) NOT NULL,
    created_at                      TIMESTAMP NOT NULL DEFAULT(NOW()),
    CHECK (origin_account_id <> destination_account_id),
    UNIQUE(transfer_key),
    UNIQUE(idempotency_key)
);

CREATE TABLE deposit_status(
    id                              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    enumerator                      VARCHAR(50) NOT NULL,
    created_at                      TIMESTAMP NOT NULL DEFAULT(NOW()),
    UNIQUE(enumerator)
);

INSERT INTO deposit_status (enumerator) VALUES
('pending_fee'),
('completed');

CREATE TABLE deposit(
    id                              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    deposit_key                     CHAR(36) NOT NULL,
    status_id                       INTEGER NOT NULL REFERENCES deposit_status(id),
    account_id                      BIGINT NOT NULL REFERENCES account(id),
    transfer_id                     BIGINT NOT NULL REFERENCES transfer(id),
    amount                          NUMERIC(15,2) NOT NULL CHECK (amount > 0),
    idempotency_key                 CHAR(36) NOT NULL,
    created_at                      TIMESTAMP NOT NULL DEFAULT(NOW()),
    UNIQUE(deposit_key),
    UNIQUE(idempotency_key)
);

CREATE TABLE deposit_status_event(
    id                              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    deposit_id                      BIGINT NOT NULL REFERENCES deposit(id),
    status_id                       INTEGER NOT NULL REFERENCES deposit_status(id),
    created_at                      TIMESTAMP NOT NULL DEFAULT(NOW())
);

CREATE TABLE withdrawal_status(
    id                              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    enumerator                      VARCHAR(50) NOT NULL,
    created_at                      TIMESTAMP NOT NULL DEFAULT(NOW()),
    UNIQUE(enumerator)
);

INSERT INTO withdrawal_status (enumerator) VALUES
('pending_confirmation'),
('pending_fee'),
('completed'),
('reversed');

CREATE TABLE withdrawal(
    id                              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    withdrawal_key                  CHAR(36) NOT NULL,
    status_id                       INTEGER NOT NULL REFERENCES withdrawal_status(id),
    account_id                      BIGINT NOT NULL REFERENCES account(id),
    transfer_id                     BIGINT NOT NULL REFERENCES transfer(id),
    reverse_transfer_id             BIGINT REFERENCES transfer(id),
    amount                          NUMERIC(15,2) NOT NULL CHECK (amount > 0),
    receiver_data                   JSONB NOT NULL,
    idempotency_key                 CHAR(36) NOT NULL,
    created_at                      TIMESTAMP NOT NULL DEFAULT(NOW()),
    UNIQUE(withdrawal_key),
    UNIQUE(idempotency_key)
);

CREATE TABLE withdrawal_status_event(
    id                              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    withdrawal_id                   BIGINT NOT NULL REFERENCES withdrawal(id),
    status_id                       INTEGER NOT NULL REFERENCES withdrawal_status(id),
    created_at                      TIMESTAMP NOT NULL DEFAULT(NOW())
);

CREATE TABLE entry_type(
    id                              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    enumerator                      VARCHAR(50) NOT NULL,
    created_at                      TIMESTAMP NOT NULL DEFAULT(NOW()),
    UNIQUE(enumerator)
);

INSERT INTO entry_type (enumerator) VALUES
('deposit'),
('withdrawal'),
('withdrawal_reversed'),
('transfer_out'),
('transfer_in');

CREATE TABLE entry(
    id                              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    entry_key                       CHAR(36) NOT NULL,
    type_id                         INTEGER NOT NULL REFERENCES entry_type(id),
    account_id                      BIGINT NOT NULL REFERENCES account(id),
    transfer_id                     BIGINT NOT NULL REFERENCES transfer(id),
    amount                          NUMERIC(15,2) NOT NULL,
    balance_after                   NUMERIC(15,2) NOT NULL CHECK (balance_after >= 0),
    created_at                      TIMESTAMP NOT NULL DEFAULT(NOW()),
    UNIQUE(entry_key)
);
