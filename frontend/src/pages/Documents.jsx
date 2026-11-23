import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, errorMessage } from '../services/api'

const AUTHORITIES = ['', 'RBI', 'SEBI', 'NPCI', 'OTHER']

export function Documents() {
  const [documents, setDocuments] = useState([])
  const [query, setQuery] = useState('')
  const [authority, setAuthority] = useState('')
  const [title, setTitle] = useState('')
  const [uploadAuthority, setUploadAuthority] = useState('RBI')
  const [category, setCategory] = useState('')
  const [file, setFile] = useState(null)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)

  async function load(nextQuery = query, nextAuthority = authority) {
    setLoading(true)
    setError('')
    try {
      const params = {}
      if (nextQuery.trim()) params.q = nextQuery.trim()
      if (nextAuthority) params.authority = nextAuthority
      const response = await api.get('/documents', { params })
      setDocuments(response.data)
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    // The first load uses the empty filters. Search applies later filters on purpose.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function handleSearch(event) {
    event.preventDefault()
    await load(query, authority)
  }

  function handleClear() {
    setQuery('')
    setAuthority('')
    load('', '')
  }

  async function handleUpload(event) {
    event.preventDefault()
    setError('')
    setNotice('')
    if (!file) {
      setError('Choose a PDF to upload.')
      return
    }
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('File must be a PDF.')
      return
    }
    setUploading(true)
    try {
      const body = new FormData()
      body.append('file', file)
      body.append('title', title.trim())
      body.append('authority', uploadAuthority)
      body.append('category', category.trim())
      await api.post('/documents/upload', body)
      setTitle('')
      setCategory('')
      setFile(null)
      event.target.reset()
      setNotice('Upload started. Open the document to watch it finish indexing.')
      await load()
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setUploading(false)
    }
  }

  async function handleDelete(document) {
    const confirmed = window.confirm(`Delete “${document.title}”? This removes its chunks.`)
    if (!confirmed) return
    setError('')
    try {
      await api.delete(`/documents/${document.id}`)
      setDocuments((current) => current.filter((item) => item.id !== document.id))
    } catch (err) {
      setError(errorMessage(err))
    }
  }

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="text-3xl font-semibold tracking-tight">Documents</h1>
      <p className="mt-1 text-sm text-muted">Upload a circular, then open it while it indexes.</p>

      <form onSubmit={handleUpload} className="mt-6 rounded-lg border border-line bg-white p-4">
        <div className="grid gap-3 md:grid-cols-2">
          <label className="text-sm font-medium">
            Title
            <input
              required
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              className="mt-1 w-full rounded-lg border border-line px-3 py-2 font-normal"
            />
          </label>
          <label className="text-sm font-medium">
            Authority
            <select
              value={uploadAuthority}
              onChange={(event) => setUploadAuthority(event.target.value)}
              className="mt-1 w-full cursor-pointer rounded-lg border border-line bg-white px-3 py-2 font-normal"
            >
              {AUTHORITIES.filter(Boolean).map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm font-medium">
            Category
            <input
              required
              value={category}
              onChange={(event) => setCategory(event.target.value)}
              placeholder="Circular"
              className="mt-1 w-full rounded-lg border border-line px-3 py-2 font-normal"
            />
          </label>
          <label className="text-sm font-medium">
            PDF
            <input
              required
              type="file"
              accept="application/pdf,.pdf"
              onChange={(event) => setFile(event.target.files?.[0] || null)}
              className="mt-1 w-full cursor-pointer text-sm font-normal"
            />
          </label>
        </div>
        <button
          type="submit"
          disabled={uploading}
          className="mt-4 cursor-pointer rounded-lg bg-teal-deep px-4 py-2 text-sm font-medium text-white transition-opacity duration-150 hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {uploading ? 'Uploading…' : 'Upload'}
        </button>
      </form>

      <form onSubmit={handleSearch} className="mt-4 flex flex-col gap-2 sm:flex-row">
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search titles"
          aria-label="Search titles"
          className="flex-1 rounded-lg border border-line bg-white px-3 py-2 text-sm"
        />
        <select
          value={authority}
          onChange={(event) => setAuthority(event.target.value)}
          aria-label="Filter by authority"
          className="cursor-pointer rounded-lg border border-line bg-white px-3 py-2 text-sm"
        >
          <option value="">All authorities</option>
          {AUTHORITIES.filter(Boolean).map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
        <button
          type="submit"
          className="cursor-pointer rounded-lg border border-line bg-white px-4 py-2 text-sm hover:bg-bubble"
        >
          Search
        </button>
        <button
          type="button"
          onClick={handleClear}
          className="cursor-pointer rounded-lg px-4 py-2 text-sm text-muted hover:bg-white"
        >
          Clear
        </button>
      </form>

      {error ? (
        <p className="mt-4 text-sm text-teal-deep" role="alert">
          {error}
        </p>
      ) : null}
      {notice ? <p className="mt-4 text-sm">{notice}</p> : null}

      <div className="mt-4 rounded-lg border border-line bg-white">
        {loading ? <p className="px-4 py-6 text-sm text-muted">Loading documents…</p> : null}
        {!loading && documents.length === 0 ? (
          <p className="px-4 py-6 text-sm text-muted">No documents yet. Upload a PDF to start.</p>
        ) : null}
        <ul>
          {documents.map((document) => (
            <li
              key={document.id}
              className="flex flex-col gap-3 border-b border-line px-4 py-3 last:border-b-0 sm:flex-row sm:items-center sm:justify-between"
            >
              <div>
                <p className="font-semibold">{document.title}</p>
                <p className="text-sm text-muted">
                  {document.authority} · {document.category} · {document.status}
                </p>
              </div>
              <div className="flex gap-2">
                <Link
                  to={`/documents/${document.id}`}
                  className="cursor-pointer rounded-lg bg-bubble px-3 py-2 text-sm font-medium"
                >
                  Open
                </Link>
                <button
                  type="button"
                  onClick={() => handleDelete(document)}
                  className="cursor-pointer rounded-lg px-3 py-2 text-sm text-muted hover:bg-mint"
                >
                  Delete
                </button>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
