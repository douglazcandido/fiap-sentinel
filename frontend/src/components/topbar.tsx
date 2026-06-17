import { RefreshCw } from "lucide-react"

interface TopbarProps {
  title: string
  subtitle?: string
  lastUpdate?: string
}

export function Topbar({ title, subtitle, lastUpdate }: TopbarProps) {
  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-[var(--color-border)] bg-[var(--color-background)]/85 px-6 backdrop-blur-md">
      <div>
        <h1 className="text-lg font-semibold tracking-tight text-[var(--color-foreground)]">
          {title}
        </h1>
        {subtitle && <p className="text-xs text-[var(--color-muted)]">{subtitle}</p>}
      </div>
      {lastUpdate && (
        <div className="flex items-center gap-2 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] px-3 py-1.5 text-xs text-[var(--color-muted)]">
          <RefreshCw className="h-3.5 w-3.5 text-[var(--color-accent)]" />
          <span>
            Última atualização: <span className="text-[var(--color-foreground)]">{lastUpdate}</span>
          </span>
        </div>
      )}
    </header>
  )
}
