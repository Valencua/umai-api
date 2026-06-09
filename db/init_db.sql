CREATE TYPE estado_reserva AS ENUM ('pendiente', 'confirmado', 'cancelado');
-- -------------------------------------------------------------
-- Tablas base
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS clientes (
    cliente_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre     VARCHAR NOT NULL,
    email      VARCHAR NOT NULL UNIQUE,
    telefono   VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS usuarios (
    usuario    VARCHAR NOT NULL,
    contraseña VARCHAR NOT NULL,
    admin      BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS platos (
    plato_id    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre      VARCHAR NOT NULL,
    descripcion TEXT NOT NULL,
    precio      INTEGER NOT NULL,
    foto        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS etiquetas (
    etiqueta_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre      VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS plato_etiquetas (
    plato_id    BIGINT NOT NULL,
    etiqueta_id BIGINT NOT NULL,
    CONSTRAINT fk_pe_plato    FOREIGN KEY (plato_id)    REFERENCES platos(plato_id)       ON DELETE CASCADE,
    CONSTRAINT fk_pe_etiqueta FOREIGN KEY (etiqueta_id) REFERENCES etiquetas(etiqueta_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reservas (
    reserva_id        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cliente_id        BIGINT NOT NULL,
    fecha             TIMESTAMPTZ NOT NULL,
    cantidad_personas SMALLINT NOT NULL,
    uuid_codigo       UUID NOT NULL,
    qr_url            TEXT NOT NULL,
    estado            estado_reserva NOT NULL DEFAULT 'pendiente',
    CONSTRAINT fk_reservas_cliente FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reseñas (
    reseña_id   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cliente_id  BIGINT NOT NULL UNIQUE,
    descripcion TEXT NOT NULL,
    estado      BOOLEAN NOT NULL DEFAULT TRUE,
    rating      BIGINT NOT NULL,
    creado_en   TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_resenas_cliente FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS servicios (
    servicio_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre      VARCHAR NOT NULL,
    descripcion TEXT NOT NULL,
    estado      BOOLEAN NOT NULL DEFAULT TRUE,
    icono       TEXT NOT NULL
);

-- -------------------------------------------------------------
-- Datos de prueba
-- -------------------------------------------------------------
INSERT INTO clientes (nombre, email, telefono) VALUES
    ('Ana García',   'ana.garcia@example.com',   '1145678901'),
    ('Bruno López',  'bruno.lopez@example.com',  '1156789012'),
    ('Carla Méndez', 'carla.mendez@example.com', '1167890123')
ON CONFLICT (email) DO NOTHING;

INSERT INTO usuarios (usuario, contraseña, admin) VALUES
    ('admin',   'admin123', TRUE),
    ('mesero1', 'pass123',  FALSE);

INSERT INTO platos (nombre, descripcion, precio, foto) VALUES
    ('Ramen Tonkotsu', 'Caldo de cerdo con fideos y huevo',  8500, 'https://umai.example.com/platos/ramen.jpg'),
    ('Gyoza',          'Empanaditas japonesas (6 unidades)', 4500, 'https://umai.example.com/platos/gyoza.jpg'),
    ('Sushi Roll',     'Roll de salmón y palta (8 piezas)',  7200, 'https://umai.example.com/platos/sushi.jpg');

INSERT INTO etiquetas (nombre) VALUES
    ('Vegetariano'), ('Sin TACC'), ('Picante'), ('Recomendado');

INSERT INTO plato_etiquetas (plato_id, etiqueta_id) VALUES
    (1, 3),
    (1, 4),
    (2, 4),
    (3, 2),
    (3, 4);

INSERT INTO reservas (cliente_id, fecha, cantidad_personas, uuid_codigo, qr_url, estado) VALUES
    (1, '2026-06-15 21:00:00-03', 4, '11111111-1111-1111-1111-111111111111', 'https://umai.example.com/qr/reserva-1.png', 'confirmado'),
    (2, '2026-06-16 20:30:00-03', 2, '22222222-2222-2222-2222-222222222222', 'https://umai.example.com/qr/reserva-2.png', 'pendiente'),
    (3, '2026-06-17 22:00:00-03', 6, '33333333-3333-3333-3333-333333333333', 'https://umai.example.com/qr/reserva-3.png', 'cancelado');

INSERT INTO reseñas (cliente_id, descripcion, estado, rating) VALUES
    (1, 'Excelente atención y comida riquísima', TRUE, 5),
    (2, 'Muy bueno, aunque tardó un poco',       TRUE, 4),
    (3, 'La pasé bien, volvería',                 TRUE, 4);
    
INSERT INTO servicios (nombre, descripcion, estado, icono) VALUES
    ('Delivery', 'Envío a domicilio',                TRUE,  'truck'),
    ('Reservas', 'Reserva de mesas online',          TRUE,  'calendar'),
    ('Eventos',  'Organización de eventos privados', FALSE, 'star');