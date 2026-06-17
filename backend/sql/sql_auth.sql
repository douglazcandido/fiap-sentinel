-- Autenticacao (schema public)

DROP TABLE IF EXISTS public.usuarios CASCADE;

CREATE TABLE IF NOT EXISTS public.usuarios (
    id              BIGSERIAL PRIMARY KEY,
    nome            TEXT NOT NULL,
    email           TEXT NOT NULL UNIQUE,
    senha_hash      TEXT NOT NULL,
    ativo           BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em       TIMESTAMP DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_usuarios_email ON public.usuarios (email);
