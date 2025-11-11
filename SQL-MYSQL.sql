--Sentencias sql usadas dentro de Clever Cloud :)
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE
);


-- Insertar usuarios de prueba
INSERT INTO usuarios (username, email, password_hash, activo)
VALUES
('admin', 'admin@example.com',
 '$2b$12$7TOcFI9p4lO3TqI1E3A3UuN9C3QqUuAkFvF5YI9Z2pJf8k4Cq2v7e', TRUE),
('juan', 'juan@example.com',
 '$2b$12$e3ZVQ4G2pjz6Z4K9Qn1M1OqL4S3XzK0C3w5uQ8dH7jJk8lPq2t6nW', TRUE),
('maria', 'maria@example.com',
 '$2b$12$K1h3A9N6dF4rE8sL2pQzDeY7Xw9Vb3C5nR2tU8yH1jK4lM6pO2aC', TRUE);