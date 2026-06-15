import pandas as pd
from sqlalchemy import create_engine, text

from app.core.config import DATABASE_URL
from app.core.logger import setup_logger


logger = setup_logger(__name__)

SOURCE_SCHEMA = 'bronze'
SOURCE_TABLE  = 'incidentes'
TARGET_SCHEMA = 'silver'
TARGET_TABLE  = 'fato_incidentes'

PRIORIDADE_MAP = {
    '1 - Crítica': (1, 'Critica'),
    '2 - Alta': (2, 'Alta'),
    '3 - Média': (3, 'Media'),
    '4 - Baixa': (4, 'Baixa'),
    '5 - Muito Baixa': (5, 'Muito Baixa'),
}

DURACAO_CAP_SEGUNDOS = 72 * 3600  # 259200s = 72h


# ---------------------------------------------------------
# EXTRACT
# ---------------------------------------------------------

def extract_bronze(engine) -> pd.DataFrame:
    logger.info('extraindo dados do bronze')
    query = f'''
        SELECT
            id AS bronze_id,
            numero,
            prioridade,
            grupo_designado,
            produto,
            categoria,
            subcategoria,
            item_configuracao,
            solucao,
            aberto,
            encerrado,
            resolvido,
            duracao,
            aberto_por,
            incidente_pai,
            status,
            entrou_kpi,
            kpi_violado
        FROM {SOURCE_SCHEMA}.{SOURCE_TABLE}
    '''
    df = pd.read_sql(query, engine)
    logger.info('bronze extraido: %d linhas', len(df))
    return df


# ---------------------------------------------------------
# DIMENSOES
# ---------------------------------------------------------

def load_dim_grupo(df: pd.DataFrame, engine) -> dict:
    '''Insere grupos novos em dim_grupo e retorna dict nome -> id.'''
    grupos = df['grupo_designado'].dropna().unique().tolist()
    logger.info('grupos encontrados: %d', len(grupos))

    with engine.begin() as conn:
        for nome in grupos:
            conn.execute(text(
                'INSERT INTO silver.dim_grupo (nome) VALUES (:nome) '
                'ON CONFLICT (nome) DO NOTHING'
            ), {'nome': nome})

        rows = conn.execute(text('SELECT id, nome FROM silver.dim_grupo')).fetchall()

    mapping = {row.nome: row.id for row in rows}
    logger.info('dim_grupo carregada: %d registros', len(mapping))
    return mapping


def load_dim_categoria(df: pd.DataFrame, engine) -> dict:
    '''Insere combinacoes unicas de produto/categoria/subcategoria
    e retorna dict (produto, categoria, subcategoria) -> id.'''

    combos = (
        df[['produto', 'categoria', 'subcategoria']]
        .drop_duplicates()
        .where(pd.notnull(df[['produto', 'categoria', 'subcategoria']]), None)
    )

    logger.info('combinacoes de categoria encontradas: %d', len(combos))

    with engine.begin() as conn:
        for _, row in combos.iterrows():
            conn.execute(text(
                'INSERT INTO silver.dim_categoria (produto, categoria, subcategoria) '
                'VALUES (:produto, :categoria, :subcategoria) '
                'ON CONFLICT (produto, categoria, subcategoria) DO NOTHING'
            ), {
                'produto': row['produto'],
                'categoria': row['categoria'],
                'subcategoria': row['subcategoria'],
            })

        rows = conn.execute(text(
            'SELECT id, produto, categoria, subcategoria FROM silver.dim_categoria'
        )).fetchall()

    mapping = {
        (row.produto, row.categoria, row.subcategoria): row.id
        for row in rows
    }
    logger.info('dim_categoria carregada: %d registros', len(mapping))
    return mapping


def fetch_dim_prioridade(engine) -> dict:
    '''Retorna dict codigo -> id de dim_prioridade (ja populada pelo SQL).'''
    with engine.connect() as conn:
        rows = conn.execute(text('SELECT id, codigo FROM silver.dim_prioridade')).fetchall()
    mapping = {row.codigo: row.id for row in rows}
    logger.info('dim_prioridade carregada: %d registros', len(mapping))
    return mapping


def fetch_dim_status(engine) -> dict:
    '''Retorna dict nome -> id de dim_status (ja populada pelo SQL).'''
    with engine.connect() as conn:
        rows = conn.execute(text('SELECT id, nome FROM silver.dim_status')).fetchall()
    mapping = {row.nome: row.id for row in rows}
    logger.info('dim_status carregada: %d registros', len(mapping))
    return mapping


# ---------------------------------------------------------
# TRANSFORM
# ---------------------------------------------------------

