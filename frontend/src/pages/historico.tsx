import { useState, useMemo } from "react"
import {
  Database,
  Bot,
  UserX,
  OctagonAlert,
} from "lucide-react"
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
  LineChart,
  Line,
  Legend,
} from "recharts"
import { Topbar } from "@/components/topbar"
import { KpiCard } from "@/components/kpi-card"
import { Card, CardHeader } from "@/components/card"
import { KpiSkeleton, ChartSkeleton } from "@/components/skeleton"
import { ErrorState, EmptyState } from "@/components/states"
import { ProgressBar } from "@/components/badge"
import { CHART_COLORS, axisProps, ChartTooltip } from "@/components/chart-theme"
import { useHistorico } from "@/lib/hooks"
import {
  abbreviateNumber,
  formatInt,
  formatPct,
  formatDate,
  diaSemanaCurto,
  mesLabel,
} from "@/lib/utils"
import type { VolumeMensal, ViolacaoMensal } from "@/lib/types"

const PRIORIDADE_CORES = [CHART_COLORS.high, CHART_COLORS.med, CHART_COLORS.accent, CHART_COLORS.low]

/** Pivot monthly rows (split by priority) into chart points keyed by "Mês/AA". */
function pivotMensal<T extends { ano: number; mes: number; prioridade_label: string }>(
  rows: T[],
  valueKey: keyof T,
  selected: Set<string>,
): { points: Record<string, number | string>[]; prioridades: string[] } {
  const prioridades = Array.from(new Set(rows.map((r) => r.prioridade_label)))
  const map = new Map<string, Record<string, number | string>>()
  for (const r of rows) {
    if (selected.size && !selected.has(r.prioridade_label)) continue
    const key = `${mesLabel(r.mes)}/${String(r.ano).slice(2)}`
    const sortKey = r.ano * 100 + r.mes
    if (!map.has(key)) map.set(key, { label: key, _sort: sortKey })
    const obj = map.get(key)!
    obj[r.prioridade_label] = ((obj[r.prioridade_label] as number) || 0) + (r[valueKey] as number)
  }
  const points = Array.from(map.values()).sort((a, b) => (a._sort as number) - (b._sort as number))
  return { points, prioridades }
}

