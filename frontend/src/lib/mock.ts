import type {
  LoginResponse,
  HistoricoData,
  PrevisaoData,
  RiscoData,
  ClustersData,
  RecomendacoesData,
  Recomendacao,
} from "./types"

/**
 * Mock mode is enabled when no real backend base URL is provided.
 * Set VITE_API_BASE_URL to point at the FastAPI backend to disable mocks.
 */
export const MOCK_MODE = !import.meta.env.VITE_API_BASE_URL

const DIAS = ["Domingo", "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"]
const PRIORIDADES = [
  { codigo: 1, label: "P1 - Crítica" },
  { codigo: 2, label: "P2 - Alta" },
  { codigo: 3, label: "P3 - Média" },
  { codigo: 4, label: "P4 - Baixa" },
]

// Deterministic pseudo-random so charts look stable across reloads.
function seeded(seed: number) {
  let s = seed
  return () => {
    s = (s * 9301 + 49297) % 233280
    return s / 233280
  }
}
const rnd = seeded(42)

function mockHistorico(): HistoricoData {
  const volume_por_hora = Array.from({ length: 24 }, (_, hora) => {
    const peak = Math.exp(-Math.pow(hora - 14, 2) / 24)
    return {
      hora,
      total_incidentes: Math.round(40 + peak * 220 + rnd() * 30),
    }
  })

  const volume_por_dia_semana = DIAS.map((dia_label, dia_semana) => {
    const weekend = dia_semana === 0 || dia_semana === 6
    return {
      dia_semana,
      dia_label,
      total_incidentes: Math.round((weekend ? 380 : 920) + rnd() * 160),
    }
  })

  const volume_mensal: HistoricoData["volume_mensal"] = []
  const violacoes_mensal: HistoricoData["violacoes_mensal"] = []
  for (let mes = 1; mes <= 12; mes++) {
    for (const p of PRIORIDADES) {
      const base = (5 - p.codigo) * 90 + rnd() * 120
      const total = Math.round(base + mes * 4)
      const noKpi = Math.round(total * 0.82)
      volume_mensal.push({
        ano: 2024,
        mes,
        prioridade_codigo: p.codigo,
        prioridade_label: p.label,
        total_incidentes: total,
        total_no_kpi: noKpi,
      })
      violacoes_mensal.push({
        ano: 2024,
        mes,
        prioridade_codigo: p.codigo,
        prioridade_label: p.label,
        total_violacoes: Math.round(noKpi * (0.05 + p.codigo * 0.02 + rnd() * 0.03)),
      })
    }
  }

  const grupos = [
    "Infraestrutura",
    "Aplicações",
    "Banco de Dados",
    "Redes",
    "Service Desk",
    "Segurança",
  ]
  const volume_por_grupo = grupos.map((grupo_nome) => {
    const total = Math.round(800 + rnd() * 1800)
    const noKpi = Math.round(total * 0.85)
    return {
      grupo_nome,
      total_incidentes: total,
      total_no_kpi: noKpi,
      total_violacoes: Math.round(noKpi * (0.04 + rnd() * 0.1)),
      pct_sem_intervencao: Math.round(rnd() * 28 * 10) / 10,
    }
  })

  const total_incidentes = volume_por_grupo.reduce((a, g) => a + g.total_incidentes, 0)
  const total_no_kpi = volume_por_grupo.reduce((a, g) => a + g.total_no_kpi, 0)
  const total_violacoes = volume_por_grupo.reduce((a, g) => a + g.total_violacoes, 0)

  return {
    kpis_gerais: {
      total_incidentes,
      pct_aberto_automaticamente: 37.4,
      pct_sem_intervencao: 18.9,
      total_violacoes_ola: total_violacoes,
      total_no_kpi,
      periodo_inicio: "2024-01-01",
      periodo_fim: "2024-12-31",
    },
    volume_por_hora,
    volume_por_dia_semana,
    volume_mensal,
    violacoes_mensal,
    volume_por_grupo,
  }
}

function mockPrevisao(): PrevisaoData {
  const today = new Date()
  const fmt = (d: Date) => d.toISOString().slice(0, 10)
  const d7: PrevisaoData["d7"] = Array.from({ length: 7 }, (_, i) => {
    const date = new Date(today)
    date.setDate(today.getDate() + i + 1)
    const center = 240 + Math.sin(i / 2) * 40 + rnd() * 30
    return {
      data_referencia: fmt(date),
      horizonte_dias: i + 1,
      total_previsto: Math.round(center),
      limite_inferior: Math.round(center * 0.82),
      limite_superior: Math.round(center * 1.18),
    }
  })
  return { d1: d7[0], d7 }
}

