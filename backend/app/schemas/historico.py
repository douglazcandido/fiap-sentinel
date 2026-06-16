from pydantic import BaseModel, ConfigDict, Field

class KpisGeraisSchema(BaseModel):
    '''4 cards do topo do painel historico.'''
    total_incidentes: int = Field(..., description='Total de incidentes no periodo')
    pct_aberto_automaticamente: float = Field(..., description='% abertos pelo monitoramento automatico')
    pct_sem_intervencao: float = Field(..., description='% encerrados sem intervencao humana')
    total_violacoes_ola: int = Field(..., description='Total de violacoes de OLA no periodo')
    total_no_kpi: int = Field(..., description='Total de incidentes que entraram no KPI')
    periodo_inicio: str = Field(..., description='Data de inicio do periodo analisado')
    periodo_fim: str = Field(..., description='Data de fim do periodo analisado')

    model_config = ConfigDict(from_attributes=True)

class VolumeHoraSchema(BaseModel):
    '''Volume de incidentes por hora do dia (0-23).'''
    hora: int = Field(..., description='Hora do dia (0-23)')
    total_incidentes: int = Field(..., description='Total de incidentes nessa hora')

    model_config = ConfigDict(from_attributes=True)

class VolumeDiaSemanaSchema(BaseModel):
    '''Volume de incidentes por dia da semana.'''
    dia_semana: int = Field(..., description='Dia da semana (0=Seg, 6=Dom)')
    dia_label: str = Field(..., description='Label do dia (Seg, Ter, ...)')
    total_incidentes: int = Field(..., description='Total de incidentes nesse dia')

    model_config = ConfigDict(from_attributes=True)

class VolumeMensalSchema(BaseModel):
    '''Volume mensal de incidentes por prioridade.'''
    ano: int = Field(..., description='Ano de referencia')
    mes: int = Field(..., description='Mes de referencia (1-12)')
    prioridade_codigo: int = Field(..., description='Codigo da prioridade (1-5)')
    prioridade_label: str = Field(..., description='Label da prioridade')
    total_incidentes: int = Field(..., description='Total de incidentes no mes')
    total_no_kpi: int = Field(..., description='Total que entrou no KPI')

    model_config = ConfigDict(from_attributes=True)

class ViolacoesMensalSchema(BaseModel):
    '''Violacoes de OLA mensais por prioridade.'''
    ano: int = Field(..., description='Ano de referencia')
    mes: int = Field(..., description='Mes de referencia (1-12)')
    prioridade_codigo: int = Field(..., description='Codigo da prioridade')
    prioridade_label: str = Field(..., description='Label da prioridade')
    total_violacoes: int = Field(..., description='Total de violacoes no mes')

    model_config = ConfigDict(from_attributes=True)

class VolumeGrupoSchema(BaseModel):
    '''Volume de incidentes por equipe/grupo.'''
    grupo_nome: str = Field(..., description='Nome do grupo/equipe')
    total_incidentes: int = Field(..., description='Total de incidentes')
    total_no_kpi: int = Field(..., description='Total que entrou no KPI')
    total_violacoes: int = Field(..., description='Total de violacoes de OLA')
    pct_sem_intervencao: float = Field(..., description='% de incidentes sem intervencao humana')

    model_config = ConfigDict(from_attributes=True)

class HistoricoCompletoSchema(BaseModel):
    '''Payload completo do painel historico.'''
    kpis_gerais: KpisGeraisSchema
    volume_por_hora: list[VolumeHoraSchema]
    volume_por_dia_semana: list[VolumeDiaSemanaSchema]
    volume_mensal: list[VolumeMensalSchema]
    violacoes_mensal: list[ViolacoesMensalSchema]
    volume_por_grupo: list[VolumeGrupoSchema]
