import { useEffect, useState } from 'react'
import { CitationCard } from '../components/assistant/CitationCard'
import { api, errorMessage } from '../services/api'

export function Assistant() {
  const [conversations, setConversations] = useState([])
  const [activeId, setActiveId] = useState(null)
  const [messages, setMessages] = useState([])
  const [question, setQuestion] = useState('')
  const [error, setError] = useState('')
  const [pending, setPending] = useState(false)

  async function loadConversations() {
    const response = await api.get('/assistant/conversations')
    setConversations(response.data)
  }

  async function openConversation(id) {
    setActiveId(id)
    setError('')
    const response = await api.get(`/assistant/conversations/${id}`)
    setMessages(response.data.messages)
  }

  useEffect(() => {
    loadConversations().catch((err) => setError(errorMessage(err)))
  }, [])

  function startNew() {
    setActiveId(null)
    setMessages([])
    setQuestion('')
    setError('')
  }

  async function handleAsk(event) {
    event.preventDefault()
    const text = question.trim()
    if (!text) return
    setPending(true)
    setError('')
    setMessages((current) => [...current, { id: `local-${Date.now()}`, role: 'user', content: text, citations: [] }])
    setQuestion('')
    try {
      const payload = { question: text }
      if (activeId) payload.conversation_id = activeId
      const response = await api.post('/assistant/ask', payload)
      const conversationId = response.data.conversation_id
      setActiveId(conversationId)
      const detail = await api.get(`/assistant/conversations/${conversationId}`)
      setMessages(detail.data.messages)
      await loadConversations()
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setPending(false)
    }
  }

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="text-3xl font-semibold tracking-tight">Assistant</h1>
      <p className="mt-1 text-sm text-muted">Ask your indexed circulars.</p>

      <div className="mt-4 flex flex-wrap gap-2">
        <button
          type="button"
          onClick={startNew}
          className="cursor-pointer rounded-lg bg-white px-3 py-1.5 text-sm hover:bg-bubble"
        >
          New question
        </button>
        {conversations.map((conversation) => (
          <button
            key={conversation.id}
            type="button"
            onClick={() => openConversation(conversation.id).catch((err) => setError(errorMessage(err)))}
            className={`cursor-pointer rounded-lg px-3 py-1.5 text-sm ${
              conversation.id === activeId ? 'bg-bubble font-medium' : 'bg-white hover:bg-bubble'
            }`}
          >
            {conversation.title}
          </button>
        ))}
      </div>

      <div className="mt-4 rounded-lg border border-line bg-white p-4">
        <div className="space-y-4">
          {messages.length === 0 ? (
            <p className="text-sm text-muted">Ask a question about a document you have indexed.</p>
          ) : null}
          {messages.map((message) =>
            message.role === 'user' ? (
              <div key={message.id} className="flex justify-end">
                <p className="max-w-[80%] rounded-lg bg-bubble px-3 py-2 text-sm">{message.content}</p>
              </div>
            ) : (
              <div key={message.id} className="space-y-3">
                <p className="text-sm">{message.content}</p>
                {message.citations?.map((citation, index) => (
                  <CitationCard key={`${message.id}-${index}`} citation={citation} />
                ))}
              </div>
            ),
          )}
          {pending ? <p className="text-sm text-muted">Reading your documents…</p> : null}
        </div>

        {error ? (
          <p className="mt-4 text-sm text-teal-deep" role="alert">
            {error}
          </p>
        ) : null}

        <form onSubmit={handleAsk} className="mt-6 flex gap-2 border-t border-line pt-4">
          <label className="sr-only" htmlFor="question">
            Ask a question
          </label>
          <input
            id="question"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ask a question"
            className="min-w-0 flex-1 rounded-lg border border-line px-3 py-2 text-sm"
          />
          <button
            type="submit"
            disabled={pending || !question.trim()}
            className="cursor-pointer rounded-lg bg-teal-deep px-4 py-2 text-sm font-medium text-white transition-opacity duration-150 hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  )
}
