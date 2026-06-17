from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.logger import setup_logger
from app.schemas.base import SentinelResponse
from app.schemas.clusters import ClustersCompletoSchema
from app.services import clusters as clusters_service

logger = setup_logger(__name__)

router = APIRouter(prefix='/clusters', tags=['Padroes e Tendencias'])


@router.get('', response_model=SentinelResponse[ClustersCompletoSchema])
def get_clusters(db: Session = Depends(get_db)):
    '''Retorna os perfis de clusters identificados pelo K-Means,
    representando padroes recorrentes de incidentes.'''
    logger.info('requisicao recebida: GET /clusters')

    data = clusters_service.get_clusters_completo(db)

    return SentinelResponse(
        mensagem='Clusters recuperados com sucesso',
        data=data,
    )
