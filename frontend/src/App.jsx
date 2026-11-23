import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import { AppShell } from './layouts/AppShell'
import { Assistant } from './pages/Assistant'
import { DocumentDetail } from './pages/DocumentDetail'
import { Compare } from './pages/Compare'
import { Compliance } from './pages/Compliance'
import { Dashboard } from './pages/Dashboard'
import { Documents } from './pages/Documents'
import { Login } from './pages/Login'
import { Research } from './pages/Research'

function RequireAuth({ children }) {
  const { token, ready } = useAuth()
  if (!ready) {
    return <p className="p-8 text-sm text-muted">Checking your session…</p>
  }
  if (!token) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        element={
          <RequireAuth>
            <AppShell />
          </RequireAuth>
        }
      >
        <Route path="/" element={<Navigate to="/documents" replace />} />
        <Route path="/documents" element={<Documents />} />
        <Route path="/documents/:id" element={<DocumentDetail />} />
        <Route path="/assistant" element={<Assistant />} />
        <Route path="/compare" element={<Compare />} />
        <Route path="/research" element={<Research />} />
        <Route path="/compliance" element={<Compliance />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
