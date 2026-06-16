import pandas as pd
from prophet import Prophet
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import DATABASE_URL
from app.core.logger import setup_logger
from app.models.gold_models import PrevisaoVolume

logger = setup_logger(__name__)

HORIZONTE_DIAS = [1, 7]

def fetch_serie_temporal(engine) -> pd.DataFrame:
    logger.info('buscando serie temporal do silver')
    query = '''
        SELECT
            abertura_data AS ds,
            count(*) AS y
        FROM silver.fato_incidentes
        GROUP BY abertura_data
        ORDER BY abertura_data
    '''
    df = pd.read_sql(query, engine)
    df['ds'] = pd.to_datetime(df['ds'])
    df['y'] = df['y'].astype(float)
    logger.info('serie temporal carregada: %d dias', len(df))
    return df

def treinar_prophet(df: pd.DataFrame) -> Prophet:
    logger.info('treinando modelo prophet')
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        seasonality_mode='multiplicative',
    )
    model.fit(df)
    logger.info('modelo prophet treinado com sucesso')
    return model

def gerar_previsoes(model: Prophet, horizonte: int) -> pd.DataFrame:
    logger.info('gerando previsao para D+%d', horizonte)
    futuro = model.make_future_dataframe(periods=horizonte, freq='D')
    forecast = model.predict(futuro)
    previsoes = forecast.tail(horizonte)[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
    previsoes['horizonte_dias'] = horizonte
    previsoes.rename(columns={'ds': 'data_referencia'}, inplace=True)
    return previsoes

def salvar_previsoes(previsoes: pd.DataFrame, session: Session) -> None:
    logger.info('salvando previsoes no gold')

    for _, row in previsoes.iterrows():
        registro = PrevisaoVolume(
            data_referencia=row['data_referencia'].date(),
            horizonte_dias=int(row['horizonte_dias']),
            total_previsto=round(float(row['yhat']), 2),
            limite_inferior=round(float(row['yhat_lower']), 2),
            limite_superior=round(float(row['yhat_upper']), 2),
        )

        existente = session.query(PrevisaoVolume).filter_by(
            data_referencia=registro.data_referencia,
            horizonte_dias=registro.horizonte_dias,
        ).first()

        if existente:
            existente.total_previsto = registro.total_previsto
            existente.limite_inferior = registro.limite_inferior
            existente.limite_superior = registro.limite_superior
        else:
            session.add(registro)

    session.commit()
    logger.info('previsoes salvas: %d registros', len(previsoes))

def run() -> None:
    logger.info('=== inicio do pipeline prophet ===')

    try:
        engine = create_engine(DATABASE_URL)

        df = fetch_serie_temporal(engine)
        model = treinar_prophet(df)

        with Session(engine) as session:
            for horizonte in HORIZONTE_DIAS:
                previsoes = gerar_previsoes(model, horizonte)
                salvar_previsoes(previsoes, session)

        engine.dispose()
        logger.info('pipeline prophet finalizado com sucesso')

    except Exception:
        logger.exception('erro inesperado no pipeline prophet')
        raise

    logger.info('=== fim do pipeline prophet ===')

if __name__ == '__main__':
    run()