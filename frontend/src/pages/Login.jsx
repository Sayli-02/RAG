import { useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { api, errorMessage } from '../services/api'

export function Login() {
  const { token, login } = useAuth()
  const navigate = useNavigate()
  const [mode, setMode] = useState('login')
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [pending, setPending] = useState(false)

  if (token) return <Navigate to="/documents" replace />

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    if (mode === 'register' && password.length < 8) {
      setError('Use at least 8 characters for the password.')
      return
    }
    setPending(true)
    try {
      if (mode === 'register') {
        await api.post('/auth/register', { name, email, password })
      }
      const body = new URLSearchParams()
      body.set('username', email)
      body.set('password', password)
      const response = await api.post('/auth/login', body)
      login(response.data.access_token)
      navigate('/documents')
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setPending(false)
    }
  }

  const isRegister = mode === 'register'

  return (
    <div className="flex min-h-screen items-center justify-center bg-mint px-4 text-ink">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md rounded-lg border border-line bg-white p-6"
      >
        <h1 className="text-2xl font-semibold tracking-tight">FinScope</h1>
        <p className="mt-1 text-sm text-muted">
          {isRegister ? 'Create an account to upload circulars.' : 'Log in to your library.'}
        </p>

        {isRegister ? (
          <label className="mt-6 block text-sm font-medium">
            Name
            <input
              required
              value={name}
              onChange={(event) => setName(event.target.value)}
              className="mt-1 w-full rounded-lg border border-line px-3 py-2 font-normal"
              autoComplete="name"
            />
          </label>
        ) : null}

        <label className="mt-4 block text-sm font-medium">
          Email
          <input
            required
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="mt-1 w-full rounded-lg border border-line px-3 py-2 font-normal"
            autoComplete="email"
          />
        </label>

        <label className="mt-4 block text-sm font-medium">
          Password
          <input
            required
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="mt-1 w-full rounded-lg border border-line px-3 py-2 font-normal"
            autoComplete={isRegister ? 'new-password' : 'current-password'}
          />
        </label>

        {error ? (
          <p className="mt-4 text-sm text-teal-deep" role="alert">
            {error}
          </p>
        ) : null}

        <button
          type="submit"
          disabled={pending}
          className="mt-6 w-full cursor-pointer rounded-lg bg-teal-deep px-4 py-2 text-sm font-medium text-white transition-opacity duration-150 hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {pending ? 'Please wait…' : isRegister ? 'Create account' : 'Log in'}
        </button>

        <button
          type="button"
          onClick={() => {
            setMode(isRegister ? 'login' : 'register')
            setError('')
          }}
          className="mt-3 w-full cursor-pointer rounded-lg px-4 py-2 text-sm text-muted hover:bg-mint"
        >
          {isRegister ? 'Already registered? Log in' : 'Need an account? Create one'}
        </button>
      </form>
    </div>
  )
}
