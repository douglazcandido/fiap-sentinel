from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Integer, SmallInteger, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

class DimPrioridade(Base):
    __tablename__ = 'dim_prioridade'
    __table_args__ = {'schema': 'silver'}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    codigo: Mapped[int] = mapped_column(SmallInteger, nullable=False, unique=True)
    label: Mapped[str] = mapped_column(Text, nullable=False)
    prazo_ola_horas: Mapped[int | None] = mapped_column(SmallInteger)
    elegivel_kpi: Mapped[bool] = mapped_column(Boolean, nullable=False)

    incidentes: Mapped[list['FatoIncidentes']] = relationship(back_populates='prioridade')

    def __repr__(self) -> str:
        return f'<DimPrioridade(codigo={self.codigo}, label={self.label})>'


class DimGrupo(Base):
    __tablename__ = 'dim_grupo'
    __table_args__ = {'schema': 'silver'}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

    incidentes: Mapped[list['FatoIncidentes']] = relationship(back_populates='grupo')

    def __repr__(self) -> str:
        return f'<DimGrupo(nome={self.nome})>'


class DimStatus(Base):
    __tablename__ = 'dim_status'
    __table_args__ = {'schema': 'silver'}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    sem_intervencao: Mapped[bool] = mapped_column(Boolean, nullable=False)

    incidentes: Mapped[list['FatoIncidentes']] = relationship(back_populates='status')

    def __repr__(self) -> str:
        return f'<DimStatus(nome={self.nome})>'


class DimCategoria(Base):
    __tablename__ = 'dim_categoria'
    __table_args__ = {'schema': 'silver'}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    produto: Mapped[str | None] = mapped_column(Text)
    categoria: Mapped[str | None] = mapped_column(Text)
    subcategoria: Mapped[str | None] = mapped_column(Text)

    incidentes: Mapped[list['FatoIncidentes']] = relationship(back_populates='categoria')

    def __repr__(self) -> str:
        return f'<DimCategoria(produto={self.produto}, categoria={self.categoria})>'


class FatoIncidentes(Base):
    __tablename__ = 'fato_incidentes'
    __table_args__ = {'schema': 'silver'}

    # chave e rastreabilidade
    numero: Mapped[str] = mapped_column(Text, primary_key=True)
    bronze_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)

    # chaves das dimensoes
    prioridade_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    grupo_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    categoria_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    # campos diretos
    item_configuracao: Mapped[str | None] = mapped_column(Text)
    solucao: Mapped[str | None] = mapped_column(Text)
    aberto_por: Mapped[str] = mapped_column(Text, nullable=False)
    incidente_pai: Mapped[str | None] = mapped_column(Text)

    # datas e duracao
    aberto_em: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    encerrado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    resolvido_em: Mapped[datetime | None] = mapped_column(DateTime)
    duracao_segundos: Mapped[int] = mapped_column(Integer, nullable=False)
    duracao_segundos_capped: Mapped[int] = mapped_column(Integer, nullable=False)

    # features temporais
    abertura_data: Mapped[date] = mapped_column(Date, nullable=False)
    abertura_hora: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    abertura_dia_semana: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    abertura_mes: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    abertura_ano: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    abertura_fim_de_semana: Mapped[bool] = mapped_column(Boolean, nullable=False)
    abertura_fora_horario: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # campos derivados
    aberto_automaticamente: Mapped[bool] = mapped_column(Boolean, nullable=False)
    tem_incidente_pai: Mapped[bool] = mapped_column(Boolean, nullable=False)
    sem_intervencao: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # KPI e OLA
    entrou_kpi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    kpi_violado: Mapped[bool | None] = mapped_column(Boolean)
    elegivel_kpi: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # controle de carga
    processado_em: Mapped[datetime] = mapped_column(
        DateTime, server_default=text('now()')
    )

    # relationships
    prioridade: Mapped['DimPrioridade'] = relationship(
        back_populates='incidentes',
        primaryjoin='FatoIncidentes.prioridade_id == DimPrioridade.id',
        foreign_keys='FatoIncidentes.prioridade_id',
    )
    grupo: Mapped['DimGrupo'] = relationship(
        back_populates='incidentes',
        primaryjoin='FatoIncidentes.grupo_id == DimGrupo.id',
        foreign_keys='FatoIncidentes.grupo_id',
    )
    status: Mapped['DimStatus'] = relationship(
        back_populates='incidentes',
        primaryjoin='FatoIncidentes.status_id == DimStatus.id',
        foreign_keys='FatoIncidentes.status_id',
    )
    categoria: Mapped['DimCategoria'] = relationship(
        back_populates='incidentes',
        primaryjoin='FatoIncidentes.categoria_id == DimCategoria.id',
        foreign_keys='FatoIncidentes.categoria_id',
    )

    def __repr__(self) -> str:
        return f'<FatoIncidentes(numero={self.numero}, kpi_violado={self.kpi_violado})>'