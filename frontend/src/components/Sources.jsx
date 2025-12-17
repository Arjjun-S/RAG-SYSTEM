function Sources({ citations }) {
  if (!citations || citations.length === 0) {
    return null
  }

  return (
    <div className="sources-section">
      <h2 className="section-title">Sources</h2>
      
      <div className="sources-list">
        {citations.map((citation, index) => (
          <div key={index} className="source-item">
            <div className="source-header">
              <div>
                <span className="source-filename">{citation.filename}</span>
                <span className="source-meta"> - Chunk {citation.chunk_index}</span>
              </div>
              <span className="relevance-score">
                {(citation.relevance_score * 100).toFixed(0)}% match
              </span>
            </div>
            <p className="source-preview">{citation.text_preview}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Sources
