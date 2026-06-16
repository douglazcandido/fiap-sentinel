import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.core.config import DATABASE_URL
from app.core.logger import setup_logger
from app.models.gold_models import (
    DimGrupo,
    DimPrioridade,
    HistoricoKpisGerais,
    HistoricoVolumeDiaSemana,
    HistoricoVolumeGrupo,
    HistoricoVolumeHora,
    HistoricoVolumeMensal,
    HistoricoViolacoesMensal,
)

logger = setup_logger(__name__)

DIAS_LABEL = {0: 'Seg', 1: 'Ter', 2: 'Qua', 3: 'Qui', 4: 'Sex', 5: 'Sab', 6: 'Dom'}

# ---------------------------------------------------------
# FETCH
# ---------------------------------------------------------

def fetch_dados(engine) -> pd.DataFrame:
    logger.info('buscando dados do silver para agregacoes historicas')
    query = '''
        SELECT
            f.numero,
            f.abertura_hora,
            f.abertura_dia_semana,
            f.abertura_mes,
            f.abertura_ano,
            f.abertura_data,
            f.aberto_automaticamente,
            f.sem_intervencao,
            f.entrou_kpi,
            f.kpi_violado,
            p.codigo AS prioridade_codigo,
            p.label AS prioridade_label,
            g.nome AS grupo_nome
        FROM silver.fato_incidentes f
        JOIN silver.dim_prioridade p ON f.prioridade_id = p.id
        JOIN silver.dim_grupo g ON f.grupo_id = g.id
    '''
    df = pd.read_sql(query, engine)
    logger.info('dados carregados: %d incidentes', len(df))
    return df

# ---------------------------------------------------------
# SINCRONIZAR DIMS
# ---------------------------------------------------------

def sincronizar_dims(df: pd.DataFrame, session: Session) -> tuple[dict, dict]:
    for nome in df['grupo_nome'].unique():
        if not session.query(DimGrupo).filter_by(nome=nome).first():
            session.add(DimGrupo(nome=nome))
    session.commit()

    dim_prioridade = {p.codigo: p.id for p in session.query(DimPrioridade).all()}
    dim_grupo = {g.nome: g.id for g in session.query(DimGrupo).all()}
    logger.info('dims sincronizadas: %d prioridades, %d grupos', len(dim_prioridade), len(dim_grupo))
    return dim_prioridade, dim_grupo

# ---------------------------------------------------------
# KPIs GERAIS
# ---------------------------------------------------------

def agregar_kpis_gerais(df: pd.DataFrame, session: Session) -> None:
    logger.info('agregando kpis gerais')

    total = int(len(df))
    pct_automatico = float(round(df["aberto_automaticamente"].mean() * 100, 2))
    pct_sem_intervencao = float(round(df['sem_intervencao'].mean() * 100, 2))
    total_violacoes = int(df['kpi_violado'].fillna(False).astype(bool).sum())
    total_no_kpi = int(df['entrou_kpi'].sum())
    periodo_inicio = df['abertura_data'].min()
    periodo_fim = df['abertura_data'].max()

    existente = session.query(HistoricoKpisGerais).first()
    if existente:
        existente.total_incidentes = total
        existente.pct_aberto_automaticamente = pct_automatico
        existente.pct_sem_intervencao = pct_sem_intervencao
        existente.total_violacoes_ola = total_violacoes
        existente.total_no_kpi = total_no_kpi
        existente.periodo_inicio = periodo_inicio
        existente.periodo_fim = periodo_fim
    else:
        session.add(HistoricoKpisGerais(
            total_incidentes = total,
            pct_aberto_automaticamente = pct_automatico,
            pct_sem_intervencao = pct_sem_intervencao,
            total_violacoes_ola = total_violacoes,
            total_no_kpi = total_no_kpi,
            periodo_inicio = periodo_inicio,
            periodo_fim = periodo_fim,
        ))

    session.commit()
    logger.info(
        'kpis gerais salvos: total=%d, violacoes=%d, pct_sem_intervencao=%.1f%%',
        total, total_violacoes, pct_sem_intervencao,
    )

# ---------------------------------------------------------
# VOLUME POR HORA
# ---------------------------------------------------------

def agregar_volume_hora(df: pd.DataFrame, session: Session) -> None:
    logger.info('agregando volume por hora do dia')

    por_hora = df.groupby('abertura_hora').size().reset_index(name='total_incidentes')

    for _, row in por_hora.iterrows():
        hora  = int(row['abertura_hora'])
        total = int(row['total_incidentes'])

        existente = session.query(HistoricoVolumeHora).filter_by(hora=hora).first()
        if existente:
            existente.total_incidentes = total
        else:
            session.add(HistoricoVolumeHora(hora=hora, total_incidentes=total))

    session.commit()
    logger.info('volume por hora salvo: %d registros', len(por_hora))

# ---------------------------------------------------------
# VOLUME POR DIA DA SEMANA
# ---------------------------------------------------------

def agregar_volume_dia_semana(df: pd.DataFrame, session: Session) -> None:
    logger.info('agregando volume por dia da semana')

    por_dia = df.groupby('abertura_dia_semana').size().reset_index(name='total_incidentes')

    for _, row in por_dia.iterrows():
        dia = int(row['abertura_dia_semana'])
        total = int(row['total_incidentes'])
        label = DIAS_LABEL.get(dia, str(dia))

        existente = session.query(HistoricoVolumeDiaSemana).filter_by(dia_semana=dia).first()
        if existente:
            existente.total_incidentes = total
            existente.dia_label = label
        else:
            session.add(HistoricoVolumeDiaSemana(
                dia_semana=dia, dia_label=label, total_incidentes=total
            ))

    session.commit()
    logger.info('volume por dia da semana salvo: %d registros', len(por_dia))

