import { useEffect, useState } from 'react'
import { CitationCard } from '../components/assistant/CitationCard'
import { api, errorMessage } from '../services/api'

export function Research() {
  const [documents, setDocuments] = useState([])
  const [selected, setSelected] = useState([])
  const [queries, setQueries] = useState([])
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState(null)
  const [error, setError] = useState('')
  const [pending, setPending] = useState(false)

  useEffect(() => {
    Promise.all([api.get('/documents', { params: { status: 'indexed' } }), api.get('/research/queries')])
      .then(([documentsResponse, queriesResponse]) => {
        setDocuments(documentsResponse.data)
        setQueries(queriesResponse.data)
      })
      .catch((err) => setError(errorMessage(err)))
  }, [])

  function toggle(id) {
    setSelected((current) => (current.includes(id) ? current.filter((item) => item !== id) : [...current, id]))
  }

  async function handleAsk(event) {
    event.preventDefault()
    setError('')
    setPending(true)
    try {
      const response = await api.post('/research/cross-document', {
        question: question.trim(),
        document_ids: selected,
      })
      setAnswer(response.data)
      const listed = await api.get('/research/queries')
      setQueries(listed.data)
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setPending(false)
    }
  }

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="text-3xl font-semibold tracking-tight">Research</h1>
      <p className="mt-1 text-sm text-muted">Ask one question across the documents you select.</p>

      <form onSubmit={handleAsk} className="mt-6 rounded-lg border border-line bg-white p-4">
        <fieldset>
          <legend className="text-sm font-medium">Documents</legend>
          {documents.length === 0 ? <p className="mt-2 text-sm text-muted">No indexed documents yet.</p> : null}
          <ul className="mt-2 space-y-2">
            {documents.map((document) => (
              <li key={document.id}>
                <label className="flex cursor-pointer items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={selected.includes(document.id)}
                    onChange={() => toggle(document.id)}
                  />
                  <span>
                    {document.title} <span className="text-muted">{document.authority}</span>
                  </span>
                </label>
              </li>
            ))}
          </ul>
        </fieldset>

        <label className="mt-4 block text-sm font-medium" htmlFor="research-question">
          Question
          <textarea
            id="research-question"
            required
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            rows={3}
            className="mt-1 w-full rounded-lg border border-line px-3 py-2 font-normal"
          />
        </label>
        <button
          type="submit"
          disabled={pending || selected.length < 2 || !question.trim()}
          className="mt-3 cursor-pointer rounded-lg bg-teal-deep px-4 py-2 text-sm font-medium text-white hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {pending ? 'Reading…' : 'Ask'}
        </button>
      </form>

      {queries.length > 0 ? (
        <div className="mt-4 flex flex-wrap gap-2">
          {queries.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => setQuestion(item.query_text)}
              className="cursor-pointer rounded-lg bg-white px-3 py-1.5 text-left text-sm hover:bg-bubble"
            >
              {item.query_text}
            </button>
          ))}
        </div>
      ) : null}

      {error ? (
        <p className="mt-4 text-sm text-teal-deep" role="alert">
          {error}
        </p>
      ) : null}

      {answer ? (
        <div className="mt-6 space-y-3">
          <p className="text-sm">{answer.answer}</p>
          {answer.citations.map((citation, index) => (
            <CitationCard key={`${citation.document_title}-${index}`} citation={citation} />
          ))}
        </div>
      ) : null}
    </div>
  )
}
