from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.logger import setup_logger
from app.schemas.base import SentinelResponse
from app.schemas.risco import RiscoCompletoSchema
from app.services import risco as risco_service


logger = setup_logger(__name__)

router = APIRouter(prefix='/risco', tags=['Risco OLA'])


@router.get('', response_model=SentinelResponse[RiscoCompletoSchema])
def get_risco(
    ano: int | None = Query(None, description='Filtrar KPIs por ano especifico'),
    db: Session = Depends(get_db),
):
    '''Retorna a distribuicao de risco de violacao de OLA (Random Forest)
    e os KPIs de atingimento de meta por ano e prioridade.'''
    logger.info('requisicao recebida: GET /risco (ano=%s)', ano)

    try:
        data = risco_service.get_risco_completo(db, ano)
    except Exception:
        logger.exception('erro inesperado ao buscar dados de risco')
        raise HTTPException(
            status_code=500,
            detail='Erro interno ao processar dados de risco OLA.',
        )

    return SentinelResponse(
        mensagem='Dados de risco OLA recuperados com sucesso',
        data=data,
    )
