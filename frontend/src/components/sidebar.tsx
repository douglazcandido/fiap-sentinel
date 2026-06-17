import { NavLink, useLocation } from "react-router-dom"
import {
  LayoutGrid,
  BarChart3,
  TrendingUp,
  ShieldAlert,
  Network,
  Lightbulb,
  LogOut,
} from "lucide-react"
import { useAuth } from "@/lib/auth"
import { Logo } from "@/components/logo"
import { cn } from "@/lib/utils"

export const NAV_ITEMS = [
  { to: "/", label: "Dashboard", icon: LayoutGrid, end: true },
  { to: "/historico", label: "Histórico", icon: BarChart3 },
  { to: "/previsao", label: "Previsão", icon: TrendingUp },
  { to: "/risco", label: "Risco OLA", icon: ShieldAlert },
  { to: "/padroes", label: "Padrões", icon: Network },
  { to: "/recomendacoes", label: "Recomendações", icon: Lightbulb },
]

export function Sidebar() {
  const { user, logout } = useAuth()
  useLocation() // ensure re-render on route change for active states

  const inicial = user?.nome?.trim().charAt(0).toUpperCase() || "?"

  return (
    <aside
      className={cn(
        "group/sidebar fixed inset-y-0 left-0 z-40 flex flex-col border-r border-[var(--color-border)] bg-[var(--color-surface)]",
        "w-[68px] transition-[width] duration-200 ease-out hover:w-60",
      )}
    >
      {/* Logo */}
      <div className="relative flex h-16 items-center gap-3 overflow-hidden px-[18px]">
        <Logo size={32} glow />
        <span className="whitespace-nowrap text-base font-semibold tracking-tight text-[var(--color-foreground)] opacity-0 transition-opacity duration-200 group-hover/sidebar:opacity-100">
          Sentinel
        </span>
      </div>

      {/* Nav */}
      <nav className="mt-2 flex flex-1 flex-col gap-1 px-3">
        {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              cn(
                "relative flex h-10 items-center gap-3 overflow-hidden rounded-lg px-[10px] text-sm transition-colors",
                isActive
                  ? "bg-[var(--color-accent-soft)] text-[var(--color-accent)]"
                  : "text-[var(--color-muted)] hover:bg-[var(--color-surface-2)] hover:text-[var(--color-foreground)]",
              )
            }
          >
            {({ isActive }) => (
              <>
                {isActive && (
                  <span className="absolute left-0 top-1/2 h-5 w-[3px] -translate-y-1/2 rounded-r bg-[var(--color-accent)]" />
                )}
                <Icon className="h-[18px] w-[18px] shrink-0" />
                <span className="whitespace-nowrap opacity-0 transition-opacity duration-200 group-hover/sidebar:opacity-100">
                  {label}
                </span>
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Footer: user + logout */}
      <div className="border-t border-[var(--color-border)] p-3">
        <div className="flex items-center gap-3 overflow-hidden rounded-lg px-1 py-1.5">
          <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[var(--color-surface-3)] text-xs font-semibold text-[var(--color-accent)]">
            {inicial}
          </span>
          <div className="min-w-0 flex-1 opacity-0 transition-opacity duration-200 group-hover/sidebar:opacity-100">
            <p className="truncate text-xs font-medium text-[var(--color-foreground)]">
              {user?.nome || "Usuário"}
            </p>
            <p className="truncate text-[11px] text-[var(--color-muted-2)]">{user?.email}</p>
          </div>
          <button
            onClick={logout}
            title="Sair"
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-[var(--color-muted)] opacity-0 transition-all duration-200 hover:bg-[var(--color-risk-high-soft)] hover:text-[var(--color-risk-high)] group-hover/sidebar:opacity-100"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>
    </aside>
  )
}
