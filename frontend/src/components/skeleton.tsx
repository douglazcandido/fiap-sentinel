import { cn } from "@/lib/utils"

export function Skeleton({
  className,
  style,
}: {
  className?: string
  style?: React.CSSProperties
}) {
  return (
    <div
      className={cn(
        "animate-skeleton rounded-md bg-[var(--color-surface-3)]",
        className,
      )}
      style={style}
    />
  )
}

/** A KPI card skeleton matching the final layout. */
export function KpiSkeleton() {
  return (
    <div className="rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-5">
      <div className="flex items-center justify-between">
        <Skeleton className="h-3 w-24" />
        <Skeleton className="h-8 w-8 rounded-lg" />
      </div>
      <Skeleton className="mt-4 h-8 w-28" />
      <Skeleton className="mt-3 h-3 w-20" />
    </div>
  )
}

/** A chart card skeleton. */
export function ChartSkeleton({ height = 260 }: { height?: number }) {
  return (
    <div className="rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-5">
      <Skeleton className="h-4 w-40" />
      <Skeleton className="mt-2 h-3 w-24" />
      <Skeleton className="mt-5 w-full rounded-lg" style={{ height }} />
    </div>
  )
}
