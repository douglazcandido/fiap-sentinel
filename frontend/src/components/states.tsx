import { AlertTriangle, Inbox, RefreshCw, Loader2 } from "lucide-react"

export function ErrorState({
  message,
  onRetry,
}: {
  message: string
  onRetry?: () => void
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-xl border border-[var(--color-risk-high)]/30 bg-[var(--color-risk-high-soft)] px-6 py-10 text-center">
      <AlertTriangle className="h-7 w-7 text-[var(--color-risk-high)]" />
      <div>
        <p className="text-sm font-medium text-[var(--color-foreground)]">
          Não foi possível carregar os dados
        </p>
        <p className="mt-1 max-w-md text-xs text-[var(--color-muted)]">{message}</p>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-1 inline-flex items-center gap-2 rounded-lg border border-[var(--color-border-strong)] bg-[var(--color-surface-2)] px-3 py-1.5 text-xs font-medium text-[var(--color-foreground)] transition-colors hover:border-[var(--color-accent)] hover:text-[var(--color-accent)]"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          Tentar novamente
        </button>
      )}
    </div>
  )
}

export function EmptyState({
  message = "Nenhum dado disponível no momento.",
}: {
  message?: string
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-xl border border-dashed border-[var(--color-border-strong)] px-6 py-12 text-center">
      <Inbox className="h-7 w-7 text-[var(--color-muted-2)]" />
      <p className="max-w-sm text-sm text-[var(--color-muted)]">{message}</p>
    </div>
  )
}

export function InlineSpinner({ className }: { className?: string }) {
  return <Loader2 className={`animate-spin-slow ${className ?? ""}`} />
}
