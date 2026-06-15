-- Dados limpos, tipados e enriquecidos com campos derivados.
-- Input para os modelos de ML e para calculos de KPI/Gold.
-- =========================================================

CREATE SCHEMA IF NOT EXISTS silver;

CREATE TABLE IF NOT EXISTS silver.incidentes (

    -- --------------------------------------------------
    -- chave e rastreabilidade
    -- --------------------------------------------------
    numero                      TEXT PRIMARY KEY,
    bronze_id                   UUID NOT NULL,          -- referencia ao registro de origem no Bronze

    -- --------------------------------------------------
    -- prioridade (split de "3 - Media" em codigo + label)
    -- --------------------------------------------------
    prioridade_codigo           SMALLINT NOT NULL,      -- 1, 2, 3, 4, 5
    prioridade_label            TEXT NOT NULL,          -- Critica, Alta, Media, Baixa, Muito Baixa

    -- --------------------------------------------------
    -- classificacao do incidente
    -- --------------------------------------------------
    grupo_designado             TEXT NOT NULL,
    produto                     TEXT,                   -- 63% nulo, mantido como NULL
    categoria                   TEXT,
    subcategoria                TEXT,
    item_configuracao           TEXT,                   -- 1.45% nulo, bem preenchido
    solucao                     TEXT,                   -- Contorno, Definitiva ou NULL

    -- --------------------------------------------------
    -- datas e duracao
    -- --------------------------------------------------
    aberto_em                   TIMESTAMP NOT NULL,
    encerrado_em                TIMESTAMP NOT NULL,
    resolvido_em                TIMESTAMP,              -- 67% nulo, opcional por design
    duracao_segundos            INTEGER NOT NULL,       -- duracao bruta (Encerrado - Aberto)
    duracao_segundos_capped     INTEGER NOT NULL,       -- duracao com capping em 72h (259200s) para ML

    -- --------------------------------------------------
    -- campos derivados de abertura (features temporais)
    -- --------------------------------------------------
    abertura_data               DATE NOT NULL,
    abertura_hora               SMALLINT NOT NULL,      -- 0-23
    abertura_dia_semana         SMALLINT NOT NULL,      -- 0=Segunda ... 6=Domingo
    abertura_mes                SMALLINT NOT NULL,      -- 1-12
    abertura_ano                SMALLINT NOT NULL,      -- 2023, 2024, 2025
    abertura_fim_de_semana      BOOLEAN NOT NULL,       -- dia_semana IN (5, 6)
    abertura_fora_horario       BOOLEAN NOT NULL,       -- hora < 8 OR hora >= 18

    -- --------------------------------------------------
    -- campos derivados de origem e comportamento
    -- --------------------------------------------------
    aberto_automaticamente      BOOLEAN NOT NULL,       -- aberto_por = 'Monitoramento'
    tem_incidente_pai           BOOLEAN NOT NULL,       -- incidente_pai IS NOT NULL
    incidente_pai               TEXT,                   -- numero do incidente pai, se houver
    status                      TEXT NOT NULL,          -- valor original normalizado
    sem_intervencao             BOOLEAN NOT NULL,       -- status = 'Sem Intervencao'
    aberto_por                  TEXT NOT NULL,          -- Manual ou Monitoramento

    -- --------------------------------------------------
    -- KPI e OLA
    -- --------------------------------------------------
    entrou_kpi                  BOOLEAN NOT NULL,       -- fonte de verdade da base
    kpi_violado                 BOOLEAN,                -- NULL se entrou_kpi = false
    prazo_ola_horas             SMALLINT,               -- 4 para P1/P2, 12 para P3, NULL para P4/P5
    elegivel_kpi                BOOLEAN NOT NULL,       -- prioridade IN (1,2,3) AND sem_intervencao = false AND tem_incidente_pai = false

    -- --------------------------------------------------
    -- controle de carga
    -- --------------------------------------------------
    processado_em               TIMESTAMP DEFAULT now()
);

-- --------------------------------------------------
-- indices para suporte a queries analiticas e ML
-- --------------------------------------------------

-- serie temporal (Prophet, volume por dia)
CREATE INDEX IF NOT EXISTS idx_silver_abertura_data
    ON silver.incidentes (abertura_data);

-- filtros de KPI (frente 03)
CREATE INDEX IF NOT EXISTS idx_silver_kpi
    ON silver.incidentes (entrou_kpi, kpi_violado);

-- filtros por prioridade (RF, agregacoes)
CREATE INDEX IF NOT EXISTS idx_silver_prioridade
    ON silver.incidentes (prioridade_codigo);

-- filtros por equipe (K-Means, frente 02, recomendacoes)
CREATE INDEX IF NOT EXISTS idx_silver_grupo
    ON silver.incidentes (grupo_designado);

-- filtros compostos mais comuns nas queries de KPI
CREATE INDEX IF NOT EXISTS idx_silver_kpi_prioridade_data
    ON silver.incidentes (entrou_kpi, prioridade_codigo, abertura_data);

-- rastreabilidade Bronze -> Silver
CREATE INDEX IF NOT EXISTS idx_silver_bronze_id
    ON silver.incidentes (bronze_id);