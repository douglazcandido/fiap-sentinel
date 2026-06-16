from pydantic import BaseModel, ConfigDict, Field

class PrevisaoDiariaSchema(BaseModel):
    '''Previsao de volume para um dia especifico.'''
    data_referencia: str = Field(..., description='Data prevista (YYYY-MM-DD)')
    horizonte_dias: int = Field(..., description='Horizonte da previsao (1=D+1, 7=D+7)')
    total_previsto: float = Field(..., description='Volume previsto de incidentes')
    limite_inferior: float | None = Field(None, description='Limite inferior do intervalo de confianca')
    limite_superior: float | None = Field(None, description='Limite superior do intervalo de confianca')

    model_config = ConfigDict(from_attributes=True)

class PrevisaoCompletaSchema(BaseModel):
    '''Payload completo da Frente 01 - Previsao de Volume.'''
    d1: PrevisaoDiariaSchema = Field(..., description='Previsao para amanha (D+1)')
    d7: list[PrevisaoDiariaSchema] = Field(..., description='Previsao para os proximos 7 dias (D+7)')
