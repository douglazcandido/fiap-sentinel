import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import DATABASE_URL
from app.core.logger import setup_logger
from app.models.gold_models import ClusterIncidente, ClusterPerfil, DimGrupo, DimPrioridade

logger = setup_logger(__name__)

N_CLUSTERS   = 8
RANDOM_STATE = 42

FEATURES_CLUSTER = [
    'prioridade_codigo',
    'abertura_hora',
    'abertura_dia_semana',
    'abertura_mes',
    'abertura_fim_de_semana',
    'abertura_fora_horario',
    'aberto_automaticamente',
    'duracao_segundos_capped',
]

DIAS_SEMANA = {0: 'Seg', 1: 'Ter', 2: 'Qua', 3: 'Qui', 4: 'Sex', 5: 'Sab', 6: 'Dom'}

def fetch_dados(engine) -> pd.DataFrame:
    logger.info('buscando dados do silver para o k-means')
    query = '''
        SELECT
            f.numero,
            p.codigo AS prioridade_codigo,
            g.nome AS grupo_nome,
            f.abertura_hora,
            f.abertura_dia_semana,
            f.abertura_mes,
            f.abertura_fim_de_semana,
            f.abertura_fora_horario,
            f.aberto_automaticamente,
            f.duracao_segundos_capped,
            f.kpi_violado
        FROM silver.fato_incidentes f
        JOIN silver.dim_prioridade p ON f.prioridade_id = p.id
        JOIN silver.dim_grupo g ON f.grupo_id = g.id
    '''
    df = pd.read_sql(query, engine)

    bool_cols = ['abertura_fim_de_semana', 'abertura_fora_horario', 'aberto_automaticamente']
    for col in bool_cols:
        df[col] = df[col].astype(int)

    logger.info('dados carregados: %d incidentes', len(df))
    return df

def treinar_kmeans(df: pd.DataFrame) -> tuple[KMeans, StandardScaler, pd.Series]:
    logger.info('treinando k-means com %d clusters', N_CLUSTERS)

    X = df[FEATURES_CLUSTER].copy()

    scaler  = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = KMeans(n_clusters=N_CLUSTERS, random_state=RANDOM_STATE, n_init=10)
    labels = model.fit_predict(X_scaled)

    logger.info('k-means treinado. distribuicao de clusters:')
    for cluster_id, qtd in pd.Series(labels).value_counts().sort_index().items():
        logger.info('  cluster %d: %d incidentes', cluster_id, qtd)

    return model, scaler, pd.Series(labels, index=df.index)

def gerar_descricao_cluster(perfil: dict) -> str:
    hora = perfil.get('hora_predominante')
    dia  = DIAS_SEMANA.get(perfil.get('dia_semana_predominante'), '?')
    grupo = perfil.get('grupo_nome', '?')
    prioridade = perfil.get('prioridade_label', '?')
    pct_viol = perfil.get('pct_violacao_ola', 0.0) or 0.0

    return (
        f'Pico {dia} ~{hora}h | {grupo} | P-{prioridade} | '
        f'{pct_viol:.1f}% violacao OLA'
    )

def construir_perfis(df: pd.DataFrame, labels: pd.Series) -> list[dict]:
    df = df.copy()
    df['cluster_id'] = labels.values

    perfis = []
    for cluster_id in range(N_CLUSTERS):
        subset = df[df['cluster_id'] == cluster_id]
        if subset.empty:
            continue

        hora_pred = int(subset['abertura_hora'].mode()[0])
        dia_pred = int(subset['abertura_dia_semana'].mode()[0])
        grupo_pred = subset['grupo_nome'].mode()[0]
        prioridade_pred = int(subset['prioridade_codigo'].mode()[0])
        total = len(subset)
        pct_viol = round(
            subset['kpi_violado'].fillna(False).astype(int).mean() * 100, 2
        )

        perfil = {
            'cluster_id': cluster_id,
            'hora_predominante': hora_pred,
            'dia_semana_predominante': dia_pred,
            'grupo_nome': grupo_pred,
            'prioridade_codigo': prioridade_pred,
            'prioridade_label': str(prioridade_pred),
            'total_incidentes': total,
            'pct_violacao_ola': pct_viol,
        }
        perfil['descricao'] = gerar_descricao_cluster(perfil)
        perfis.append(perfil)

    return perfis

def sincronizar_dim_grupo(grupos: list, session: Session) -> dict:
    for nome in grupos:
        if not session.query(DimGrupo).filter_by(nome=nome).first():
            session.add(DimGrupo(nome=nome))
    session.commit()
    return {g.nome: g.id for g in session.query(DimGrupo).all()}

def salvar_perfis(perfis: list[dict], session: Session) -> None:
    logger.info('salvando perfis de clusters no gold')

    dim_prioridade = {p.codigo: p.id for p in session.query(DimPrioridade).all()}
    dim_grupo      = {g.nome: g.id for g in session.query(DimGrupo).all()}

    for perfil in perfis:
        existente = session.query(ClusterPerfil).filter_by(
            cluster_id=perfil['cluster_id']
        ).first()

        grupo_id = dim_grupo.get(perfil['grupo_nome'])
        prioridade_id = dim_prioridade.get(perfil['prioridade_codigo'])

        if existente:
            existente.descricao = perfil['descricao']
            existente.grupo_id = grupo_id
            existente.prioridade_id = prioridade_id
            existente.hora_predominante = perfil['hora_predominante']
            existente.dia_semana_predominante = perfil['dia_semana_predominante']
            existente.total_incidentes = perfil['total_incidentes']
            existente.pct_violacao_ola = perfil['pct_violacao_ola']
        else:
            session.add(ClusterPerfil(
                cluster_id = perfil['cluster_id'],
                descricao = perfil['descricao'],
                grupo_id = grupo_id,
                prioridade_id = prioridade_id,
                hora_predominante = perfil['hora_predominante'],
                dia_semana_predominante  = perfil['dia_semana_predominante'],
                total_incidentes = perfil['total_incidentes'],
                pct_violacao_ola = perfil['pct_violacao_ola'],
            ))

    session.commit()
    logger.info('perfis salvos: %d clusters', len(perfis))

def salvar_incidentes(df: pd.DataFrame, labels: pd.Series, session: Session) -> None:
    logger.info('salvando associacao incidente -> cluster no gold')

    for numero, cluster_id in zip(df['numero'], labels):
        existente = session.query(ClusterIncidente).filter_by(numero=numero).first()

        if existente:
            existente.cluster_id = int(cluster_id)
        else:
            session.add(ClusterIncidente(
                numero     = numero,
                cluster_id = int(cluster_id),
            ))

    session.commit()
    logger.info('associacoes salvas: %d incidentes', len(df))

def run() -> None:
    logger.info('=== inicio do pipeline k-means ===')

    try:
        engine = create_engine(DATABASE_URL)

        df = fetch_dados(engine)

        with Session(engine) as session:
            grupos = df['grupo_nome'].unique().tolist()
            sincronizar_dim_grupo(grupos, session)

        _, _, labels = treinar_kmeans(df)

        perfis = construir_perfis(df, labels)

        with Session(engine) as session:
            salvar_perfis(perfis, session)
            salvar_incidentes(df, labels, session)

        engine.dispose()
        logger.info('pipeline k-means finalizado com sucesso')

    except Exception:
        logger.exception('erro inesperado no pipeline k-means')
        raise

    logger.info('=== fim do pipeline k-means ===')

if __name__ == '__main__':
    run()