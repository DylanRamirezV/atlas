CREATE TABLE IF NOT EXISTS usuarios (
  numero_identificacion VARCHAR(50) PRIMARY KEY,
  clave VARCHAR(255) NOT NULL
);

INSERT INTO usuarios (numero_identificacion, clave)
VALUES ('TU_IDENTIFICACION', 'TU_CONTRASENA')
ON CONFLICT (numero_identificacion)
DO UPDATE SET clave = EXCLUDED.clave;
