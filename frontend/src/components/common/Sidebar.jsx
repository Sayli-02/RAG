import { ClipboardList, FileText, GitCompare, LayoutDashboard, Library, LogOut, MessageCircle } from 'lucide-react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

const linkClass = ({ isActive }) =>
  `flex cursor-pointer items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors duration-150 ${
    isActive ? 'bg-bubble font-medium' : 'hover:bg-mint'
  }`

export function Sidebar() {
  const { logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <aside className="flex items-center justify-between gap-3 border-b border-line bg-white px-4 py-3 md:min-h-screen md:w-60 md:flex-col md:items-stretch md:justify-start md:border-r md:border-b-0 md:px-4 md:py-6">
      <div>
        <p className="px-3 text-xl font-semibold tracking-tight">FinScope</p>
        <nav className="mt-4 flex flex-wrap gap-2 md:mt-8 md:flex-col" aria-label="Main">
          <NavLink to="/dashboard" className={linkClass}>
            <LayoutDashboard size={18} aria-hidden="true" />
            Dashboard
          </NavLink>
          <NavLink to="/documents" className={linkClass}>
            <FileText size={18} aria-hidden="true" />
            Documents
          </NavLink>
          <NavLink to="/assistant" className={linkClass}>
            <MessageCircle size={18} aria-hidden="true" />
            Assistant
          </NavLink>
          <NavLink to="/compare" className={linkClass}>
            <GitCompare size={18} aria-hidden="true" />
            Compare
          </NavLink>
          <NavLink to="/research" className={linkClass}>
            <Library size={18} aria-hidden="true" />
            Research
          </NavLink>
          <NavLink to="/compliance" className={linkClass}>
            <ClipboardList size={18} aria-hidden="true" />
            Compliance
          </NavLink>
        </nav>
      </div>
      <button
        type="button"
        onClick={handleLogout}
        className="flex cursor-pointer items-center gap-2 rounded-lg px-3 py-2 text-sm text-muted transition-colors duration-150 hover:bg-mint md:mt-auto"
      >
        <LogOut size={18} aria-hidden="true" />
        Log out
      </button>
    </aside>
  )
}
