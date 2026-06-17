from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.logger import setup_logger
from app.core.security import criar_access_token, verificar_senha
from app.models.usuario_model import Usuario
from app.schemas.auth import LoginRequest, LoginResponseData
from app.schemas.base import SentinelResponse

logger = setup_logger(__name__)

router = APIRouter(prefix='/auth', tags=['Autenticacao'])


@router.post('/login', response_model=SentinelResponse[LoginResponseData])
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    '''Autentica um usuario e retorna um token JWT valido por 8 horas.'''
    logger.info('tentativa de login: %s', payload.email)

    usuario = db.query(Usuario).filter(Usuario.email == payload.email).first()

    if not usuario or not verificar_senha(payload.senha, usuario.senha_hash):
        logger.warning('login falhou para: %s', payload.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Email ou senha invalidos',
        )

    if not usuario.ativo:
        logger.warning('login bloqueado, usuario inativo: %s', payload.email)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Usuario inativo',
        )

    token = criar_access_token(usuario.email)
    logger.info('login bem-sucedido: %s', payload.email)

    data = LoginResponseData(
        access_token=token,
        nome=usuario.nome,
        email=usuario.email,
    )

    return SentinelResponse(
        mensagem='Login realizado com sucesso',
        data=data,
    )