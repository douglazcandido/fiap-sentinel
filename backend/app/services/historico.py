from sqlalchemy.orm import Session

from app.models.gold_models import (
    DimGrupo,
    DimPrioridade,
    HistoricoKpisGerais,
    HistoricoVolumeDiaSemana,
    HistoricoVolumeGrupo,
    HistoricoVolumeHora,
    HistoricoVolumeMensal,
    HistoricoViolacoesMensal,
)
from app.schemas.historico import (
    HistoricoCompletoSchema,
    KpisGeraisSchema,
    VolumeDiaSemanaSchema,
    VolumeGrupoSchema,
    VolumeHoraSchema,
    VolumeMensalSchema,
    ViolacoesMensalSchema,
)


def get_historico_completo(db: Session) -> HistoricoCompletoSchema:
    kpis = _get_kpis_gerais(db)
    volume_hora = _get_volume_hora(db)
    volume_dia = _get_volume_dia_semana(db)
    volume_mensal = _get_volume_mensal(db)
    violacoes_mensal = _get_violacoes_mensal(db)
    volume_grupo = _get_volume_grupo(db)

    return HistoricoCompletoSchema(
        kpis_gerais=kpis,
        volume_por_hora=volume_hora,
        volume_por_dia_semana=volume_dia,
        volume_mensal=volume_mensal,
        violacoes_mensal=violacoes_mensal,
        volume_por_grupo=volume_grupo,
    )


def _get_kpis_gerais(db: Session) -> KpisGeraisSchema:
    row = db.query(HistoricoKpisGerais).first()
    if not row:
        raise ValueError('kpis gerais nao encontrados no gold')

    return KpisGeraisSchema(
        total_incidentes=row.total_incidentes,
        pct_aberto_automaticamente=float(row.pct_aberto_automaticamente),
        pct_sem_intervencao=float(row.pct_sem_intervencao),
        total_violacoes_ola=row.total_violacoes_ola,
        total_no_kpi=row.total_no_kpi,
        periodo_inicio=row.periodo_inicio.isoformat(),
        periodo_fim=row.periodo_fim.isoformat(),
    )


def _get_volume_hora(db: Session) -> list[VolumeHoraSchema]:
    rows = (
        db.query(HistoricoVolumeHora)
        .order_by(HistoricoVolumeHora.hora)
        .all()
    )
    return [
        VolumeHoraSchema(hora=r.hora, total_incidentes=r.total_incidentes)
        for r in rows
    ]


def _get_volume_dia_semana(db: Session) -> list[VolumeDiaSemanaSchema]:
    rows = (
        db.query(HistoricoVolumeDiaSemana)
        .order_by(HistoricoVolumeDiaSemana.dia_semana)
        .all()
    )
    return [
        VolumeDiaSemanaSchema(
            dia_semana=r.dia_semana,
            dia_label=r.dia_label,
            total_incidentes=r.total_incidentes,
        )
        for r in rows
    ]


def _get_volume_mensal(db: Session) -> list[VolumeMensalSchema]:
    rows = (
        db.query(HistoricoVolumeMensal, DimPrioridade)
        .join(DimPrioridade, HistoricoVolumeMensal.prioridade_id == DimPrioridade.id)
        .order_by(HistoricoVolumeMensal.ano, HistoricoVolumeMensal.mes, DimPrioridade.codigo)
        .all()
    )
    return [
        VolumeMensalSchema(
            ano=r.HistoricoVolumeMensal.ano,
            mes=r.HistoricoVolumeMensal.mes,
            prioridade_codigo=r.DimPrioridade.codigo,
            prioridade_label=r.DimPrioridade.label,
            total_incidentes=r.HistoricoVolumeMensal.total_incidentes,
            total_no_kpi=r.HistoricoVolumeMensal.total_no_kpi,
        )
        for r in rows
    ]


def _get_violacoes_mensal(db: Session) -> list[ViolacoesMensalSchema]:
    rows = (
        db.query(HistoricoViolacoesMensal, DimPrioridade)
        .join(DimPrioridade, HistoricoViolacoesMensal.prioridade_id == DimPrioridade.id)
        .order_by(HistoricoViolacoesMensal.ano, HistoricoViolacoesMensal.mes, DimPrioridade.codigo)
        .all()
    )
    return [
        ViolacoesMensalSchema(
            ano=r.HistoricoViolacoesMensal.ano,
            mes=r.HistoricoViolacoesMensal.mes,
            prioridade_codigo=r.DimPrioridade.codigo,
            prioridade_label=r.DimPrioridade.label,
            total_violacoes=r.HistoricoViolacoesMensal.total_violacoes,
        )
        for r in rows
    ]


def _get_volume_grupo(db: Session) -> list[VolumeGrupoSchema]:
    rows = (
        db.query(HistoricoVolumeGrupo, DimGrupo)
        .join(DimGrupo, HistoricoVolumeGrupo.grupo_id == DimGrupo.id)
        .order_by(HistoricoVolumeGrupo.total_incidentes.desc())
        .all()
    )
    return [
        VolumeGrupoSchema(
            grupo_nome=r.DimGrupo.nome,
            total_incidentes=r.HistoricoVolumeGrupo.total_incidentes,
            total_no_kpi=r.HistoricoVolumeGrupo.total_no_kpi,
            total_violacoes=r.HistoricoVolumeGrupo.total_violacoes,
            pct_sem_intervencao=float(r.HistoricoVolumeGrupo.pct_sem_intervencao),
        )
        for r in rows
    ]
