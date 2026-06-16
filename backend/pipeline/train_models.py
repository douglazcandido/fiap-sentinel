from app.core.logger import setup_logger
from pipeline.train import prophet, random_forest, kmeans

logger = setup_logger(__name__)

def run() -> None:
    logger.info('=== inicio do orquestrador de modelos ===')

    logger.info('executando prophet')
    prophet.run()

    logger.info('executando random forest')
    random_forest.run()

    logger.info('executando k-means')
    kmeans.run()

    logger.info('=== todos os modelos finalizados com sucesso ===')

if __name__ == '__main__':
    run()