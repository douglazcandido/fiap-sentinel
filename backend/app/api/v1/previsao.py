from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.logger import setup_logger
from app.schemas.base import SentinelResponse
from app.schemas.previsao import PrevisaoCompletaSchema
from app.services import previsao as previsao_service


logger = setup_logger(__name__)

router = APIRouter(prefix='/previsao', tags=['Previsao'])


@router.get('', response_model=SentinelResponse[PrevisaoCompletaSchema])
def get_previsao(db: Session = Depends(get_db)):
    '''Retorna a previsao de volume de incidentes para D+1 e D+7,
    gerada pelo modelo NeuralProphet.'''
    logger.info('requisicao recebida: GET /previsao')

    try:
        data = previsao_service.get_previsao_completa(db)
    except ValueError as exc:
        logger.warning('previsao indisponivel: %s', exc)
        raise HTTPException(
            status_code=503,
            detail='Previsoes ainda nao foram geradas. Execute o pipeline de treino primeiro.',
        ) from exc
    except Exception:
        logger.exception('erro inesperado ao buscar previsao')
        raise HTTPException(
            status_code=500,
            detail='Erro interno ao processar previsao.',
        )

    return SentinelResponse(
        mensagem='Previsao de volume recuperada com sucesso',
        data=data,
    )
