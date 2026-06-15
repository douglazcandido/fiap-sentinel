-- Cópia do XLSX de origem, sem transformacao.

CREATE SCHEMA IF NOT EXISTS bronze;

CREATE TABLE IF NOT EXISTS bronze.incidentes (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numero                  TEXT,
    prioridade              TEXT,
    produto                 TEXT,
    categoria               TEXT,
    subcategoria            TEXT,
    grupo_designado         TEXT,
    item_configuracao       TEXT,
    aberto                  TEXT,
    resolvido               TEXT,
    encerrado               TEXT,
    duracao                 TEXT,
    codigo_fechamento       TEXT,
    descricao_resumida      TEXT,
    solucao                 TEXT,
    aberto_por              TEXT,
    incidente_pai           TEXT,
    status                  TEXT,
    entrou_kpi              TEXT,
    kpi_violado             TEXT,
    carga_origem            TEXT DEFAULT 'LW-DATASET.xlsx',
    carga_em                TIMESTAMP DEFAULT now()
);