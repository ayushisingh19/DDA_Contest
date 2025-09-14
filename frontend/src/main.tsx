import React, { useState, useEffect } from 'react'
import ReactDOM from 'react-dom/client'
import { createSubmission, getSubmission, getProblemDetail, getStarterCode } from './api/client'

interface ProblemDetail {
  id: number
  code: string
  title: string
  description: string
  difficulty: string
  constraints: string
  function_name: string
  function_params: string[]
  return_type: string
  starter_code: string
  visible_testcases: Array<{
    test_case_no: number
    stdin: string
    expected_output: string
  }>
  is_solved: boolean
}

function App() {
  // State for submission
  const [code, setCode] = useState('')
  const [problemId, setProblemId] = useState(1)
  const [language, setLanguage] = useState('python')
  const [subId, setSubId] = useState<string | undefined>()
  const [status, setStatus] = useState<any>()

  // State for problem details and starter code
  const [problem, setProblem] = useState<ProblemDetail | null>(null)
  const [loading, setLoading] = useState(false)
  const [useStarterCode, setUseStarterCode] = useState(true)
  const [originalStarterCode, setOriginalStarterCode] = useState('')
  const [error, setError] = useState<string | null>(null)

  // Load problem details when problemId changes
  useEffect(() => {
    loadProblemDetails()
  }, [problemId])

  // Update starter code when language changes
  useEffect(() => {
    if (useStarterCode && problem) {
      updateStarterCodeForLanguage()
    }
  }, [language, useStarterCode])

  async function loadProblemDetails() {
    setLoading(true)
    setError(null)
    try {
      const problemData = await getProblemDetail(problemId, language)
      setProblem(problemData)
      setOriginalStarterCode(problemData.starter_code)
      if (useStarterCode) {
        setCode(problemData.starter_code)
      }
    } catch (err) {
      setError(`Failed to load problem: ${err}`)
      console.error('Error loading problem:', err)
    } finally {
      setLoading(false)
    }
  }

  async function updateStarterCodeForLanguage() {
    if (!problem) return

    try {
      const starterData = await getStarterCode(problemId, language)
      setOriginalStarterCode(starterData.starter_code)
      if (useStarterCode) {
        setCode(starterData.starter_code)
      }
    } catch (err) {
      console.error('Error updating starter code:', err)
    }
  }

  async function submit() {
    if (!code.trim()) {
      alert('Please enter some code before submitting')
      return
    }

    try {
      const res = await createSubmission({ problem_id: Number(problemId), code, language })
      setSubId(res.submission_id)
      setStatus(res)
    } catch (err) {
      alert(`Submission failed: ${err}`)
    }
  }

  async function refresh() {
    if (!subId) return
    try {
      const res = await getSubmission(subId)
      setStatus(res)
    } catch (err) {
      alert(`Failed to refresh: ${err}`)
    }
  }

  function handleUseStarterCodeChange(checked: boolean) {
    setUseStarterCode(checked)
    if (checked && originalStarterCode) {
      setCode(originalStarterCode)
    } else if (!checked) {
      setCode('')
    }
  }

  function restoreStarterCode() {
    if (originalStarterCode) {
      setCode(originalStarterCode)
    }
  }

  return (
    <div style={{ padding: 24, fontFamily: 'sans-serif', maxWidth: 1200, margin: '0 auto' }}>
      <h1>DDT Coding Platform</h1>
      <p>API base: {(import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost'}</p>

      {error && (
        <div
          style={{
            backgroundColor: '#fee',
            border: '1px solid #fcc',
            padding: 12,
            borderRadius: 4,
            marginBottom: 16,
          }}
        >
          <strong>Error:</strong> {error}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginBottom: 24 }}>
        {/* Problem Details Panel */}
        <div style={{ border: '1px solid #ddd', borderRadius: 8, padding: 16 }}>
          <h2>Problem Details</h2>

          <div style={{ marginBottom: 16 }}>
            <label>
              Problem ID:
              <input
                type="number"
                value={problemId}
                onChange={(e) => setProblemId(Number(e.target.value))}
                style={{ marginLeft: 8, padding: 4 }}
              />
            </label>
            <button
              onClick={loadProblemDetails}
              disabled={loading}
              style={{ marginLeft: 8, padding: '4px 8px' }}
            >
              {loading ? 'Loading...' : 'Load Problem'}
            </button>
          </div>

          {problem && (
            <div>
              <h3 style={{ color: '#333', margin: '0 0 8px 0' }}>
                {problem.code}: {problem.title}
              </h3>
              <p
                style={{
                  display: 'inline-block',
                  backgroundColor:
                    problem.difficulty === 'Easy'
                      ? '#d4edda'
                      : problem.difficulty === 'Medium'
                        ? '#fff3cd'
                        : '#f8d7da',
                  color:
                    problem.difficulty === 'Easy'
                      ? '#155724'
                      : problem.difficulty === 'Medium'
                        ? '#856404'
                        : '#721c24',
                  padding: '2px 6px',
                  borderRadius: 4,
                  fontSize: 12,
                  fontWeight: 'bold',
                }}
              >
                {problem.difficulty}
              </p>
              {problem.is_solved && (
                <span
                  style={{
                    marginLeft: 8,
                    backgroundColor: '#d4edda',
                    color: '#155724',
                    padding: '2px 6px',
                    borderRadius: 4,
                    fontSize: 12,
                  }}
                >
                  ✅ Solved
                </span>
              )}

              <div style={{ marginTop: 12 }}>
                <strong>Description:</strong>
                <p style={{ marginTop: 4, whiteSpace: 'pre-wrap' }}>{problem.description}</p>
              </div>

              {problem.constraints && (
                <div style={{ marginTop: 12 }}>
                  <strong>Constraints:</strong>
                  <p style={{ marginTop: 4, whiteSpace: 'pre-wrap' }}>{problem.constraints}</p>
                </div>
              )}

              {problem.visible_testcases.length > 0 && (
                <div style={{ marginTop: 12 }}>
                  <strong>Sample Test Cases:</strong>
                  {problem.visible_testcases.map((tc, idx) => (
                    <div
                      key={idx}
                      style={{
                        marginTop: 8,
                        padding: 8,
                        backgroundColor: '#f8f9fa',
                        borderRadius: 4,
                      }}
                    >
                      <div>
                        <strong>Input:</strong> <code>{tc.stdin}</code>
                      </div>
                      <div>
                        <strong>Output:</strong> <code>{tc.expected_output}</code>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <div style={{ marginTop: 12, fontSize: 14, color: '#666' }}>
                <strong>Function Signature:</strong> {problem.function_name}(
                {problem.function_params.join(', ')}) → {problem.return_type}
              </div>
            </div>
          )}
        </div>

        {/* Code Submission Panel */}
        <div style={{ border: '1px solid #ddd', borderRadius: 8, padding: 16 }}>
          <h2>Code Submission</h2>

          <div style={{ marginBottom: 16 }}>
            <label>
              Language:
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                style={{ marginLeft: 8, padding: 4 }}
              >
                <option value="python">Python</option>
                <option value="java">Java</option>
                <option value="cpp">C++</option>
                <option value="csharp">C#</option>
                <option value="javascript">JavaScript</option>
                <option value="typescript">TypeScript</option>
              </select>
            </label>
          </div>

          {/* Starter Code Controls */}
          <div
            style={{ marginBottom: 16, padding: 12, backgroundColor: '#f8f9fa', borderRadius: 4 }}
          >
            <label style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
              <input
                type="checkbox"
                checked={useStarterCode}
                onChange={(e) => handleUseStarterCodeChange(e.target.checked)}
                style={{ marginRight: 8 }}
              />
              Use starter code template
            </label>

            {useStarterCode && (
              <button
                onClick={restoreStarterCode}
                style={{
                  padding: '4px 8px',
                  fontSize: 12,
                  backgroundColor: '#6c757d',
                  color: 'white',
                  border: 'none',
                  borderRadius: 4,
                  cursor: 'pointer',
                }}
              >
                Reset to Starter Code
              </button>
            )}
          </div>

          {/* Code Editor */}
          <div style={{ marginBottom: 16 }}>
            <textarea
              style={{
                width: '100%',
                height: 300,
                fontFamily: 'Monaco, Consolas, "Courier New", monospace',
                fontSize: 14,
                padding: 12,
                border: '1px solid #ddd',
                borderRadius: 4,
                resize: 'vertical',
              }}
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder={useStarterCode ? 'Loading starter code...' : 'Write your code here...'}
            />
          </div>

          {/* Submission Actions */}
          <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
            <button
              onClick={submit}
              disabled={!code.trim()}
              style={{
                padding: '8px 16px',
                backgroundColor: '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: 4,
                cursor: code.trim() ? 'pointer' : 'not-allowed',
                opacity: code.trim() ? 1 : 0.6,
              }}
            >
              Submit Solution
            </button>

            <button
              onClick={refresh}
              disabled={!subId}
              style={{
                padding: '8px 16px',
                backgroundColor: '#007bff',
                color: 'white',
                border: 'none',
                borderRadius: 4,
                cursor: subId ? 'pointer' : 'not-allowed',
                opacity: subId ? 1 : 0.6,
              }}
            >
              Refresh Status
            </button>
          </div>

          {/* Submission Status */}
          {(subId || status) && (
            <div style={{ marginTop: 16 }}>
              <h3>Submission Status</h3>
              <div
                style={{
                  padding: 12,
                  backgroundColor: '#f8f9fa',
                  borderRadius: 4,
                  border: '1px solid #ddd',
                  maxHeight: 300,
                  overflowY: 'auto',
                }}
              >
                <pre style={{ margin: 0, fontSize: 12 }}>
                  {JSON.stringify({ subId, status }, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

ReactDOM.createRoot(document.getElementById('root')!).render(<App />)
