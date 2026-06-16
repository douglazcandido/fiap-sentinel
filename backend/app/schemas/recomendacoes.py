from pydantic import BaseModel, ConfigDict, Field

class RecomendacaoSchema(BaseModel):
    '''Uma recomendacao pratica gerada pelo Sentinel.'''
    id: int = Field(..., description='Identificador da recomendacao')
    tipo: str = Field(..., description='Tipo da recomendacao (equipe, janela_critica, produto_recorrente)')
    prioridade: str | None = Field(None, description='Prioridade relacionada (Alta, Media) ou None se geral')
    grupo_nome: str | None = Field(None, description='Equipe relacionada ou None se geral')
    titulo: str = Field(..., description='Titulo curto da recomendacao')
    descricao: str = Field(..., description='Descricao detalhada da recomendacao')

    model_config = ConfigDict(from_attributes=True)

class RecomendacoesCompletaSchema(BaseModel):
    '''Payload completo da Frente 04 - Recomendacoes.'''
    recomendacoes: list[RecomendacaoSchema] = Field(
        ..., description='Lista de recomendacoes ordenadas por relevancia'
    )
    total: int = Field(..., description='Total de recomendacoes geradas')
