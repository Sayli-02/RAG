import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api, errorMessage } from '../services/api'

export function DocumentDetail() {
  const { id } = useParams()
  const [document, setDocument] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let timer
    let cancelled = false

    async function load() {
      try {
        const response = await api.get(`/documents/${id}`)
        if (cancelled) return
        setDocument(response.data)
        setError('')
        if (response.data.status === 'processing' || response.data.status === 'uploaded') {
          timer = setTimeout(load, 2000)
        }
      } catch (err) {
        if (!cancelled) setError(errorMessage(err))
      }
    }

    load()
    return () => {
      cancelled = true
      clearTimeout(timer)
    }
  }, [id])

  return (
    <div className="mx-auto max-w-3xl">
      <Link to="/documents" className="text-sm text-muted hover:underline">
        Back to documents
      </Link>
      {error ? (
        <p className="mt-4 text-sm text-teal-deep" role="alert">
          {error}
        </p>
      ) : null}
      {!document && !error ? <p className="mt-6 text-sm text-muted">Loading document…</p> : null}
      {document ? (
        <>
          <h1 className="mt-3 text-3xl font-semibold tracking-tight">{document.title}</h1>
          <p className="mt-1 text-sm text-muted">
            {document.authority} · {document.category} · {document.status}
          </p>
          {document.error_message ? (
            <p className="mt-4 text-sm text-teal-deep" role="alert">
              {document.error_message}
            </p>
          ) : null}
          {document.status === 'processing' ? (
            <p className="mt-4 text-sm">Indexing the PDF. This page refreshes on its own.</p>
          ) : null}
          <h2 className="mt-8 text-lg font-semibold">Chunks</h2>
          {document.chunks.length === 0 ? (
            <p className="mt-2 text-sm text-muted">No chunks yet.</p>
          ) : (
            <ul className="mt-3 space-y-3">
              {document.chunks.map((chunk) => (
                <li key={chunk.id} className="rounded-lg border border-line bg-white px-4 py-3">
                  <p className="text-sm text-muted">
                    Page {chunk.page_number ?? 'unknown'}
                    {chunk.metadata?.section_heading ? ` · ${chunk.metadata.section_heading}` : ''}
                  </p>
                  <p className="mt-2 text-sm">{chunk.chunk_text}</p>
                </li>
              ))}
            </ul>
          )}
        </>
      ) : null}
    </div>
  )
}
