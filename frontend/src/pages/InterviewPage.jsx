<<<<<<< HEAD
import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Navbar from '../components/Navbar'
import ChatMessage from '../components/ChatMessage'
import ModelSelector from '../components/ModelSelector'
import { useChat } from '../hooks/useChat'
import { useModels } from '../hooks/useModels'
import apiClient from '../api/client'
import { useVoiceToText } from '../hooks/useVoiceToText';

const PROVIDER_LABELS = { openai: 'OpenAI', anthropic: 'Anthropic', google: 'Google' }
const PROVIDER_COLORS = {
  openai: 'bg-green-50 text-green-700 border-green-200',
  anthropic: 'bg-orange-50 text-orange-700 border-orange-200',
  google: 'bg-blue-50 text-blue-700 border-blue-200',
}

export default function InterviewPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const projectId = parseInt(id)

  const [project, setProject] = useState(null)
  const [input, setInput] = useState('')
  const [generating, setGenerating] = useState(false)
  const [showModelModal, setShowModelModal] = useState(false)
  const [pendingModel, setPendingModel] = useState('')
  const [savingModel, setSavingModel] = useState(false)

  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const { models } = useModels()
  const { messages, loading, isSaturated, error, loadHistory, startInterview, sendMessage, resetConversation } =
    useChat(projectId)

  useEffect(() => {
    apiClient.get(`/projects/${projectId}`).then(({ data }) => {
      setProject(data)
      setPendingModel(`${data.model_provider}:${data.model_name}`)
    })
  }, [projectId])

  useEffect(() => {
    loadHistory().then(() => { })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    if (messages.length === 0 && !loading) startInterview()
  }, [messages, loading])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const { isListening, toggleListening } = useVoiceToText((transcript) => {
<<<<<<< HEAD
<<<<<<< HEAD
    setInput((prev) => prev + (prev ? ' ' : '') + transcript);
  });
=======
  setInput((prev) => prev + (prev ? ' ' : '') + transcript);
});
>>>>>>> 1960d1a (add voice to text feature)
=======
    setInput((prev) => prev + (prev ? ' ' : '') + transcript);
  });
