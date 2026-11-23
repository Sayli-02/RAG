import { Outlet } from 'react-router-dom'
import { Sidebar } from '../components/common/Sidebar'

export function AppShell() {
  return (
    <div className="min-h-screen bg-mint text-ink md:flex">
      <Sidebar />
      <main className="min-w-0 flex-1 px-4 py-6 md:px-8 md:py-8">
        <Outlet />
      </main>
    </div>
  )
}