def transform(
    df: pd.DataFrame,
    dim_prioridade: dict,
    dim_grupo: dict,
    dim_status: dict,
    dim_categoria: dict,
) -> pd.DataFrame:
    logger.info('iniciando transformacoes')

    # --- prioridade ---
    df['prioridade_codigo'] = df['prioridade'].map(
        lambda x: PRIORIDADE_MAP.get(x, (None, None))[0]
    )
    invalidos = df['prioridade_codigo'].isna().sum()
    if invalidos > 0:
        logger.warning('prioridade nao mapeada em %d linhas', invalidos)

    df['prioridade_id'] = df['prioridade_codigo'].map(dim_prioridade)

    # --- status (normaliza outlier) ---
    df['status'] = df['status'].replace({'Aguardando Problema': 'Encerrado'})
    df['status_id'] = df['status'].map(dim_status)

    status_nao_mapeado = df['status_id'].isna().sum()
    if status_nao_mapeado > 0:
        logger.warning('status nao mapeado em %d linhas: %s',
                       status_nao_mapeado,
                       df.loc[df['status_id'].isna(), 'status'].unique().tolist())

    # --- grupo ---
    df['grupo_id'] = df['grupo_designado'].map(dim_grupo)

    # --- categoria ---
    df['produto'] = df['produto'].where(pd.notnull(df['produto']), None)
    df['categoria'] = df['categoria'].where(pd.notnull(df['categoria']), None)
    df['subcategoria'] = df['subcategoria'].where(pd.notnull(df['subcategoria']), None)

    df['categoria_id'] = df.apply(
        lambda r: dim_categoria.get((r['produto'], r['categoria'], r['subcategoria'])),
        axis=1,
    )

    # --- datas ---
    df['aberto_em'] = pd.to_datetime(df['aberto'],    errors='coerce')
    df['encerrado_em'] = pd.to_datetime(df['encerrado'], errors='coerce')
    df['resolvido_em'] = pd.to_datetime(df['resolvido'], errors='coerce')

    for col in ['aberto_em', 'encerrado_em']:
        nulos = df[col].isna().sum()
        if nulos > 0:
            logger.warning('%s nulo em %d linhas', col, nulos)

    # --- duracao ---
    df['duracao_segundos'] = pd.to_numeric(df['duracao'], errors='coerce').astype('Int64')
    df['duracao_segundos_capped'] = df['duracao_segundos'].clip(upper=DURACAO_CAP_SEGUNDOS)

    # --- features temporais ---
    df['abertura_data'] = df['aberto_em'].dt.date
    df['abertura_hora'] = df['aberto_em'].dt.hour.astype('Int8')
    df['abertura_dia_semana'] = df['aberto_em'].dt.dayofweek.astype('Int8')
    df['abertura_mes'] = df['aberto_em'].dt.month.astype('Int8')
    df['abertura_ano'] = df['aberto_em'].dt.year.astype('Int16')
    df['abertura_fim_de_semana'] = df['abertura_dia_semana'].isin([5, 6])
    df['abertura_fora_horario'] = (df['abertura_hora'] < 8) | (df['abertura_hora'] >= 18)

    # --- campos derivados ---
    df['aberto_automaticamente'] = df['aberto_por'] == 'Monitoramento'
    df['tem_incidente_pai'] = df['incidente_pai'].notna()
    df['sem_intervencao'] = df['status'] == 'Sem Intervenção'

    # --- KPI ---
    df['entrou_kpi'] = df['entrou_kpi'].map({'SIM': True, 'NAO': False})
    df['kpi_violado'] = df['kpi_violado'].map({'SIM': True, 'NAO': False})
    df['elegivel_kpi'] = (
        df['prioridade_codigo'].isin([1, 2, 3]) &
        ~df['sem_intervencao'] &
        ~df['tem_incidente_pai']
    )

    # --- seleciona colunas finais da fato ---
    fato_cols = [
        'numero', 'bronze_id',
        'prioridade_id', 'grupo_id', 'status_id', 'categoria_id',
        'item_configuracao', 'solucao', 'aberto_por', 'incidente_pai',
        'aberto_em', 'encerrado_em', 'resolvido_em',
        'duracao_segundos', 'duracao_segundos_capped',
        'abertura_data', 'abertura_hora', 'abertura_dia_semana',
        'abertura_mes', 'abertura_ano',
        'abertura_fim_de_semana', 'abertura_fora_horario',
        'aberto_automaticamente', 'tem_incidente_pai', 'sem_intervencao',
        'entrou_kpi', 'kpi_violado', 'elegivel_kpi',
    ]

    df = df[fato_cols]
    logger.info('transformacoes concluidas: %d linhas prontas para o silver', len(df))
    return df


# ---------------------------------------------------------
# LOAD
# ---------------------------------------------------------

def load_silver(df: pd.DataFrame, engine) -> int:
    logger.info('iniciando carga no silver.fato_incidentes')

    df.to_sql(
        TARGET_TABLE,
        engine,
        schema=TARGET_SCHEMA,
        if_exists='append',
        index=False,
        method='multi',
        chunksize=1000,
    )

    logger.info('carga concluida: %d linhas inseridas', len(df))
    return len(df)


# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------

def run() -> None:
    logger.info('=== inicio do pipeline clean (bronze -> silver) ===')

    try:
        engine = create_engine(DATABASE_URL)

        df = extract_bronze(engine)

        dim_prioridade = fetch_dim_prioridade(engine)
        dim_status     = fetch_dim_status(engine)
        dim_grupo      = load_dim_grupo(df, engine)
        dim_categoria  = load_dim_categoria(df, engine)

        df = transform(df, dim_prioridade, dim_grupo, dim_status, dim_categoria)
        total = load_silver(df, engine)

        engine.dispose()
        logger.info('pipeline finalizado com sucesso, total de linhas: %d', total)

    except Exception:
        logger.exception('erro inesperado no pipeline clean')
        raise

    logger.info('=== fim do pipeline clean (bronze -> silver) ===')


if __name__ == '__main__':
    run()