import { useState } from 'react'
import Upload from './components/Upload'
import Chat from './components/Chat'
import Sources from './components/Sources'

// API base URL
const resolveApiBase = () => {
  if (import.meta.env.VITE_API_URL) return import.meta.env.VITE_API_URL
  return '/api'
}

function App() {
  const [documents, setDocuments] = useState([])
  const [response, setResponse] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [stats, setStats] = useState({ total_chunks: 0 })
  const [apiBase] = useState(resolveApiBase())

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
      {/* Header with Logo */}
      <header className="header">
        <img src="/logo.svg" alt="RAG Mini" className="logo" />
      </header>

      {/* Main Content */}
      <main className="main-content">
        {/* Left Side - Upload Section */}
        <section className="left-section">
          <Upload 
            onUpload={handleUpload} 
            documents={documents}
            stats={stats}
            isLoading={isLoading}
            onClear={handleClear}
          />
        </section>

        {/* Right Side - Hero and Chat */}
        <section className="right-section">
          {/* Hero Image with Speech Bubble */}
          <div className="hero-container">
            <div className="speech-bubble">
              <p>Hello people! This is RAG Mini. Upload your docs and run it for less hallucination. This host is free, so please don't upload too many files and overload it!</p>
            </div>
            <img src="/hero.svg" alt="RAG Mini Assistant" className="hero-image" />
          </div>

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
        </section>
      </main>
    </div>
  )
}

export default App
