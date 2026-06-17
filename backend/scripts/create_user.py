import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import DATABASE_URL
from app.core.logger import setup_logger
from app.core.security import hash_senha
from app.models.usuario_model import Usuario

logger = setup_logger(__name__)

def criar_usuario(nome: str, email: str, senha: str) -> None:
    engine = create_engine(DATABASE_URL)

    with Session(engine) as session:
        existente = session.query(Usuario).filter_by(email=email).first()
        if existente:
            logger.warning('usuario ja existe: %s', email)
            engine.dispose()
            return

        usuario = Usuario(
            nome=nome,
            email=email,
            senha_hash=hash_senha(senha),
        )
        session.add(usuario)
        session.commit()
        logger.info('usuario criado com sucesso: %s', email)

    engine.dispose()


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('uso: python -m scripts.create_user "<nome>" "<email>" "<senha>"')
        sys.exit(1)

    nome_arg, email_arg, senha_arg = sys.argv[1], sys.argv[2], sys.argv[3]
    criar_usuario(nome_arg, email_arg, senha_arg)
