import { useEffect, useState } from 'react'
import { api, errorMessage } from '../services/api'

function Count({ label, value }) {
  return (
    <section className="rounded-lg border border-line bg-white p-4">
      <p className="text-sm text-muted">{label}</p>
      <p className="mt-1 text-2xl font-semibold">{value}</p>
    </section>
  )
}

function formatWhen(value) {
  if (!value) return ''
  return new Date(value).toLocaleString()
}

export function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [evaluation, setEvaluation] = useState(null)
  const [error, setError] = useState('')
  const [pending, setPending] = useState(false)

  async function load() {
    const [summaryResponse, evaluationResponse] = await Promise.all([
      api.get('/analytics/summary'),
      api.get('/evaluation/latest'),
    ])
    setSummary(summaryResponse.data)
    setEvaluation(evaluationResponse.data)
  }

  useEffect(() => {
    load().catch((err) => setError(errorMessage(err)))
  }, [])

  async function handleRun() {
    setError('')
    setPending(true)
    try {
      const response = await api.post('/evaluation/run')
      setEvaluation(response.data)
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setPending(false)
    }
  }

  const metrics = evaluation?.metrics_json

  return (
    <div className="mx-auto max-w-5xl">
      <h1 className="text-3xl font-semibold tracking-tight">Dashboard</h1>
      <p className="mt-1 text-sm text-muted">Your library, reviews, and the latest retrieval scores.</p>

      {error ? (
        <p className="mt-4 text-sm text-teal-deep" role="alert">
          {error}
        </p>
      ) : null}

      {summary ? (
        <>
          <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <Count label="Documents" value={summary.documents_total} />
            <Count label="Indexed" value={summary.documents_indexed} />
            <Count label="Pending review" value={summary.review.pending_review} />
            <Count label="Reviewed" value={summary.review.reviewed} />
          </div>

          <div className="mt-4 grid gap-4 lg:grid-cols-2">
            <section className="rounded-lg border border-line bg-white p-4">
              <h2 className="text-lg font-semibold">By authority</h2>
              {Object.keys(summary.by_authority).length === 0 ? <p className="mt-2 text-sm text-muted">None yet.</p> : null}
              <ul className="mt-2 space-y-1 text-sm">
                {Object.entries(summary.by_authority).map(([authority, count]) => (
                  <li key={authority}>
                    {authority}: {count}
                  </li>
                ))}
              </ul>
              <h2 className="mt-4 text-lg font-semibold">By status</h2>
              <ul className="mt-2 space-y-1 text-sm">
                {Object.entries(summary.by_status).map(([status, count]) => (
                  <li key={status}>
                    {status}: {count}
                  </li>
                ))}
              </ul>
            </section>

            <section className="rounded-lg border border-line bg-white p-4">
              <h2 className="text-lg font-semibold">Recent documents</h2>
              {summary.recent_documents.length === 0 ? <p className="mt-2 text-sm text-muted">None yet.</p> : null}
              <ul className="mt-2 space-y-2 text-sm">
                {summary.recent_documents.map((document) => (
                  <li key={document.id}>
                    {document.title} <span className="text-muted">{document.status}</span>
                    <span className="block text-muted">{formatWhen(document.updated_at)}</span>
                  </li>
                ))}
              </ul>
            </section>

            <section className="rounded-lg border border-line bg-white p-4">
              <h2 className="text-lg font-semibold">Frequent questions</h2>
              {summary.frequent_queries.length === 0 ? <p className="mt-2 text-sm text-muted">None yet.</p> : null}
              <ul className="mt-2 space-y-1 text-sm">
                {summary.frequent_queries.map((item) => (
                  <li key={item.query_text}>
                    {item.query_text} <span className="text-muted">× {item.count}</span>
                  </li>
                ))}
              </ul>
            </section>

            <section className="rounded-lg border border-line bg-white p-4">
              <h2 className="text-lg font-semibold">Recent comparisons</h2>
              {summary.recent_comparisons.length === 0 ? <p className="mt-2 text-sm text-muted">None yet.</p> : null}
              <ul className="mt-2 space-y-2 text-sm">
                {summary.recent_comparisons.map((report) => (
                  <li key={report.id}>
                    {report.document_a_title} → {report.document_b_title}
                    <span className="block text-muted">{report.summary}</span>
                  </li>
                ))}
              </ul>
            </section>
          </div>
        </>
      ) : null}

      <section className="mt-4 rounded-lg border border-line bg-white p-4">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-lg font-semibold">Retrieval scores</h2>
            <p className="mt-1 text-sm text-muted">
              Three sample questions look for pages 3, 5, and 2. Scores stay at zero until your indexed text contains those pages. Faithfulness is the share of answer words found in the retrieved text, and it runs only when a Gemini key is set.
            </p>
          </div>
          <button
            type="button"
            onClick={handleRun}
            disabled={pending}
            className="cursor-pointer rounded-lg bg-teal-deep px-4 py-2 text-sm font-medium text-white hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {pending ? 'Scoring…' : 'Run scores'}
          </button>
        </div>
        {metrics ? (
          <ul className="mt-4 space-y-1 text-sm">
            <li>Hybrid recall@{metrics.k}: {metrics.hybrid.recall_at_k.toFixed(2)}, MRR {metrics.hybrid.mrr.toFixed(2)}</li>
            <li>Vector recall@{metrics.k}: {metrics.vector.recall_at_k.toFixed(2)}, MRR {metrics.vector.mrr.toFixed(2)}</li>
            <li>BM25 recall@{metrics.k}: {metrics.bm25.recall_at_k.toFixed(2)}, MRR {metrics.bm25.mrr.toFixed(2)}</li>
            <li>Faithfulness: {metrics.faithfulness == null ? 'not run' : metrics.faithfulness.toFixed(2)}</li>
          </ul>
        ) : (
          <p className="mt-4 text-sm text-muted">No score run yet.</p>
        )}
      </section>
    </div>
  )
}
