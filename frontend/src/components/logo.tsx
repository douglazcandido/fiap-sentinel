import { cn } from "@/lib/utils"

interface LogoProps {
  className?: string
  /** size in px for width/height */
  size?: number
  glow?: boolean
}

/**
 * Sentinel logo. The source SVG is black; we invert it to render as a soft
 * light/cyan mark on the dark theme.
 */
export function Logo({ className, size = 36, glow = false }: LogoProps) {
  return (
    <div
      className={cn("relative inline-flex items-center justify-center", className)}
      style={{ width: size, height: size }}
    >
      {glow && (
        <div
          aria-hidden
          className="absolute inset-0 rounded-full blur-xl"
          style={{ background: "rgba(34,211,238,0.35)" }}
        />
      )}
      <img
        src="/icon.svg"
        alt="Sentinel"
        width={size}
        height={size}
        className="relative z-10"
        style={{
          filter: "invert(1) brightness(1.6) sepia(1) saturate(0)",
          opacity: 0.92,
        }}
      />
    </div>
  )
}
