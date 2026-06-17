from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

class Usuario(Base):
    __tablename__ = 'usuarios'
    __table_args__ = {'schema': 'public'}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    senha_hash: Mapped[str] = mapped_column(Text, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=text('now()'))

    def __repr__(self) -> str:
        return f'<Usuario(email={self.email})>'
