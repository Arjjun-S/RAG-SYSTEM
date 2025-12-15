import { useState } from 'react'

function Chat({ onAsk, response, isLoading, disabled, error }) {
  const [question, setQuestion] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (question.trim() && !isLoading && !disabled) {
      onAsk(question.trim())
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      handleSubmit(e)
    }
  }

  return (
    <div className="card">
      <h2 className="card-title">💬 Ask a Question</h2>
      
      <div className="chat-container">
        <form onSubmit={handleSubmit} className="chat-input-wrapper">
          <input
            type="text"
            className="chat-input"
            placeholder={disabled ? 'Upload a document first...' : 'Ask a question about your documents...'}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading || disabled}
            maxLength={1000}
          />
          <button 
            type="submit" 
            className="send-button"
            disabled={isLoading || disabled || !question.trim()}
          >
            {isLoading ? '...' : 'Ask'}
          </button>
        </form>

        <div className="response-area">
          {isLoading ? (
            <div className="placeholder-text">
              <div className="loading-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <p style={{ marginTop: '0.5rem' }}>Thinking...</p>
            </div>
          ) : error ? (
            <div style={{ textAlign: 'center' }}>
              <span className="status-badge error">❌ {error}</span>
            </div>
          ) : response ? (
            <>
              <div className="response-header">
                <span style={{ fontWeight: '600' }}>Answer</span>
                {response.model_used && (
                  <span className="model-badge">
                    🤖 {response.model_used}
                  </span>
                )}
              </div>
              <div className="response-text">{response.answer}</div>
              {response.context_tokens && (
                <div style={{ marginTop: '1rem', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                  📊 Used {response.chunks_used} chunks ({response.context_tokens} tokens)
                </div>
              )}
            </>
          ) : (
            <div className="placeholder-text">
              {disabled 
                ? '📤 Upload a document to get started'
                : '🔍 Your answer will appear here'}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Chat
