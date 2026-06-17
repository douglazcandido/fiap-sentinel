import { useState, type FormEvent } from "react"
import { useNavigate, useLocation, Navigate } from "react-router-dom"
import { Loader2, AlertCircle, Mail, Lock } from "lucide-react"
import { useAuth } from "@/lib/auth"
import { Logo } from "@/components/logo"

export default function LoginPage() {
  const { login, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState("")
  const [senha, setSenha] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const from = (location.state as { from?: string } | null)?.from || "/"

  if (isAuthenticated) {
    return <Navigate to={from} replace />
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      await login(email, senha)
      navigate(from, { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha ao entrar.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden bg-[var(--color-background)] px-4">
      {/* subtle radar glow backdrop */}
      <div
        aria-hidden
        className="pointer-events-none absolute left-1/2 top-1/3 h-[480px] w-[480px] -translate-x-1/2 -translate-y-1/2 rounded-full blur-[120px]"
        style={{ background: "rgba(34,211,238,0.10)" }}
      />

      <div className="relative z-10 w-full max-w-sm animate-enter">
        <div className="mb-8 flex flex-col items-center text-center">
          <Logo size={64} glow />
          <h1 className="mt-5 text-2xl font-semibold tracking-tight text-[var(--color-foreground)]">
            Sentinel
          </h1>
          <p className="mt-1.5 text-sm text-[var(--color-muted)]">
            Analytics preditivo de incidentes de TI
          </p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-6 shadow-2xl"
        >
          <div className="flex flex-col gap-4">
            <label className="flex flex-col gap-1.5">
              <span className="text-xs font-medium text-[var(--color-muted)]">E-mail</span>
              <div className="relative">
                <Mail className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--color-muted-2)]" />
                <input
                  type="email"
                  required
                  autoComplete="username"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="voce@locaweb.com.br"
                  className="w-full rounded-lg border border-[var(--color-border)] bg-[var(--color-background)] py-2.5 pl-9 pr-3 text-sm text-[var(--color-foreground)] outline-none transition-colors placeholder:text-[var(--color-muted-2)] focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)]/40"
                />
              </div>
            </label>

            <label className="flex flex-col gap-1.5">
              <span className="text-xs font-medium text-[var(--color-muted)]">Senha</span>
              <div className="relative">
                <Lock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--color-muted-2)]" />
                <input
                  type="password"
                  required
                  autoComplete="current-password"
                  value={senha}
                  onChange={(e) => setSenha(e.target.value)}
                  placeholder="••••••••"
                  className="w-full rounded-lg border border-[var(--color-border)] bg-[var(--color-background)] py-2.5 pl-9 pr-3 text-sm text-[var(--color-foreground)] outline-none transition-colors placeholder:text-[var(--color-muted-2)] focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)]/40"
                />
              </div>
            </label>

            <button
              type="submit"
              disabled={loading}
              className="mt-1 flex items-center justify-center gap-2 rounded-lg bg-[var(--color-accent)] py-2.5 text-sm font-semibold text-[#06141b] transition-all hover:bg-[var(--color-accent-2)] hover:text-white disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading && <Loader2 className="h-4 w-4 animate-spin-slow" />}
              {loading ? "Entrando..." : "Entrar"}
            </button>

            {error && (
              <div className="flex items-start gap-2 rounded-lg border border-[var(--color-risk-high)]/30 bg-[var(--color-risk-high-soft)] px-3 py-2 text-xs text-[var(--color-risk-high)]">
                <AlertCircle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                <span>{error}</span>
              </div>
            )}
          </div>
        </form>

        <p className="mt-6 text-center text-xs text-[var(--color-muted-2)]">
          Acesso restrito · Sistema interno Locaweb
        </p>
      </div>
    </main>
  )
}
