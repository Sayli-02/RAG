export function CitationCard({ citation }) {
  const page = citation.page_number != null ? `Page ${citation.page_number}` : 'Page unknown'
  return (
    <article className="rounded-lg border border-line bg-white px-4 py-3 text-left">
      <div className="flex items-baseline justify-between gap-3">
        <p className="font-semibold">
          {citation.document_title} <span className="font-normal">{citation.authority}</span>
        </p>
        <p className="shrink-0 text-sm text-muted">{page}</p>
      </div>
      {citation.section ? <p className="mt-2 text-sm">{citation.section}</p> : null}
      <p className="mt-2 text-sm italic">{citation.excerpt}</p>
    </article>
  )
}
