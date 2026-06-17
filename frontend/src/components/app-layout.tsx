import { Outlet } from "react-router-dom"
import { Sidebar } from "./sidebar"

export function AppLayout() {
  return (
    <div className="min-h-screen bg-[var(--color-background)]">
      <Sidebar />
      {/* fixed left margin = collapsed sidebar width; sidebar expands as overlay */}
      <div className="ml-[68px] flex min-h-screen flex-col">
        <Outlet />
      </div>
    </div>
  )
}
