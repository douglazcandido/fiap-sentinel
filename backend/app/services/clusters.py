from sqlalchemy.orm import Session

from app.models.gold_models import ClusterPerfil, DimGrupo, DimPrioridade
from app.schemas.clusters import ClusterPerfilSchema, ClustersCompletoSchema


def get_clusters_completo(db: Session) -> ClustersCompletoSchema:
    rows = (
        db.query(ClusterPerfil, DimGrupo, DimPrioridade)
        .outerjoin(DimGrupo, ClusterPerfil.grupo_id == DimGrupo.id)
        .outerjoin(DimPrioridade, ClusterPerfil.prioridade_id == DimPrioridade.id)
        .order_by(ClusterPerfil.total_incidentes.desc())
        .all()
    )

    clusters = [
        ClusterPerfilSchema(
            cluster_id=r.ClusterPerfil.cluster_id,
            descricao=r.ClusterPerfil.descricao,
            grupo_nome=r.DimGrupo.nome if r.DimGrupo else None,
            prioridade_label=r.DimPrioridade.label if r.DimPrioridade else None,
            hora_predominante=r.ClusterPerfil.hora_predominante,
            dia_semana_predominante=r.ClusterPerfil.dia_semana_predominante,
            total_incidentes=r.ClusterPerfil.total_incidentes,
            pct_violacao_ola=float(r.ClusterPerfil.pct_violacao_ola) if r.ClusterPerfil.pct_violacao_ola is not None else None,
        )
        for r in rows
    ]

    return ClustersCompletoSchema(
        clusters=clusters,
        total_clusters=len(clusters),
    )
