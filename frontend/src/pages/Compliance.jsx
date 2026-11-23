import { useEffect, useState } from 'react'
import { api, errorMessage } from '../services/api'

const STATUS_LABELS = {
  pending_review: 'Pending review',
  reviewed: 'Reviewed',
  not_applicable: 'Not applicable',
}

export function Compliance() {
  const [documents, setDocuments] = useState([])
  const [documentId, setDocumentId] = useState('')
  const [checklists, setChecklists] = useState([])
  const [checklist, setChecklist] = useState(null)
  const [notes, setNotes] = useState({})
  const [error, setError] = useState('')
  const [pending, setPending] = useState(false)

  async function loadLists() {
    const [documentsResponse, checklistsResponse] = await Promise.all([
      api.get('/documents', { params: { status: 'indexed' } }),
      api.get('/compliance/checklists'),
    ])
    setDocuments(documentsResponse.data)
    setChecklists(checklistsResponse.data)
  }

  useEffect(() => {
    loadLists().catch((err) => setError(errorMessage(err)))
  }, [])

  async function openChecklist(id) {
    setError('')
    const response = await api.get(`/compliance/checklists/${id}`)
    setChecklist(response.data)
    const nextNotes = {}
    response.data.requirements.forEach((item) => {
      nextNotes[item.id] = item.reviewer_notes || ''
    })
    setNotes(nextNotes)
  }

  async function handleExtract(event) {
    event.preventDefault()
    setError('')
    setPending(true)
    try {
      const response = await api.post('/compliance/extract', { document_id: Number(documentId) })
      setChecklist(response.data)
      const nextNotes = {}
      response.data.requirements.forEach((item) => {
        nextNotes[item.id] = item.reviewer_notes || ''
      })
      setNotes(nextNotes)
      await loadLists()
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setPending(false)
    }
  }

  async function saveReview(requirement, status) {
    setError('')
    try {
      const response = await api.patch(`/compliance/requirements/${requirement.id}`, {
        status,
        reviewer_notes: notes[requirement.id] || '',
      })
      setChecklist((current) => ({
        ...current,
        requirements: current.requirements.map((item) => (item.id === requirement.id ? response.data : item)),
      }))
    } catch (err) {
      setError(errorMessage(err))
    }
  }

  async function exportCsv() {
    if (!checklist) return
    setError('')
    try {
      const response = await api.get(`/compliance/checklists/${checklist.id}/export`, { responseType: 'blob' })
      const url = URL.createObjectURL(response.data)
      const link = document.createElement('a')
      link.href = url
      link.download = `checklist-${checklist.id}.csv`
      link.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      setError(errorMessage(err))
    }
  }

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="text-3xl font-semibold tracking-tight">Compliance</h1>
      <p className="mt-1 text-sm text-muted">Extract requirements for review. This is not legal advice.</p>

      <form onSubmit={handleExtract} className="mt-6 flex flex-col gap-3 rounded-lg border border-line bg-white p-4 md:flex-row md:items-end">
        <label className="flex-1 text-sm font-medium">
          Indexed document
          <select
            required
            value={documentId}
            onChange={(event) => setDocumentId(event.target.value)}
            className="mt-1 w-full cursor-pointer rounded-lg border border-line bg-white px-3 py-2 font-normal"
          >
            <option value="">Choose</option>
            {documents.map((document) => (
              <option key={document.id} value={document.id}>
                {document.title}
              </option>
            ))}
          </select>
        </label>
        <button
          type="submit"
          disabled={pending || !documentId}
          className="cursor-pointer rounded-lg bg-teal-deep px-4 py-2 text-sm font-medium text-white hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {pending ? 'Extracting…' : 'Extract'}
        </button>
      </form>

      {checklists.length > 0 ? (
        <div className="mt-4 flex flex-wrap gap-2">
          {checklists.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => openChecklist(item.id)}
              className="cursor-pointer rounded-lg bg-white px-3 py-1.5 text-sm hover:bg-bubble"
            >
              {item.title}
            </button>
          ))}
        </div>
      ) : null}

      {error ? (
        <p className="mt-4 text-sm text-teal-deep" role="alert">
          {error}
        </p>
      ) : null}

      {checklist ? (
        <section className="mt-6">
          <div className="flex items-center justify-between gap-3">
            <h2 className="text-lg font-semibold">{checklist.title}</h2>
            <button
              type="button"
              onClick={exportCsv}
              className="cursor-pointer rounded-lg bg-white px-3 py-1.5 text-sm hover:bg-bubble"
            >
              Export CSV
            </button>
          </div>
          {checklist.requirements.length === 0 ? (
            <p className="mt-3 text-sm text-muted">No obligation sentences were found in this document.</p>
          ) : null}
          <ul className="mt-3 space-y-3">
            {checklist.requirements.map((requirement) => (
              <li key={requirement.id} className="rounded-lg border border-line bg-white p-4">
                <p className="text-sm">{requirement.requirement_text}</p>
                <p className="mt-1 text-sm text-muted">
                  {requirement.authority || 'Authority unknown'}
                  {requirement.page_number != null ? ` · Page ${requirement.page_number}` : ''}
                  {requirement.category ? ` · ${requirement.category}` : ''}
                </p>
                <div className="mt-3 flex flex-col gap-2 md:flex-row">
                  <label className="text-sm font-medium">
                    Status
                    <select
                      value={requirement.status}
                      onChange={(event) => saveReview(requirement, event.target.value)}
                      className="mt-1 block cursor-pointer rounded-lg border border-line bg-white px-3 py-2 font-normal"
                    >
                      {Object.entries(STATUS_LABELS).map(([value, label]) => (
                        <option key={value} value={value}>
                          {label}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="flex-1 text-sm font-medium">
                    Notes
                    <input
                      value={notes[requirement.id] || ''}
                      onChange={(event) => setNotes((current) => ({ ...current, [requirement.id]: event.target.value }))}
                      className="mt-1 w-full rounded-lg border border-line px-3 py-2 font-normal"
                    />
                  </label>
                  <button
                    type="button"
                    onClick={() => saveReview(requirement, requirement.status)}
                    className="cursor-pointer self-end rounded-lg bg-white px-3 py-2 text-sm hover:bg-bubble"
                  >
                    Save notes
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </section>
      ) : null}
    </div>
  )
}
