from pydantic import BaseModel, ConfigDict, Field

class ClusterPerfilSchema(BaseModel):
    '''Perfil de um cluster identificado pelo K-Means.'''
    cluster_id: int = Field(..., description='Identificador do cluster')
    descricao: str | None = Field(None, description='Descricao legivel do padrao do cluster')
    grupo_nome: str | None = Field(None, description='Equipe predominante no cluster')
    prioridade_label: str | None = Field(None, description='Prioridade predominante no cluster')
    hora_predominante: int | None = Field(None, description='Hora de pico do cluster (0-23)')
    dia_semana_predominante: int | None = Field(None, description='Dia de pico (0=Seg, 6=Dom)')
    total_incidentes: int = Field(..., description='Total de incidentes no cluster')
    pct_violacao_ola: float | None = Field(None, description='% de violacoes de OLA dentro do cluster')

    model_config = ConfigDict(from_attributes=True)

class ClustersCompletoSchema(BaseModel):
    '''Payload completo da Frente 02 - Padroes e Tendencias.'''
    clusters: list[ClusterPerfilSchema] = Field(
        ..., description='Lista de clusters ordenados por total de incidentes'
    )
    total_clusters: int = Field(..., description='Numero total de clusters identificados')
