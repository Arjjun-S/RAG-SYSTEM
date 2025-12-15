import { useState, useRef } from 'react'

function Upload({ onUpload, documents, isLoading }) {
  const [isDragging, setIsDragging] = useState(false)
  const [uploadStatus, setUploadStatus] = useState(null)
  const fileInputRef = useRef(null)

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = async (e) => {
    e.preventDefault()
    setIsDragging(false)
    
    const files = e.dataTransfer.files
    if (files.length > 0) {
      await processFile(files[0])
    }
  }

  const handleFileSelect = async (e) => {
    const files = e.target.files
    if (files.length > 0) {
      await processFile(files[0])
    }
    // Reset input
    e.target.value = ''
  }

  const processFile = async (file) => {
    // Validate file type
    const validTypes = ['.pdf', '.txt']
    const fileExt = file.name.toLowerCase().slice(file.name.lastIndexOf('.'))
    
    if (!validTypes.includes(fileExt)) {
      setUploadStatus({ type: 'error', message: 'Only PDF and TXT files are supported' })
      return
    }

    // Validate file size (5MB limit)
    if (file.size > 5 * 1024 * 1024) {
      setUploadStatus({ type: 'error', message: 'File too large. Maximum size is 5MB.' })
      return
    }

    setUploadStatus({ type: 'loading', message: `Uploading ${file.name}...` })

    const result = await onUpload(file)

    if (result.success) {
      setUploadStatus({ type: 'success', message: `${file.name} uploaded successfully!` })
      // Clear status after 3 seconds
      setTimeout(() => setUploadStatus(null), 3000)
    } else {
      setUploadStatus({ type: 'error', message: result.error || 'Upload failed' })
    }
  }

  const handleClick = () => {
    fileInputRef.current?.click()
  }

  return (
    <div className="card">
      <h2 className="card-title">📤 Upload Documents</h2>
      
      <div 
        className={`upload-zone ${isDragging ? 'dragging' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <input 
          type="file"
          ref={fileInputRef}
          onChange={handleFileSelect}
          accept=".pdf,.txt"
          disabled={isLoading}
        />
        <div className="upload-icon">📁</div>
        <p className="upload-text">
          {isLoading ? 'Processing...' : 'Drop files here or click to upload'}
        </p>
        <p className="upload-hint">Supports PDF and TXT files (max 5MB)</p>
      </div>

      {/* Upload Status */}
      {uploadStatus && (
        <div style={{ marginTop: '1rem', textAlign: 'center' }}>
          <span className={`status-badge ${uploadStatus.type}`}>
            {uploadStatus.type === 'loading' && '⏳'}
            {uploadStatus.type === 'success' && '✅'}
            {uploadStatus.type === 'error' && '❌'}
            {uploadStatus.message}
          </span>
        </div>
      )}

      {/* Document List */}
      {documents.length > 0 && (
        <div className="document-list">
          <h3 style={{ fontSize: '0.9rem', marginBottom: '0.75rem', color: 'var(--text-secondary)' }}>
            Uploaded Documents
          </h3>
          {documents.map((doc, index) => (
            <div key={index} className="document-item">
              <div className="document-info">
                <span>{doc.filename.endsWith('.pdf') ? '📄' : '📝'}</span>
                <span>{doc.filename}</span>
              </div>
              <span className="chunk-count">{doc.chunks} chunks</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default Upload