>>>>>>> e5ecc7d (InterviewPage navbar stick on top)
  const handleSend = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return
    const text = input
    setInput('')
    await sendMessage(text)
    inputRef.current?.focus()
  }

  const handleGenerateSRS = async () => {
    setGenerating(true)
    try {
      await apiClient.post('/generate-srs', { project_id: projectId })
      navigate(`/project/${projectId}/srs`)
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to generate SRS')
    } finally {
      setGenerating(false)
    }
  }

  const handleReset = async () => {
    if (!window.confirm('Archive this conversation? Previous requirements will remain accessible.')) return
    await resetConversation()
    await startInterview()
  }

  const handleSaveModel = async () => {
    const [provider, modelName] = pendingModel.split(':')
    setSavingModel(true)
    try {
      const { data } = await apiClient.patch(`/projects/${projectId}/model`, {
        model_provider: provider,
        model_name: modelName,
      })
      setProject(data)
      setShowModelModal(false)
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to update model')
    } finally {
      setSavingModel(false)
    }
  }

  const currentModelKey = project ? `${project.model_provider}:${project.model_name}` : ''
  const currentModelName = project && models
    ? models[project.model_provider]?.[project.model_name] || project.model_name
    : ''
  const providerColorClass = project ? (PROVIDER_COLORS[project.model_provider] || 'bg-slate-50 text-slate-700 border-slate-200') : ''

  return (
<<<<<<< HEAD
<<<<<<< HEAD
    <div className="h-screen bg-slate-50 flex flex-col"> {/* Changed min-h-screen to h-screen */}

      {/* --- STICKY HEADER WRAPPER --- */}
      <div className="sticky top-0 z-50 bg-white">
        <Navbar projectName={project?.app_name} backTo="/" backLabel="Dashboard" />

        {/* Model badge bar */}
        {project && (
          <div className="border-b border-slate-100 px-6 py-2 flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs text-slate-500">
              <span>Model:</span>
              <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full border font-medium ${providerColorClass}`}>
                {PROVIDER_LABELS[project.model_provider] || project.model_provider} — {currentModelName}
              </span>
            </div>
            <button
              onClick={() => { setPendingModel(currentModelKey); setShowModelModal(true) }}
              className="text-xs text-brand-600 hover:text-brand-700 font-medium transition-colors"
            >
              Change
            </button>
=======
  <div className="h-screen bg-slate-50 flex flex-col"> {/* Changed min-h-screen to h-screen */}
    
    {/* --- STICKY HEADER WRAPPER --- */}
    <div className="sticky top-0 z-50 bg-white">
      <Navbar projectName={project?.app_name} backTo="/" backLabel="Dashboard" />
=======
    <div className="h-screen bg-slate-50 flex flex-col"> {/* Changed min-h-screen to h-screen */}
>>>>>>> e5ecc7d (InterviewPage navbar stick on top)

      {/* --- STICKY HEADER WRAPPER --- */}
      <div className="sticky top-0 z-50 bg-white">
        <Navbar projectName={project?.app_name} backTo="/" backLabel="Dashboard" />

<<<<<<< HEAD
      {/* SRS Banner */}
      {isSaturated && (
        <div className="bg-green-50 border-b border-green-200 px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2 text-green-800 text-sm">
            <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
            <strong>Information gathering complete.</strong> Ready to generate your SRS document.
>>>>>>> 4a82795 (InterviewPage navbar stick on top)
=======
        {/* Model badge bar */}
        {project && (
          <div className="border-b border-slate-100 px-6 py-2 flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs text-slate-500">
              <span>Model:</span>
              <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full border font-medium ${providerColorClass}`}>
                {PROVIDER_LABELS[project.model_provider] || project.model_provider} — {currentModelName}
              </span>
            </div>
            <button
              onClick={() => { setPendingModel(currentModelKey); setShowModelModal(true) }}
              className="text-xs text-brand-600 hover:text-brand-700 font-medium transition-colors"
            >
              Change
            </button>
>>>>>>> e5ecc7d (InterviewPage navbar stick on top)
          </div>
        )}

        {/* SRS Banner */}
        {isSaturated && (
          <div className="bg-green-50 border-b border-green-200 px-6 py-3 flex items-center justify-between">
            <div className="flex items-center gap-2 text-green-800 text-sm">
              <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> e5ecc7d (InterviewPage navbar stick on top)
              <strong>Information gathering complete.</strong> Ready to generate your SRS document.
            </div>
            <button
              onClick={handleGenerateSRS}
              disabled={generating}
              className="flex items-center gap-2 px-4 py-1.5 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 disabled:opacity-60 transition-colors"
            >
              {generating && (
                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
              )}
              {generating ? 'Generating…' : 'Generate SRS'}
            </button>
<<<<<<< HEAD

          </div>
        )}
      </div>
      {/* --- END STICKY HEADER --- */}
=======
            )}
            {generating ? 'Generating…' : 'Generate SRS'}
          </button>

        </div>
      )}
    </div>
    {/* --- END STICKY HEADER --- */}
>>>>>>> 4a82795 (InterviewPage navbar stick on top)
=======

          </div>
        )}
      </div>
      {/* --- END STICKY HEADER --- */}
