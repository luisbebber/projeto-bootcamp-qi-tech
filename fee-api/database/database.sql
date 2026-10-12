

CREATE TABLE client_configuration(
    id                              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    client_key                      CHAR(36) NOT NULL,
    created_at                      TIMESTAMP NOT NULL DEFAULT(NOW()),
    UNIQUE(client_key)
);

CREATE TABLE fee_type(
    id                              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    enumerator                      VARCHAR(50) NOT NULL,
    created_at                      TIMESTAMP NOT NULL DEFAULT(NOW()),
    UNIQUE(enumerator)
);

INSERT INTO fee_type (enumerator) VALUES
('transfer'),
('account_opening');

CREATE TABLE fee_configuration_status(
    id                              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    enumerator                      VARCHAR(50) NOT NULL,
    created_at                      TIMESTAMP NOT NULL DEFAULT(NOW()),
    UNIQUE(enumerator)
);

INSERT INTO fee_configuration_status (enumerator) VALUES
('active'),
('inactive');

CREATE TABLE fee_configuration(
    id                              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    fee_configuration_key           CHAR(36) NOT NULL,
    client_key                      CHAR(36) NOT NULL REFERENCES client_configuration(client_key),
    fee_type_id                     INTEGER NOT NULL REFERENCES fee_type(id),
    amount                          NUMERIC(15,2) NOT NULL CHECK (amount >= 0),
    status_id                       INTEGER NOT NULL REFERENCES fee_configuration_status(id),
    created_at                      TIMESTAMP NOT NULL DEFAULT(NOW()),
    UNIQUE(fee_configuration_key)
);

CREATE TABLE fee_configuration_status_event(
    id                              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    fee_configuration_id            INTEGER NOT NULL REFERENCES fee_configuration(id),
    status_id                       INTEGER NOT NULL REFERENCES fee_configuration_status(id),
    created_at                      TIMESTAMP NOT NULL DEFAULT(NOW())
);

CREATE TABLE charge_status(
    id                              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    enumerator                      VARCHAR(50) NOT NULL,
    created_at                      TIMESTAMP NOT NULL DEFAULT(NOW()),
    UNIQUE(enumerator)
);

INSERT INTO charge_status (enumerator) VALUES
('pending_payment'),
('paid');

CREATE TABLE charge(
    id                              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    charge_key                      CHAR(36) NOT NULL,
    client_key                      CHAR(36) NOT NULL REFERENCES client_configuration(client_key),
    month                           DATE NOT NULL CHECK (EXTRACT(DAY FROM month) = 1),
    amount                          NUMERIC(15,2) NOT NULL CHECK (amount >= 0),
    status_id                       INTEGER NOT NULL REFERENCES charge_status(id),
    created_at                      TIMESTAMP NOT NULL DEFAULT(NOW()),
    UNIQUE(charge_key),
    UNIQUE(client_key, month)
);

CREATE TABLE charge_status_event(
    id                              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    charge_id                       BIGINT NOT NULL REFERENCES charge(id),
    status_id                       INTEGER NOT NULL REFERENCES charge_status(id),
    created_at                      TIMESTAMP NOT NULL DEFAULT(NOW())
);

CREATE TABLE fee(
    id                              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    fee_key                         CHAR(36) NOT NULL,
    client_key                      CHAR(36) NOT NULL REFERENCES client_configuration(client_key),
    fee_type_id                     INTEGER NOT NULL REFERENCES fee_type(id),
    amount                          NUMERIC(15,2) NOT NULL CHECK (amount >= 0),
    charge_id                       BIGINT REFERENCES charge(id),
    idempotency_key                 CHAR(36) NOT NULL,
    created_at                      TIMESTAMP NOT NULL DEFAULT(NOW()),
    UNIQUE(fee_key),
    UNIQUE(idempotency_key)
);
