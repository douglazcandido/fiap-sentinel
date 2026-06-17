import sys
import time

from app.core.logger import setup_logger
from pipeline import aggregate, clean, ingest, recommend, train_models

logger = setup_logger(__name__)

ETAPAS = [
    ('ingest', ingest.run),
    ('clean', clean.run),
    ('aggregate', aggregate.run),
    ('train_models', train_models.run),
    ('recommend', recommend.run),
]

def run() -> None:
    logger.info('=== inicio do pipeline completo sentinel ===')

    inicio_total = time.time()

    for nome, funcao in ETAPAS:
        logger.info('--- iniciando etapa: %s ---', nome)
        inicio_etapa = time.time()

        try:
            funcao()
        except Exception:
            logger.exception('falha na etapa "%s", pipeline interrompido', nome)
            sys.exit(1)

        duracao = round(time.time() - inicio_etapa, 1)
        logger.info('--- etapa "%s" concluida em %ss ---', nome, duracao)

    duracao_total = round(time.time() - inicio_total, 1)
    logger.info('=== pipeline completo finalizado com sucesso em %ss ===', duracao_total)


if __name__ == '__main__':
    run()