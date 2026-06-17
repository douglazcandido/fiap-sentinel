from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.logger import setup_logger
from app.schemas.base import SentinelResponse
from app.schemas.recomendacoes import RecomendacoesCompletaSchema
from app.services import recomendacoes as recomendacoes_service

logger = setup_logger(__name__)

router = APIRouter(prefix='/recomendacoes', tags=['Recomendacoes'])

@router.get('', response_model=SentinelResponse[RecomendacoesCompletaSchema])
def get_recomendacoes(
    tipo: str | None = Query(None, description='Filtrar por tipo: equipe, janela_critica, produto_recorrente'),
    db: Session = Depends(get_db),
):
    '''Retorna as recomendacoes praticas geradas pelo Sentinel
    com base nos padroes e riscos identificados.'''
    logger.info('requisicao recebida: GET /recomendacoes (tipo=%s)', tipo)

    data = recomendacoes_service.get_recomendacoes_completo(db, tipo)

    return SentinelResponse(
        mensagem='Recomendacoes recuperadas com sucesso',
        data=data,
    )
