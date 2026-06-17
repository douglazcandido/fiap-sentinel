import { useMemo } from "react"
import { Link } from "react-router-dom"
import {
  Database,
  UserX,
  OctagonAlert,
  TrendingUp,
  Network,
  Target,
  Lightbulb,
  ArrowRight,
  Clock,
  Calendar,
} from "lucide-react"
import { Topbar } from "@/components/topbar"
import { KpiCard } from "@/components/kpi-card"
import { Card, CardHeader } from "@/components/card"
import { KpiSkeleton, Skeleton } from "@/components/skeleton"
import { Badge, prioridadeTone, ProgressBar } from "@/components/badge"
import { useHistorico, usePrevisao, useClusters, useRisco, useRecomendacoes } from "@/lib/hooks"
import {
  formatInt,
  formatPct,
  formatDate,
  horaLabel,
  diaSemanaLabel,
} from "@/lib/utils"

export default function DashboardPage() {
  const { user } = useUser()
  const hist = useHistorico()
  const prev = usePrevisao()
  const clusters = useClusters()
  const risco = useRisco("todos")
  const recs = useRecomendacoes("todas")

  const k = hist.data?.kpis_gerais

  // cluster de maior risco (maior pct_violacao_ola; fallback maior volume)
  const clusterCritico = useMemo(() => {
    if (!clusters.data?.clusters.length) return null
    return [...clusters.data.clusters].sort(
      (a, b) => (b.pct_violacao_ola ?? 0) - (a.pct_violacao_ola ?? 0),
    )[0]
  }, [clusters.data])

  // KPI de meta mais crítico (menor pct_atingimento_meta)
  const kpiCritico = useMemo(() => {
    const withMeta = risco.data?.kpis_ola.filter((k) => k.pct_atingimento_meta != null) ?? []
    if (!withMeta.length) return null
    return [...withMeta].sort(
      (a, b) => (a.pct_atingimento_meta ?? 0) - (b.pct_atingimento_meta ?? 0),
    )[0]
  }, [risco.data])

  const recDestaque = recs.data?.recomendacoes[0] ?? null

  return (
    <>
      <Topbar
        title="Dashboard"
        subtitle={user ? `Bem-vindo de volta, ${user.nome.split(" ")[0]}` : "Visão executiva"}
        lastUpdate={k ? formatDate(k.periodo_fim) : undefined}
      />
      <div className="flex-1 space-y-5 p-6">
        {/* KPIs principais */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {hist.loading || prev.loading || !k ? (
            Array.from({ length: 4 }).map((_, i) => <KpiSkeleton key={i} />)
          ) : (
            <>
              <KpiCard
                index={0}
                label="Total de Incidentes"
                icon={<Database className="h-4 w-4" />}
                value={formatInt(k.total_incidentes)}
                hint="Histórico completo"
              />
              <KpiCard
                index={1}
                tone="accent"
                label="Sem Intervenção"
                icon={<UserX className="h-4 w-4" />}
                value={formatPct(k.pct_sem_intervencao)}
                hint="Automação sem ação humana"
              />
              <KpiCard
                index={2}
                tone="high"
                label="Violações OLA"
                icon={<OctagonAlert className="h-4 w-4" />}
                value={formatInt(k.total_violacoes_ola)}
                hint={`${formatInt(k.total_no_kpi)} no KPI`}
              />
              <KpiCard
                index={3}
                tone="low"
                label="Previsão D+1"
                icon={<TrendingUp className="h-4 w-4" />}
                value={prev.data ? formatInt(prev.data.d1.total_previsto) : "—"}
                hint={
                  prev.data ? `Para ${formatDate(prev.data.d1.data_referencia)}` : "Sem previsão"
                }
              />
            </>
          )}
        </div>

        {/* Destaques */}
        <div className="grid grid-cols-1 gap-5 lg:grid-cols-3">
          {/* Cluster crítico */}
          <Card index={0} className="flex flex-col">
            <CardHeader
              title="Cluster de maior risco"
              icon={<Network className="h-4 w-4" />}
              action={
                <Link
                  to="/padroes"
                  className="text-[var(--color-muted-2)] transition-colors hover:text-[var(--color-accent)]"
                >
                  <ArrowRight className="h-4 w-4" />
                </Link>
              }
            />
            {clusters.loading ? (
              <Skeleton className="h-28 w-full" />
            ) : !clusterCritico ? (
              <p className="text-sm text-[var(--color-muted)]">Sem clusters disponíveis.</p>
            ) : (
              <div className="flex flex-1 flex-col">
                <p className="text-sm leading-relaxed text-[var(--color-foreground)]">
                  {clusterCritico.descricao ?? `Cluster #${clusterCritico.cluster_id}`}
                </p>
                <div className="mt-3 flex items-center gap-3 text-xs text-[var(--color-muted)]">
                  <span className="flex items-center gap-1">
                    <Clock className="h-3.5 w-3.5 text-[var(--color-accent)]" />
                    {horaLabel(clusterCritico.hora_predominante)}
                  </span>
                  <span className="flex items-center gap-1">
                    <Calendar className="h-3.5 w-3.5 text-[var(--color-accent)]" />
                    {diaSemanaLabel(clusterCritico.dia_semana_predominante)}
                  </span>
                </div>
                <div className="mt-auto flex items-end justify-between pt-4">
                  <div>
                    <p className="text-[11px] text-[var(--color-muted-2)]">Incidentes</p>
                    <p className="tnum text-lg font-semibold text-[var(--color-foreground)]">
                      {formatInt(clusterCritico.total_incidentes)}
                    </p>
                  </div>
                  <Badge tone="high">{formatPct(clusterCritico.pct_violacao_ola)} violação</Badge>
                </div>
              </div>
            )}
          </Card>

          {/* KPI meta crítico */}
          <Card index={1} className="flex flex-col">
            <CardHeader
              title="Meta OLA mais crítica"
              icon={<Target className="h-4 w-4" />}
              action={
                <Link
                  to="/risco"
                  className="text-[var(--color-muted-2)] transition-colors hover:text-[var(--color-accent)]"
                >
                  <ArrowRight className="h-4 w-4" />
                </Link>
              }
            />
            {risco.loading ? (
              <Skeleton className="h-28 w-full" />
            ) : !kpiCritico ? (
              <p className="text-sm text-[var(--color-muted)]">Sem KPIs de meta.</p>
            ) : (
              <div className="flex flex-1 flex-col">
                <div className="flex items-center gap-2">
                  <span className="tnum text-sm font-semibold text-[var(--color-foreground)]">
                    {kpiCritico.ano}
                  </span>
                  <Badge tone={prioridadeTone(kpiCritico.prioridade_label)}>
                    {kpiCritico.prioridade_label}
                  </Badge>
                </div>
                <p className="mt-3 text-[11px] text-[var(--color-muted-2)]">Atingimento da meta</p>
                <div className="tnum text-3xl font-semibold text-[var(--color-foreground)]">
                  {formatPct(kpiCritico.pct_atingimento_meta, 0)}
                </div>
                <ProgressBar value={kpiCritico.pct_atingimento_meta ?? 0} className="mt-3" />
                {kpiCritico.faixa_meta && (
                  <p className="mt-auto pt-3 text-xs text-[var(--color-muted)]">
                    Faixa: {kpiCritico.faixa_meta}
                  </p>
                )}
              </div>
            )}
          </Card>

          {/* Recomendação destaque */}
          <Card index={2} className="flex flex-col">
            <CardHeader
              title="Recomendação em destaque"
              icon={<Lightbulb className="h-4 w-4" />}
              action={
                <Link
                  to="/recomendacoes"
                  className="text-[var(--color-muted-2)] transition-colors hover:text-[var(--color-accent)]"
                >
                  <ArrowRight className="h-4 w-4" />
                </Link>
              }
            />
            {recs.loading ? (
              <Skeleton className="h-28 w-full" />
            ) : !recDestaque ? (
              <p className="text-sm text-[var(--color-muted)]">Nenhuma recomendação gerada.</p>
            ) : (
              <div className="flex flex-1 flex-col">
                <h4 className="text-sm font-semibold text-[var(--color-foreground)]">
                  {recDestaque.titulo}
                </h4>
                <p className="mt-1.5 line-clamp-4 text-sm leading-relaxed text-[var(--color-muted)]">
                  {recDestaque.descricao}
                </p>
                <div className="mt-auto flex flex-wrap gap-1.5 pt-4">
                  {recDestaque.grupo_nome && <Badge tone="accent">{recDestaque.grupo_nome}</Badge>}
                  {recDestaque.prioridade && (
                    <Badge tone={prioridadeTone(recDestaque.prioridade)}>
                      {recDestaque.prioridade}
                    </Badge>
                  )}
                </div>
              </div>
            )}
          </Card>
        </div>
      </div>
    </>
  )
}

import { useAuth } from "@/lib/auth"
function useUser() {
  return useAuth()
}
