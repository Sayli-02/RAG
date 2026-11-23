import { useEffect, useState } from 'react'
import { api, errorMessage } from '../services/api'

function Column({ title, items, render }) {
  return (
    <section className="rounded-lg border border-line bg-white p-4">
      <h2 className="text-lg font-semibold">{title}</h2>
      {items.length === 0 ? <p className="mt-2 text-sm text-muted">None.</p> : null}
      <ul className="mt-3 space-y-3">
        {items.map((item, index) => (
          <li key={index} className="text-sm">
            {render(item)}
          </li>
        ))}
      </ul>
    </section>
  )
}

export function Compare() {
  const [documents, setDocuments] = useState([])
  const [leftId, setLeftId] = useState('')
  const [rightId, setRightId] = useState('')
  const [reports, setReports] = useState([])
  const [report, setReport] = useState(null)
  const [error, setError] = useState('')
  const [pending, setPending] = useState(false)

  useEffect(() => {
    Promise.all([api.get('/documents', { params: { status: 'indexed' } }), api.get('/comparison/reports')])
      .then(([documentsResponse, reportsResponse]) => {
        setDocuments(documentsResponse.data)
        setReports(reportsResponse.data)
      })
      .catch((err) => setError(errorMessage(err)))
  }, [])

  async function handleCompare(event) {
    event.preventDefault()
    setError('')
    setPending(true)
    try {
      const response = await api.post('/comparison/compare', {
        document_a_id: Number(leftId),
        document_b_id: Number(rightId),
      })
      setReport(response.data)
      const listed = await api.get('/comparison/reports')
      setReports(listed.data)
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setPending(false)
    }
  }

  async function openReport(id) {
    setError('')
    try {
      const response = await api.get(`/comparison/reports/${id}`)
      setReport(response.data)
    } catch (err) {
      setError(errorMessage(err))
    }
  }

  const diff = report?.report_json

  return (
    <div className="mx-auto max-w-5xl">
      <h1 className="text-3xl font-semibold tracking-tight">Compare</h1>
      <p className="mt-1 text-sm text-muted">Diff the latest version of two indexed documents.</p>

      <form onSubmit={handleCompare} className="mt-6 flex flex-col gap-3 rounded-lg border border-line bg-white p-4 md:flex-row md:items-end">
        <label className="flex-1 text-sm font-medium">
          Older document
          <select
            required
            value={leftId}
            onChange={(event) => setLeftId(event.target.value)}
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
        <label className="flex-1 text-sm font-medium">
          Newer document
          <select
            required
            value={rightId}
            onChange={(event) => setRightId(event.target.value)}
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
          disabled={pending || !leftId || !rightId || leftId === rightId}
          className="cursor-pointer rounded-lg bg-teal-deep px-4 py-2 text-sm font-medium text-white hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {pending ? 'Comparing…' : 'Compare'}
        </button>
      </form>

      {reports.length > 0 ? (
        <div className="mt-4 flex flex-wrap gap-2">
          {reports.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => openReport(item.id)}
              className="cursor-pointer rounded-lg bg-white px-3 py-1.5 text-sm hover:bg-bubble"
            >
              {item.document_a_title} → {item.document_b_title}
            </button>
          ))}
        </div>
      ) : null}

      {error ? (
        <p className="mt-4 text-sm text-teal-deep" role="alert">
          {error}
        </p>
      ) : null}

      {diff ? (
        <>
          <p className="mt-6 text-sm">{report.summary}</p>
          {diff.affected_requirements?.length ? (
            <ul className="mt-2 list-disc pl-5 text-sm">
              {diff.affected_requirements.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          ) : null}
          <div className="mt-4 grid gap-4 lg:grid-cols-3">
            <Column
              title="Removed"
              items={diff.removed}
              render={(item) => (
                <p>
                  <span className="text-muted">Page {item.page ?? 'unknown'}. </span>
                  {item.text}
                </p>
              )}
            />
            <Column
              title="Modified"
              items={diff.modified}
              render={(item) => (
                <div>
                  <p className="text-muted">Page {item.page ?? 'unknown'}</p>
                  <p className="mt-1 line-through">{item.before}</p>
                  <p className="mt-1">{item.after}</p>
                </div>
              )}
            />
            <Column
              title="Added"
              items={diff.added}
              render={(item) => (
                <p>
                  <span className="text-muted">Page {item.page ?? 'unknown'}. </span>
                  {item.text}
                </p>
              )}
            />
          </div>
        </>
      ) : null}
    </div>
  )
}