>>>>>>> e5ecc7d (InterviewPage navbar stick on top)

      <div className="flex-1 overflow-y-auto px-4 py-6 max-w-3xl mx-auto w-full scrollbar-hide">
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">{error}</div>
        )}
        {messages.map((msg) => <ChatMessage key={msg.id} message={msg} />)}
        {loading && (
          <div className="flex justify-start mb-4">
            <div className="w-8 h-8 rounded-full bg-brand-600 flex items-center justify-center text-white text-xs font-bold mr-2 mt-1">AI</div>
            <div className="bg-white border border-slate-200 rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm">
              <div className="flex space-x-1.5">
                {[0, 150, 300].map((delay) => (
                  <div key={delay} className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: `${delay}ms` }} />
                ))}
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="border-t border-slate-200 bg-white px-4 py-4">
        <div className="max-w-3xl mx-auto">
          <form onSubmit={handleSend} className="flex gap-3 items-end">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(e) } }}
              rows={1}
              placeholder="Type your answer… (Enter to send)"
              className="flex-1 border border-slate-300 rounded-xl px-4 py-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent max-h-32 overflow-y-auto"
              style={{ minHeight: '44px' }}
            />
            {/* MICROPHONE BUTTON */}
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> e5ecc7d (InterviewPage navbar stick on top)
            <button
              type="button"
              onClick={toggleListening}
              className={`p-3 rounded-xl transition-colors flex-shrink-0 ${isListening ? 'bg-red-500 text-white animate-pulse' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
            </button>
<<<<<<< HEAD
=======
  <button
    type="button"
    onClick={toggleListening}
    className={`p-3 rounded-xl transition-colors flex-shrink-0 ${
      isListening ? 'bg-red-500 text-white animate-pulse' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
    }`}
  >
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
    </svg>
  </button>
>>>>>>> 1960d1a (add voice to text feature)
=======
>>>>>>> e5ecc7d (InterviewPage navbar stick on top)
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="p-3 bg-brand-600 text-white rounded-xl hover:bg-brand-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex-shrink-0"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </form>
          <div className="flex items-center justify-between mt-2">
            <p className="text-xs text-slate-400">{messages.length} messages</p>
            <button onClick={handleReset} className="text-xs text-slate-400 hover:text-slate-600 transition-colors">
              Reset conversation
            </button>
          </div>
        </div>
      </div>

      {/* Change Model Modal */}
      {showModelModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-slate-800">Change AI Model</h3>
              <button onClick={() => setShowModelModal(false)} className="text-slate-400 hover:text-slate-600">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <p className="text-sm text-slate-500 mb-4">
              The selected model will be used for all future AI responses in this project.
            </p>
            <ModelSelector value={pendingModel} onChange={setPendingModel} models={models} />
            <div className="flex gap-3 mt-5">
              <button onClick={() => setShowModelModal(false)} className="flex-1 py-2 border border-slate-300 text-slate-700 text-sm font-medium rounded-lg hover:bg-slate-50 transition-colors">
                Cancel
              </button>
              <button
                onClick={handleSaveModel}
                disabled={savingModel || pendingModel === currentModelKey}
                className="flex-1 py-2 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 disabled:opacity-50 transition-colors flex items-center justify-center gap-2"
              >
                {savingModel && <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>}
                Save
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
=======
import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Navbar from '../components/Navbar'
import ChatMessage from '../components/ChatMessage'
import ModelSelector from '../components/ModelSelector'
import { useChat } from '../hooks/useChat'
import { useModels } from '../hooks/useModels'
import apiClient from '../api/client'
import { useVoiceToText } from '../hooks/useVoiceToText';

const PROVIDER_LABELS = { openai: 'OpenAI', anthropic: 'Anthropic', google: 'Google' }
const PROVIDER_COLORS = {
  openai: 'bg-green-50 text-green-700 border-green-200',
  anthropic: 'bg-orange-50 text-orange-700 border-orange-200',
  google: 'bg-blue-50 text-blue-700 border-blue-200',
}

export default function InterviewPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const projectId = parseInt(id)

  const [project, setProject] = useState(null)
  const [input, setInput] = useState('')
  const [generating, setGenerating] = useState(false)
  const [showModelModal, setShowModelModal] = useState(false)
  const [pendingModel, setPendingModel] = useState('')
  const [savingModel, setSavingModel] = useState(false)

  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const { models } = useModels()
  const { messages, loading, isSaturated, error, loadHistory, startInterview, sendMessage, resetConversation } =
    useChat(projectId)

  useEffect(() => {
    apiClient.get(`/projects/${projectId}`).then(({ data }) => {
      setProject(data)
      setPendingModel(`${data.model_provider}:${data.model_name}`)
    })
  }, [projectId])

  useEffect(() => {
    loadHistory().then(() => { })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    if (messages.length === 0 && !loading) startInterview()
  }, [messages, loading])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const { isListening, toggleListening } = useVoiceToText((transcript) => {
    setInput((prev) => prev + (prev ? ' ' : '') + transcript);
  });
  const handleSend = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return
    const text = input
    setInput('')
    await sendMessage(text)
    inputRef.current?.focus()
  }

  const handleGenerateSRS = async () => {
    setGenerating(true)
    try {
      await apiClient.post('/generate-srs', { project_id: projectId })
      navigate(`/project/${projectId}/srs`)
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to generate SRS')
    } finally {
      setGenerating(false)
    }
  }

  const handleReset = async () => {
    if (!window.confirm('Archive this conversation? Previous requirements will remain accessible.')) return
    await resetConversation()
    await startInterview()
  }

  const handleSaveModel = async () => {
    const [provider, modelName] = pendingModel.split(':')
    setSavingModel(true)
    try {
      const { data } = await apiClient.patch(`/projects/${projectId}/model`, {
        model_provider: provider,
        model_name: modelName,
      })
      setProject(data)
      setShowModelModal(false)
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to update model')
    } finally {
      setSavingModel(false)
    }
  }

  const currentModelKey = project ? `${project.model_provider}:${project.model_name}` : ''
  const currentModelName = project && models
    ? models[project.model_provider]?.[project.model_name] || project.model_name
    : ''
  const providerColorClass = project ? (PROVIDER_COLORS[project.model_provider] || 'bg-slate-50 text-slate-700 border-slate-200') : ''

  return (
    <div className="h-screen bg-slate-50 flex flex-col"> {/* Changed min-h-screen to h-screen */}

      {/* --- STICKY HEADER WRAPPER --- */}
      <div className="sticky top-0 z-50 bg-white">
        <Navbar projectName={project?.app_name} backTo="/" backLabel="Dashboard" />

        {/* Model badge bar */}
        {project && (
          <div className="border-b border-slate-100 px-6 py-2 flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs text-slate-500">
              <span>Model:</span>
              <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full border font-medium ${providerColorClass}`}>
                {PROVIDER_LABELS[project.model_provider] || project.model_provider} — {currentModelName}
              </span>
            </div>
            <button
              onClick={() => { setPendingModel(currentModelKey); setShowModelModal(true) }}
              className="text-xs text-brand-600 hover:text-brand-700 font-medium transition-colors"
            >
              Change
            </button>
          </div>
        )}

        {/* SRS Banner */}
        {isSaturated && (
          <div className="bg-green-50 border-b border-green-200 px-6 py-3 flex items-center justify-between">
            <div className="flex items-center gap-2 text-green-800 text-sm">
              <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              <strong>Information gathering complete.</strong> Ready to generate your SRS document.
            </div>
            <button
              onClick={handleGenerateSRS}
              disabled={generating}
              className="flex items-center gap-2 px-4 py-1.5 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 disabled:opacity-60 transition-colors"
            >
              {generating && (
                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
              )}
              {generating ? 'Generating…' : 'Generate SRS'}
            </button>

          </div>
        )}
      </div>
      {/* --- END STICKY HEADER --- */}

      <div className="flex-1 overflow-y-auto px-4 py-6 max-w-3xl mx-auto w-full scrollbar-hide">
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">{error}</div>
        )}
        {messages.map((msg) => <ChatMessage key={msg.id} message={msg} />)}
        {loading && (
          <div className="flex justify-start mb-4">
            <div className="w-8 h-8 rounded-full bg-brand-600 flex items-center justify-center text-white text-xs font-bold mr-2 mt-1">AI</div>
            <div className="bg-white border border-slate-200 rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm">
              <div className="flex space-x-1.5">
                {[0, 150, 300].map((delay) => (
                  <div key={delay} className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: `${delay}ms` }} />
                ))}
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="border-t border-slate-200 bg-white px-4 py-4">
        <div className="max-w-3xl mx-auto">
          <form onSubmit={handleSend} className="flex gap-3 items-end">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(e) } }}
              rows={1}
              placeholder="Type your answer… (Enter to send)"
              className="flex-1 border border-slate-300 rounded-xl px-4 py-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent max-h-32 overflow-y-auto"
              style={{ minHeight: '44px' }}
            />
            {/* MICROPHONE BUTTON */}
            <button
              type="button"
              onClick={toggleListening}
              className={`p-3 rounded-xl transition-colors flex-shrink-0 ${isListening ? 'bg-red-500 text-white animate-pulse' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
            </button>
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="p-3 bg-brand-600 text-white rounded-xl hover:bg-brand-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex-shrink-0"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </form>
          <div className="flex items-center justify-between mt-2">
            <p className="text-xs text-slate-400">{messages.length} messages</p>
            <button onClick={handleReset} className="text-xs text-slate-400 hover:text-slate-600 transition-colors">
              Reset conversation
            </button>
          </div>
        </div>
      </div>

      {/* Change Model Modal */}
      {showModelModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-slate-800">Change AI Model</h3>
              <button onClick={() => setShowModelModal(false)} className="text-slate-400 hover:text-slate-600">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <p className="text-sm text-slate-500 mb-4">
              The selected model will be used for all future AI responses in this project.
            </p>
            <ModelSelector value={pendingModel} onChange={setPendingModel} models={models} />
            <div className="flex gap-3 mt-5">
              <button onClick={() => setShowModelModal(false)} className="flex-1 py-2 border border-slate-300 text-slate-700 text-sm font-medium rounded-lg hover:bg-slate-50 transition-colors">
                Cancel
              </button>
              <button
                onClick={handleSaveModel}
                disabled={savingModel || pendingModel === currentModelKey}
                className="flex-1 py-2 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 disabled:opacity-50 transition-colors flex items-center justify-center gap-2"
              >
                {savingModel && <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>}
                Save
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
>>>>>>> 5b97499 (chore: apply .gitignore and remove cached files)
