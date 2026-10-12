CREATE TABLE client_status(
    id                              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    enumerator                      VARCHAR(50) NOT NULL,
    created_at                      TIMESTAMP NOT NULL DEFAULT(NOW()),
    UNIQUE(enumerator)
);

INSERT INTO client_status (enumerator) VALUES
('active'),
('inactivated');

CREATE TABLE client(
    id                              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    client_key                      CHAR(36) NOT NULL,
    status_id                       INTEGER NOT NULL REFERENCES client_status(id),
    name                            VARCHAR(255) NOT NULL,
    document_number                 CHAR(14) NOT NULL,
    operation                       VARCHAR(50) NOT NULL,
    created_at                      TIMESTAMP NOT NULL DEFAULT(NOW()),
    UNIQUE(client_key)
);

CREATE TABLE client_status_event(
    id                              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    client_id                       BIGINT NOT NULL REFERENCES client(id),
    status_id                       INTEGER NOT NULL REFERENCES client_status(id),
    created_at                      TIMESTAMP NOT NULL DEFAULT(NOW())
);
