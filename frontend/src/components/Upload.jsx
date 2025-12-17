import { useState, useRef } from 'react'

function Upload({ onUpload, documents, stats, isLoading, onClear }) {
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
    e.target.value = ''
  }

  const processFile = async (file) => {
    const validTypes = ['.pdf', '.txt']
    const fileExt = file.name.toLowerCase().slice(file.name.lastIndexOf('.'))
    
    if (!validTypes.includes(fileExt)) {
      setUploadStatus({ type: 'error', message: 'Only PDF and TXT files are supported' })
      return
    }

    if (file.size > 5 * 1024 * 1024) {
      setUploadStatus({ type: 'error', message: 'File too large. Maximum size is 5MB.' })
      return
    }

    setUploadStatus({ type: 'loading', message: `Uploading ${file.name}...` })

    const result = await onUpload(file)

    if (result.success) {
      setUploadStatus({ type: 'success', message: `${file.name} uploaded successfully!` })
      setTimeout(() => setUploadStatus(null), 3000)
    } else {
      setUploadStatus({ type: 'error', message: result.error || 'Upload failed' })
    }
  }

  const handleClick = () => {
    fileInputRef.current?.click()
  }

  return (
    <div className="upload-section">
      <h2 className="section-title">Upload Documents</h2>
      
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
        <img src="/folder-icon.svg" alt="Upload" className="upload-icon" />
        <p className="upload-text">
          {isLoading ? 'Processing...' : 'Drop files here or click to upload'}
        </p>
        <p className="upload-hint">Supports PDF and TXT files (max 5MB)</p>
      </div>

      {/* Upload Status */}
      {uploadStatus && (
        <div className={`upload-status ${uploadStatus.type}`}>
          {uploadStatus.message}
        </div>
      )}

      {/* Stats and Clear */}
      <div className="stats-row">
        <span>Documents: {documents.length}</span>
        <span>Chunks: {stats?.total_chunks || 0}</span>
        {documents.length > 0 && (
          <button className="clear-btn" onClick={onClear}>clear all</button>
        )}
      </div>

      {/* Uploaded Documents Box */}
      <div className="uploaded-docs-box">
        <h3 className="uploaded-title">Uploaded Documents</h3>
        <div className="docs-list">
          {documents.length === 0 ? (
            <div className="no-docs">No documents uploaded yet</div>
          ) : (
            documents.map((doc, index) => (
              <div key={index} className="doc-item">
                <span className="doc-name">{doc.filename}</span>
                <span className="doc-chunks">{doc.chunks} chunks</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}

export default Upload
