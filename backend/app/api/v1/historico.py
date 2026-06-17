from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.logger import setup_logger
from app.schemas.base import SentinelResponse
from app.schemas.historico import HistoricoCompletoSchema
from app.services import historico as historico_service

logger = setup_logger(__name__)

router = APIRouter(prefix='/historico', tags=['Historico'])

@router.get('', response_model=SentinelResponse[HistoricoCompletoSchema])
def get_historico(db: Session = Depends(get_db)):
    '''Retorna o payload completo do painel historico (EDA): kpis gerais,
    volume por hora, dia da semana, mes, e por equipe.'''
    logger.info('requisicao recebida: GET /historico')

    data = historico_service.get_historico_completo(db)

    return SentinelResponse(
        mensagem='Dados historicos recuperados com sucesso',
        data=data,
    )
