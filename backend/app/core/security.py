import os
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.logger import setup_logger


logger = setup_logger(__name__)

SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'troque-essa-chave-em-producao')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # 8 horas

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def hash_senha(senha: str) -> str:
    return pwd_context.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    return pwd_context.verify(senha, senha_hash)


def criar_access_token(email: str) -> str:
    expira_em = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {'sub': email, 'exp': expira_em}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    logger.info('token gerado para %s, expira em %s', email, expira_em.isoformat())
    return token


def decodificar_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get('sub')
    except JWTError:
        logger.warning('token invalido ou expirado')
        return None
