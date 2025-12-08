CREATE TABLE known_ids (
    registration_id SERIAL PRIMARY KEY, 
    values BIGINT NOT NULL UNIQUE, 
    description VARCHAR(255) 
);

CREATE TABLE access_attempts (
    log_id SERIAL PRIMARY KEY, 
    time NUMERIC(15, 6) NOT NULL, 
    tag_id BIGINT, 
    tag_text VARCHAR(255), 
    access VARCHAR(50) NOT NULL,
);