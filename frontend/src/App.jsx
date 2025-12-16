import { useState, useCallback, useMemo, useEffect } from 'react'
import Upload from './components/Upload'
import Chat from './components/Chat'
import Sources from './components/Sources'

// API base URL: must be provided via VITE_API_URL in production.
// Fallbacks help local dev but avoid 404 in production static hosting.
const resolveApiBase = () => {
  if (import.meta.env.VITE_API_URL) return import.meta.env.VITE_API_URL
  if (window?.__API_BASE) return window.__API_BASE
  // Dev fallback to Vite proxy
  return '/api'
}

function App() {
  const [documents, setDocuments] = useState([])
  const [response, setResponse] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [stats, setStats] = useState({ total_chunks: 0 })
  const [apiBase, setApiBase] = useState(resolveApiBase())

  // Warn if API base is missing to avoid silent 404s in production
  const apiConfigured = useMemo(() => !!apiBase && apiBase !== '/api', [apiBase])

  useEffect(() => {
    if (!apiConfigured) {
      console.warn('VITE_API_URL is not set; falling back to /api (dev proxy). Set VITE_API_URL in production.')
      setError('API URL not configured. Set VITE_API_URL to your backend URL.')
    }
  }, [apiConfigured])

  // Fetch stats
  const fetchStats = useCallback(async () => {
    try {
      const res = await fetch(`${apiBase}/stats`)
      if (res.ok) {
        const data = await res.json()
        setStats(data)
      }
    } catch (err) {
      console.error('Failed to fetch stats:', err)
    }
  }, [])

  // Handle document upload
  const handleUpload = async (file) => {
    setIsLoading(true)
    setError(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch(`${apiBase}/upload`, {
        method: 'POST',
        body: formData
      })

      const data = await res.json()

      if (res.ok && data.success) {
        setDocuments(prev => [...prev, {
          filename: data.filename,
          chunks: data.chunks_created
        }])
        setStats(prev => ({
          ...prev,
          total_chunks: data.total_chunks_in_store
        }))
        return { success: true }
      } else {
        throw new Error(data.detail || data.error || 'Upload failed')
      }
    } catch (err) {
      setError(err.message)
      return { success: false, error: err.message }
    } finally {
      setIsLoading(false)
    }
  }

  // Handle question
  const handleAsk = async (question) => {
    setIsLoading(true)
    setError(null)
    setResponse(null)

    try {
      const res = await fetch(`${apiBase}/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ question, top_k: 3 })
      })

      const data = await res.json()

      if (res.ok) {
        if (data.success) {
          setResponse(data)
        } else {
          setError(data.error || 'Failed to get answer')
        }
      } else {
        throw new Error(data.detail || 'Request failed')
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  // Handle clear
  const handleClear = async () => {
    try {
      const res = await fetch(`${apiBase}/clear`, {
        method: 'POST'
      })

      if (res.ok) {
        setDocuments([])
        setResponse(null)
        setStats({ total_chunks: 0 })
        setError(null)
      }
    } catch (err) {
      setError('Failed to clear documents')
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>📚 RAG Demo</h1>
        <p>Upload documents and ask questions with AI-powered answers</p>
      </header>

      {/* Stats Bar */}
      <div className="stats-bar">
        <div className="stat-item">
          <span>📄 Documents:</span>
          <span className="stat-value">{documents.length}</span>
        </div>
        <div className="stat-item">
          <span>🧩 Chunks:</span>
          <span className="stat-value">{stats.total_chunks}</span>
        </div>
        {documents.length > 0 && (
          <button className="clear-button" onClick={handleClear}>
            🗑️ Clear All
          </button>
        )}
      </div>

      {/* Upload Section */}
      <Upload 
        onUpload={handleUpload} 
        documents={documents}
        isLoading={isLoading}
      />

      {/* Chat Section */}
      <Chat 
        onAsk={handleAsk}
        response={response}
        isLoading={isLoading}
        disabled={documents.length === 0}
        error={error}
      />

      {/* Sources Section */}
      {response?.citations && response.citations.length > 0 && (
        <Sources citations={response.citations} />
      )}
    </div>
  )
}

export default App