# ---------------------------------------------------------
# VOLUME MENSAL POR PRIORIDADE
# ---------------------------------------------------------

def agregar_volume_mensal(df: pd.DataFrame, dim_prioridade: dict, session: Session) -> None:
    logger.info('agregando volume mensal por prioridade')

    por_mes = (
        df.groupby(['abertura_ano', 'abertura_mes', 'prioridade_codigo'])
        .agg(
            total_incidentes=('numero', 'count'),
            total_no_kpi=('entrou_kpi', 'sum'),
        )
        .reset_index()
    )

    for _, row in por_mes.iterrows():
        ano = int(row['abertura_ano'])
        mes = int(row['abertura_mes'])
        prioridade_id = dim_prioridade.get(int(row['prioridade_codigo']))
        total = int(row['total_incidentes'])
        total_kpi = int(row['total_no_kpi'])

        existente = session.query(HistoricoVolumeMensal).filter_by(
            ano=ano, mes=mes, prioridade_id=prioridade_id
        ).first()

        if existente:
            existente.total_incidentes = total
            existente.total_no_kpi = total_kpi
        else:
            session.add(HistoricoVolumeMensal(
                ano=ano, mes=mes, prioridade_id=prioridade_id,
                total_incidentes=total, total_no_kpi=total_kpi,
            ))

    session.commit()
    logger.info('volume mensal salvo: %d registros', len(por_mes))

# ---------------------------------------------------------
# VIOLACOES MENSAIS POR PRIORIDADE
# ---------------------------------------------------------

def agregar_violacoes_mensal(df: pd.DataFrame, dim_prioridade: dict, session: Session) -> None:
    logger.info('agregando violacoes mensais por prioridade')

    df_violacoes = df[df['kpi_violado'] == True].copy()

    por_mes = (
        df_violacoes.groupby(['abertura_ano', 'abertura_mes', 'prioridade_codigo'])
        .size()
        .reset_index(name='total_violacoes')
    )

    for _, row in por_mes.iterrows():
        ano = int(row['abertura_ano'])
        mes = int(row['abertura_mes'])
        prioridade_id = dim_prioridade.get(int(row['prioridade_codigo']))
        total = int(row['total_violacoes'])

        existente = session.query(HistoricoViolacoesMensal).filter_by(
            ano=ano, mes=mes, prioridade_id=prioridade_id
        ).first()

        if existente:
            existente.total_violacoes = total
        else:
            session.add(HistoricoViolacoesMensal(
                ano=ano, mes=mes, prioridade_id=prioridade_id,
                total_violacoes=total,
            ))

    session.commit()
    logger.info('violacoes mensais salvas: %d registros', len(por_mes))

# ---------------------------------------------------------
# VOLUME POR GRUPO
# ---------------------------------------------------------

def agregar_volume_grupo(df: pd.DataFrame, dim_grupo: dict, session: Session) -> None:
    logger.info('agregando volume por grupo')

    por_grupo = (
        df.groupby('grupo_nome')
        .agg(
            total_incidentes=('numero', 'count'),
            total_no_kpi=('entrou_kpi', 'sum'),
            total_violacoes=('kpi_violado', lambda x: x.fillna(False).sum()),
            pct_sem_intervencao=('sem_intervencao', lambda x: round(x.mean() * 100, 2)),
        )
        .reset_index()
    )

    for _, row in por_grupo.iterrows():
        grupo_id = dim_grupo.get(row['grupo_nome'])

        existente = session.query(HistoricoVolumeGrupo).filter_by(grupo_id=grupo_id).first()

        if existente:
            existente.total_incidentes = int(row['total_incidentes'])
            existente.total_no_kpi = int(row['total_no_kpi'])
            existente.total_violacoes = int(row['total_violacoes'])
            existente.pct_sem_intervencao = float(row['pct_sem_intervencao'])
        else:
            session.add(HistoricoVolumeGrupo(
                grupo_id = grupo_id,
                total_incidentes = int(row['total_incidentes']),
                total_no_kpi = int(row['total_no_kpi']),
                total_violacoes = int(row['total_violacoes']),
                pct_sem_intervencao = float(row['pct_sem_intervencao']),
            ))

    session.commit()
    logger.info('volume por grupo salvo: %d registros', len(por_grupo))

# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------

def run() -> None:
    logger.info('=== inicio do pipeline aggregate (silver -> gold historico) ===')

    try:
        engine = create_engine(DATABASE_URL)

        df = fetch_dados(engine)

        with Session(engine) as session:
            dim_prioridade, dim_grupo = sincronizar_dims(df, session)

            agregar_kpis_gerais(df, session)
            agregar_volume_hora(df, session)
            agregar_volume_dia_semana(df, session)
            agregar_volume_mensal(df, dim_prioridade, session)
            agregar_violacoes_mensal(df, dim_prioridade, session)
            agregar_volume_grupo(df, dim_grupo, session)

        engine.dispose()
        logger.info('pipeline aggregate finalizado com sucesso')

    except Exception:
        logger.exception('erro inesperado no pipeline aggregate')
        raise

    logger.info('=== fim do pipeline aggregate (silver -> gold historico) ===')

if __name__ == '__main__':
    run()