from sqlalchemy.orm import Session

from app.models.gold_models import PrevisaoVolume
from app.schemas.previsao import PrevisaoCompletaSchema, PrevisaoDiariaSchema


def get_previsao_completa(db: Session) -> PrevisaoCompletaSchema:
    rows_d1 = (
        db.query(PrevisaoVolume)
        .filter(PrevisaoVolume.horizonte_dias == 1)
        .order_by(PrevisaoVolume.data_referencia)
        .all()
    )
    rows_d7 = (
        db.query(PrevisaoVolume)
        .filter(PrevisaoVolume.horizonte_dias == 7)
        .order_by(PrevisaoVolume.data_referencia)
        .all()
    )

    if not rows_d1:
        raise ValueError('previsao D+1 nao encontrada no gold')
    if not rows_d7:
        raise ValueError('previsao D+7 nao encontrada no gold')

    d1 = _to_schema(rows_d1[0])
    d7 = [_to_schema(r) for r in rows_d7]

    return PrevisaoCompletaSchema(d1=d1, d7=d7)


def _to_schema(row: PrevisaoVolume) -> PrevisaoDiariaSchema:
    return PrevisaoDiariaSchema(
        data_referencia=row.data_referencia.isoformat(),
        horizonte_dias=row.horizonte_dias,
        total_previsto=float(row.total_previsto),
        limite_inferior=float(row.limite_inferior) if row.limite_inferior is not None else None,
        limite_superior=float(row.limite_superior) if row.limite_superior is not None else None,
    )