export default function HistoricoPage() {
  const { data, loading, error, reload } = useHistorico()
  const [prioMensal, setPrioMensal] = useState<Set<string>>(new Set())

  const prioridades = useMemo(
    () => (data ? Array.from(new Set(data.volume_mensal.map((r) => r.prioridade_label))) : []),
    [data],
  )

  function togglePrio(p: string) {
    setPrioMensal((prev) => {
      const next = new Set(prev)
      if (next.has(p)) next.delete(p)
      else next.add(p)
      return next
    })
  }

  const volumeMensal = useMemo(
    () => (data ? pivotMensal<VolumeMensal>(data.volume_mensal, "total_incidentes", prioMensal) : null),
    [data, prioMensal],
  )
  const violacoesMensal = useMemo(
    () =>
      data ? pivotMensal<ViolacaoMensal>(data.violacoes_mensal, "total_violacoes", prioMensal) : null,
    [data, prioMensal],
  )

  const maxHora = useMemo(
    () => (data ? Math.max(...data.volume_por_hora.map((h) => h.total_incidentes)) : 0),
    [data],
  )
  const maxDia = useMemo(
    () => (data ? Math.max(...data.volume_por_dia_semana.map((d) => d.total_incidentes)) : 0),
    [data],
  )

  const k = data?.kpis_gerais

  return (
    <>
      <Topbar
        title="Histórico"
        subtitle="Análise exploratória e agregações dos incidentes"
        lastUpdate={k ? formatDate(k.periodo_fim) : undefined}
      />
      <div className="flex-1 space-y-5 p-6">
        {error ? (
          <ErrorState message={error} onRetry={reload} />
        ) : (
          <>
            {/* KPIs */}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {loading || !k ? (
                Array.from({ length: 4 }).map((_, i) => <KpiSkeleton key={i} />)
              ) : (
                <>
                  <KpiCard
                    index={0}
                    label="Total de Incidentes"
                    icon={<Database className="h-4 w-4" />}
                    value={formatInt(k.total_incidentes)}
                    hint={`${formatDate(k.periodo_inicio)} — ${formatDate(k.periodo_fim)}`}
                  />
                  <KpiCard
                    index={1}
                    tone="accent"
                    label="Abertura Automática"
                    icon={<Bot className="h-4 w-4" />}
                    value={formatPct(k.pct_aberto_automaticamente)}
                    hint="Incidentes abertos por automação"
                  />
                  <KpiCard
                    index={2}
                    tone="med"
                    label="Sem Intervenção"
                    icon={<UserX className="h-4 w-4" />}
                    value={formatPct(k.pct_sem_intervencao)}
                    hint="Resolvidos sem ação humana"
                  />
                  <KpiCard
                    index={3}
                    tone="high"
                    label="Violações OLA"
                    icon={<OctagonAlert className="h-4 w-4" />}
                    value={formatInt(k.total_violacoes_ola)}
                    hint={`${formatInt(k.total_no_kpi)} incidentes no KPI`}
                  />
                </>
              )}
            </div>

            {/* Hora + Dia */}
            <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
              {loading || !data ? (
                <>
                  <ChartSkeleton />
                  <ChartSkeleton />
                </>
              ) : (
                <>
                  <Card index={0}>
                    <CardHeader
                      title="Volume por hora do dia"
                      subtitle="Distribuição de incidentes em 24h"
                    />
                    <ResponsiveContainer width="100%" height={260}>
                      <BarChart data={data.volume_por_hora} margin={{ top: 8, right: 8 }}>
                        <CartesianGrid stroke={CHART_COLORS.grid} vertical={false} />
                        <XAxis
                          dataKey="hora"
                          {...axisProps}
                          tickFormatter={(h) => `${h}h`}
                          interval={1}
                        />
                        <YAxis {...axisProps} tickFormatter={(v) => abbreviateNumber(v)} width={42} />
                        <Tooltip
                          cursor={{ fill: "rgba(255,255,255,0.03)" }}
                          content={({ active, payload }) =>
                            active && payload?.length ? (
                              <ChartTooltip
                                title={`${String(payload[0].payload.hora).padStart(2, "0")}:00h`}
                                rows={[
                                  {
                                    label: "Incidentes",
                                    value: formatInt(payload[0].value as number),
                                    color: CHART_COLORS.accent,
                                  },
                                ]}
                              />
                            ) : null
                          }
                        />
                        <Bar dataKey="total_incidentes" radius={[3, 3, 0, 0]}>
                          {data.volume_por_hora.map((h, i) => (
                            <Cell
                              key={i}
                              fill={
                                h.total_incidentes >= maxHora * 0.85
                                  ? CHART_COLORS.accent
                                  : CHART_COLORS.accent2
                              }
                              fillOpacity={h.total_incidentes >= maxHora * 0.85 ? 1 : 0.45}
                            />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </Card>

                  <Card index={1}>
                    <CardHeader
                      title="Volume por dia da semana"
                      subtitle="Segunda a Domingo"
                    />
                    <ResponsiveContainer width="100%" height={260}>
                      <BarChart data={data.volume_por_dia_semana} margin={{ top: 8, right: 8 }}>
                        <CartesianGrid stroke={CHART_COLORS.grid} vertical={false} />
                        <XAxis
                          dataKey="dia_semana"
                          {...axisProps}
                          tickFormatter={(d) => diaSemanaCurto(d)}
                        />
                        <YAxis {...axisProps} tickFormatter={(v) => abbreviateNumber(v)} width={42} />
                        <Tooltip
                          cursor={{ fill: "rgba(255,255,255,0.03)" }}
                          content={({ active, payload }) =>
                            active && payload?.length ? (
                              <ChartTooltip
                                title={payload[0].payload.dia_label}
                                rows={[
                                  {
                                    label: "Incidentes",
                                    value: formatInt(payload[0].value as number),
                                    color: CHART_COLORS.accent,
                                  },
                                ]}
                              />
                            ) : null
                          }
                        />
                        <Bar dataKey="total_incidentes" radius={[3, 3, 0, 0]}>
                          {data.volume_por_dia_semana.map((d, i) => (
                            <Cell
                              key={i}
                              fill={
                                d.total_incidentes >= maxDia * 0.85
                                  ? CHART_COLORS.accent
                                  : CHART_COLORS.accent2
                              }
                              fillOpacity={d.total_incidentes >= maxDia * 0.85 ? 1 : 0.45}
                            />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </Card>
                </>
              )}
            </div>

            {/* Mensal: volume + violações com filtro de prioridade */}
            {loading || !data ? (
              <ChartSkeleton height={300} />
            ) : (
              <div className="grid grid-cols-1 gap-5 xl:grid-cols-2">
                <Card index={0}>
                  <CardHeader
                    title="Volume mensal por prioridade"
                    subtitle="Evolução temporal"
                    action={
                      <div className="flex flex-wrap gap-1.5">
                        {prioridades.map((p, i) => {
                          const active = prioMensal.size === 0 || prioMensal.has(p)
                          return (
                            <button
                              key={p}
                              onClick={() => togglePrio(p)}
                              className="flex items-center gap-1.5 rounded-md border px-2 py-1 text-[11px] font-medium transition-colors"
                              style={{
                                borderColor: active ? PRIORIDADE_CORES[i % 4] : "var(--color-border)",
                                color: active ? PRIORIDADE_CORES[i % 4] : "var(--color-muted)",
                                background: active
                                  ? `${PRIORIDADE_CORES[i % 4]}1a`
                                  : "transparent",
                              }}
                            >
                              <span
                                className="h-2 w-2 rounded-full"
                                style={{ background: PRIORIDADE_CORES[i % 4] }}
                              />
                              {p}
                            </button>
                          )
                        })}
                      </div>
                    }
                  />
                  <ResponsiveContainer width="100%" height={280}>
                    <LineChart data={volumeMensal!.points} margin={{ top: 8, right: 8 }}>
                      <CartesianGrid stroke={CHART_COLORS.grid} vertical={false} />
                      <XAxis dataKey="label" {...axisProps} />
                      <YAxis {...axisProps} tickFormatter={(v) => abbreviateNumber(v)} width={42} />
                      <Tooltip
                        content={({ active, payload, label }) =>
                          active && payload?.length ? (
                            <ChartTooltip
                              title={String(label)}
                              rows={payload.map((p) => ({
                                label: String(p.name),
                                value: formatInt(p.value as number),
                                color: p.color,
                              }))}
                            />
                          ) : null
                        }
                      />
                      {volumeMensal!.prioridades.map((p, i) =>
                        prioMensal.size === 0 || prioMensal.has(p) ? (
                          <Line
                            key={p}
                            type="monotone"
                            dataKey={p}
                            stroke={PRIORIDADE_CORES[i % 4]}
                            strokeWidth={2}
                            dot={false}
                            activeDot={{ r: 4 }}
                          />
                        ) : null,
                      )}
                    </LineChart>
                  </ResponsiveContainer>
                </Card>

                <Card index={1}>
                  <CardHeader
                    title="Violações OLA mensais"
                    subtitle="Por prioridade ao longo do tempo"
                  />
                  <ResponsiveContainer width="100%" height={280}>
                    <LineChart data={violacoesMensal!.points} margin={{ top: 8, right: 8 }}>
                      <CartesianGrid stroke={CHART_COLORS.grid} vertical={false} />
                      <XAxis dataKey="label" {...axisProps} />
                      <YAxis {...axisProps} tickFormatter={(v) => abbreviateNumber(v)} width={42} />
                      <Tooltip
                        content={({ active, payload, label }) =>
                          active && payload?.length ? (
                            <ChartTooltip
                              title={String(label)}
                              rows={payload.map((p) => ({
                                label: String(p.name),
                                value: formatInt(p.value as number),
                                color: p.color,
                              }))}
                            />
                          ) : null
                        }
                      />
                      <Legend
                        wrapperStyle={{ fontSize: 11, color: CHART_COLORS.muted }}
                        iconType="plainline"
                      />
                      {violacoesMensal!.prioridades.map((p, i) =>
                        prioMensal.size === 0 || prioMensal.has(p) ? (
                          <Line
                            key={p}
                            type="monotone"
                            dataKey={p}
                            stroke={PRIORIDADE_CORES[i % 4]}
                            strokeWidth={2}
                            dot={false}
                            activeDot={{ r: 4 }}
                          />
                        ) : null,
                      )}
                    </LineChart>
                  </ResponsiveContainer>
                </Card>
              </div>
            )}

            {/* Volume por grupo */}
            {loading || !data ? (
              <ChartSkeleton height={300} />
            ) : (
              <Card index={0}>
                <CardHeader
                  title="Volume por equipe / grupo"
                  subtitle="Ordenado por total de incidentes"
                />
                {data.volume_por_grupo.length === 0 ? (
                  <EmptyState message="Nenhum grupo encontrado." />
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-[var(--color-border)] text-left text-xs text-[var(--color-muted)]">
                          <th className="pb-2 pr-4 font-medium">Grupo</th>
                          <th className="pb-2 pr-4 text-right font-medium">Incidentes</th>
                          <th className="pb-2 pr-4 text-right font-medium">No KPI</th>
                          <th className="pb-2 pr-4 text-right font-medium">Violações</th>
                          <th className="min-w-[160px] pb-2 font-medium">Sem intervenção</th>
                        </tr>
                      </thead>
                      <tbody>
                        {[...data.volume_por_grupo]
                          .sort((a, b) => b.total_incidentes - a.total_incidentes)
                          .map((g, i) => (
                            <tr
                              key={g.grupo_nome + i}
                              className="border-b border-[var(--color-border)]/60 transition-colors hover:bg-[var(--color-surface-2)]"
                            >
                              <td className="py-2.5 pr-4 font-medium text-[var(--color-foreground)]">
                                {g.grupo_nome}
                              </td>
                              <td className="tnum py-2.5 pr-4 text-right text-[var(--color-foreground)]">
                                {formatInt(g.total_incidentes)}
                              </td>
                              <td className="tnum py-2.5 pr-4 text-right text-[var(--color-muted)]">
                                {formatInt(g.total_no_kpi)}
                              </td>
                              <td className="tnum py-2.5 pr-4 text-right text-[var(--color-risk-high)]">
                                {formatInt(g.total_violacoes)}
                              </td>
                              <td className="py-2.5">
                                <div className="flex items-center gap-2">
                                  <ProgressBar
                                    value={g.pct_sem_intervencao}
                                    tone="accent"
                                    className="flex-1"
                                  />
                                  <span className="tnum w-12 text-right text-xs text-[var(--color-muted)]">
                                    {formatPct(g.pct_sem_intervencao, 0)}
                                  </span>
                                </div>
                              </td>
                            </tr>
                          ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </Card>
            )}
          </>
        )}
      </div>
    </>
  )
}