function mockRisco(): RiscoData {
  return {
    distribuicao_risco: [
      { classe_risco: "Baixo", quantidade: 1280 },
      { classe_risco: "Medio", quantidade: 460 },
      { classe_risco: "Alto", quantidade: 175 },
    ],
    kpis_ola: PRIORIDADES.map((p) => {
      const total = Math.round(2000 + rnd() * 3000)
      const viol = Math.round(total * (0.03 + p.codigo * 0.015))
      const pct = Math.round((1 - viol / total) * 1000) / 10
      const projViol = Math.round(viol * 1.12)
      return {
        ano: 2024,
        prioridade_codigo: p.codigo,
        prioridade_label: p.label,
        violacoes_acumuladas: viol,
        total_no_kpi: total,
        pct_atingimento_meta: pct,
        faixa_meta: pct >= 95 ? "Dentro da meta" : pct >= 90 ? "Atenção" : "Crítico",
        violacoes_projetadas_ano: projViol,
        pct_projetado_meta: Math.round((1 - projViol / total) * 1000) / 10,
      }
    }),
  }
}

function mockClusters(): ClustersData {
  const grupos = ["Infraestrutura", "Aplicações", "Banco de Dados", "Redes", "Segurança"]
  const clusters = Array.from({ length: 8 }, (_, i) => ({
    cluster_id: i + 1,
    descricao: `Padrão de incidentes #${i + 1}`,
    grupo_nome: grupos[i % grupos.length],
    prioridade_label: PRIORIDADES[i % PRIORIDADES.length].label,
    hora_predominante: Math.round(8 + rnd() * 12),
    dia_semana_predominante: Math.round(1 + rnd() * 5),
    total_incidentes: Math.round(120 + rnd() * 900),
    pct_violacao_ola: Math.round(rnd() * 35 * 10) / 10,
  }))
  return { clusters, total_clusters: clusters.length }
}

function mockRecomendacoes(): RecomendacoesData {
  const recs: Recomendacao[] = [
    {
      id: 1,
      tipo: "equipe",
      prioridade: "P1 - Crítica",
      grupo_nome: "Banco de Dados",
      titulo: "Reforçar equipe de Banco de Dados no turno da tarde",
      descricao:
        "O grupo de Banco de Dados concentra 28% das violações de OLA em incidentes P1, com pico entre 14h e 17h. Recomenda-se alocar ao menos um analista sênior adicional nesse turno.",
    },
    {
      id: 2,
      tipo: "janela_critica",
      prioridade: "P2 - Alta",
      grupo_nome: "Aplicações",
      titulo: "Antecipar plantão nas quartas-feiras",
      descricao:
        "Quartas-feiras apresentam volume 22% acima da média semanal. Antecipar o início do plantão em 1 hora reduz o tempo de fila inicial.",
    },
    {
      id: 3,
      tipo: "produto_recorrente",
      prioridade: "P3 - Média",
      grupo_nome: "Infraestrutura",
      titulo: "Investigar recorrência no serviço de autenticação",
      descricao:
        "Incidentes ligados ao serviço de autenticação reaparecem a cada 6 dias em média, sugerindo causa raiz não tratada. Recomenda-se análise de problema dedicada.",
    },
    {
      id: 4,
      tipo: "equipe",
      prioridade: "P4 - Baixa",
      grupo_nome: "Service Desk",
      titulo: "Automatizar triagem de chamados de baixa prioridade",
      descricao:
        "37% dos incidentes P4 são abertos automaticamente e poderiam ser resolvidos via runbook, liberando a equipe para casos de maior impacto.",
    },
    {
      id: 5,
      tipo: "janela_critica",
      prioridade: "P1 - Crítica",
      grupo_nome: "Redes",
      titulo: "Monitoramento reforçado na virada do mês",
      descricao:
        "Há aumento consistente de violações de OLA nos primeiros 3 dias de cada mês no grupo de Redes, provavelmente ligado a fechamentos contábeis.",
    },
  ]
  return { recomendacoes: recs, total: recs.length }
}

export const mockLogin: LoginResponse = {
  access_token: "mock-token-sentinel-demo",
  token_type: "bearer",
  nome: "Analista Demo",
  email: "demo@sentinel.app",
}

/** Returns mock payload for a given path, or throws if unknown. */
export function getMockData<T>(path: string): T {
  if (path.includes("/historico")) return mockHistorico() as T
  if (path.includes("/previsao")) return mockPrevisao() as T
  if (path.includes("/risco")) return mockRisco() as T
  if (path.includes("/clusters")) return mockClusters() as T
  if (path.includes("/recomendacoes")) return mockRecomendacoes() as T
  throw new Error(`Mock não definido para a rota: ${path}`)
}
