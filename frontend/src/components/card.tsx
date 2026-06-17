import type { ReactNode, HTMLAttributes } from "react"
import { cn } from "@/lib/utils"

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
  /** stagger index for entrance animation */
  index?: number
  hover?: boolean
}

export function Card({ children, className, index, hover, style, ...rest }: CardProps) {
  return (
    <div
      className={cn(
        "rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-5",
        "animate-enter",
        hover &&
          "transition-all duration-200 hover:border-[var(--color-border-strong)] hover:bg-[var(--color-surface-2)]",
        className,
      )}
      style={{
        animationDelay: index !== undefined ? `${index * 60}ms` : undefined,
        ...style,
      }}
      {...rest}
    >
      {children}
    </div>
  )
}

export function CardHeader({
  title,
  subtitle,
  icon,
  action,
}: {
  title: string
  subtitle?: string
  icon?: ReactNode
  action?: ReactNode
}) {
  return (
    <div className="mb-4 flex items-start justify-between gap-4">
      <div className="flex items-center gap-2.5">
        {icon && (
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-[var(--color-accent-soft)] text-[var(--color-accent)]">
            {icon}
          </span>
        )}
        <div>
          <h3 className="text-sm font-semibold tracking-tight text-[var(--color-foreground)]">
            {title}
          </h3>
          {subtitle && <p className="mt-0.5 text-xs text-[var(--color-muted)]">{subtitle}</p>}
        </div>
      </div>
      {action}
    </div>
  )
}
