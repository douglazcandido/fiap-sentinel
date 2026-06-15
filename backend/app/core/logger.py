import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


LOG_DIR = Path(__file__).resolve().parents[2] / 'logs'
LOG_FILE = LOG_DIR / 'sentinel.log'

MAX_BYTES = 5 * 1024 * 1024  # 5 MB por arquivo
BACKUP_COUNT = 5  # mantem sentinel.log.1 ... sentinel.log.5

LOG_FORMAT = '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    '''Cria/recupera um logger configurado com saida em console e arquivo rotativo.

    Args:
        name: nome do logger, normalmente __name__ do modulo chamador.
        level: nivel minimo de log (default INFO).

    Returns:
        logging.Logger configurado.
    '''
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding='utf-8',
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.propagate = False

    return logger