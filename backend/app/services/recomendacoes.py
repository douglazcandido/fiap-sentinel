from sqlalchemy.orm import Session

from app.models.gold_models import DimGrupo, Recomendacao
from app.schemas.recomendacoes import RecomendacaoSchema, RecomendacoesCompletaSchema


def get_recomendacoes_completo(
    db: Session,
    tipo: str | None = None,
) -> RecomendacoesCompletaSchema:
    query = (
        db.query(Recomendacao, DimGrupo)
        .outerjoin(DimGrupo, Recomendacao.grupo_id == DimGrupo.id)
    )

    if tipo:
        query = query.filter(Recomendacao.tipo == tipo)

    rows = query.order_by(Recomendacao.id).all()

    recomendacoes = [
        RecomendacaoSchema(
            id=r.Recomendacao.id,
            tipo=r.Recomendacao.tipo,
            prioridade=r.Recomendacao.prioridade,
            grupo_nome=r.DimGrupo.nome if r.DimGrupo else None,
            titulo=r.Recomendacao.titulo,
            descricao=r.Recomendacao.descricao,
        )
        for r in rows
    ]

    return RecomendacoesCompletaSchema(
        recomendacoes=recomendacoes,
        total=len(recomendacoes),
    )
