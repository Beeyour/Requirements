import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

import Navbar from '../components/Navbar'
import ChatMessage from '../components/ChatMessage'
import ModelSelector from '../components/ModelSelector'
import { useChat } from '../hooks/useChat'
import { useModels } from '../hooks/useModels'
import apiClient from '../api/client'
import { useVoiceToText } from '../hooks/useVoiceToText'

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

  const { t } = useTranslation()

  const [project, setProject] = useState(null)
  const [input, setInput] = useState('')
  const [generating, setGenerating] = useState(false)
  const [showModelModal, setShowModelModal] = useState(false)
  const [pendingModel, setPendingModel] = useState('')
  const [savingModel, setSavingModel] = useState(false)
  const [sendError, setSendError] = useState(null)

  // New state to manage the availability of diagrams
  const [artifacts, setArtifacts] = useState({
    srs: false,
    useCase: false,
    class: false,
    activity: false
  })

  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const { models } = useModels()
  const { messages, loading, isSaturated, error, loadHistory, startInterview, sendMessage, resetConversation } =
    useChat(projectId)

  useEffect(() => {
    apiClient.get(`/projects/${projectId}`).then(({ data }) => {
      setProject(data)
      setPendingModel(`${data.model_provider}:${data.model_name}`)
      // If your API returns whether these exist, update the state here. 
      // Example: setArtifacts({ srs: data.has_srs, useCase: data.has_usecase, ... })
    })
  }, [projectId])

  useEffect(() => {
    loadHistory().then(() => { })
  }, [])

  useEffect(() => {
    if (messages.length === 0 && !loading) startInterview()
  }, [messages, loading])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const { isListening, toggleListening } = useVoiceToText((transcript) => {
    setInput((prev) => {
      const newText = prev.trim() ? `${prev} ${transcript}` : transcript
      return newText
    })
  })

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const text = input;
    setInput('');
    setSendError(null);

    try {
      await sendMessage(text);
      inputRef.current?.focus();
    } catch (err) {
      console.error("Send error:", err);
      setSendError(t('err_failed_send'));
    }
  };

  // Button Click Handlers for State Logic
  const handleGenerateSRS = async () => {
    setGenerating(true)
    try {
      await apiClient.post('/req/generate-srs', { project_id: projectId })
      
      // Update local state to unlock dependent buttons
      setArtifacts(prev => ({ ...prev, srs: true }))
      
      navigate(`/project/${projectId}/srs`)
    } catch (err) {
      alert(err.response?.data?.detail || t('err_generate_srs'))
    } finally {
      setGenerating(false)
    }
  }

  // Placeholder functions to trigger the state changes for the other diagrams
  const handleGenerateUseCase = () => {
    setArtifacts(prev => ({ ...prev, useCase: true }))
    // Add API call here
  }

  const handleGenerateClass = () => {
    setArtifacts(prev => ({ ...prev, class: true }))
    // Add API call here
  }

  const handleGenerateActivity = () => {
    setArtifacts(prev => ({ ...prev, activity: true }))
    // Add API call here
  }

  const handleReset = async () => {
    if (!window.confirm(t('archive_confirm'))) return
    await resetConversation()
    await startInterview()
  }

  const handleModelChange = async (newModelValue) => {
    if (newModelValue === currentModelKey) return;
    const [provider, modelName] = newModelValue.split(':')
    setSavingModel(true)
    try {
      const { data } = await apiClient.patch(`/projects/${projectId}/model`, {
        model_provider: provider,
        model_name: modelName,
      })
      setProject(data)
    } catch (err) {
      alert(err.response?.data?.detail || t('err_update_model'))
    } finally {
      setSavingModel(false)
    }
  }

  const currentModelKey = project ? `${project.model_provider}:${project.model_name}` : ''
  const currentModelName = project && models
    ? models[project.model_provider]?.[project.model_name] || project.model_name
    : ''

  return (
    <div className="h-screen bg-slate-100 flex flex-col overflow-hidden">
      
      {/* --- HEADER --- */}
      <div className="flex-none z-50 bg-white shadow-sm border-b border-slate-200/50">
        <Navbar projectName={project?.app_name} backTo="/" backLabel={t('dashboard')} />
        
        {project && (
          <div className="px-6 py-2 bg-slate-50/50 flex border-t border-slate-100">
            <ModelSelector
              value={currentModelKey}
              onChange={handleModelChange}
              models={models}
            />
          </div>
        )}
      </div>

      {/* --- MAIN PADDED LAYOUT (Creates the separated floating sections) --- */}
      <div className="flex-1 flex flex-row overflow-hidden p-4 gap-4">
        
        {/* ================= LEFT SECTION: CHAT (3/4 WIDTH, ROUNDED) ================= */}
        <div className="w-3/4 flex flex-col bg-white rounded-3xl shadow-sm border border-slate-200 overflow-hidden relative">
          
          <div className="flex-1 overflow-y-auto px-6 py-8 w-full scrollbar-hide">
            <div className="max-w-4xl mx-auto">
              {error && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700 text-start">{error}</div>
              )}

              {/* CHAT MESSAGES */}
              {messages.map((msg) => <ChatMessage key={msg.id} message={msg} />)}

              {/* LOADING INDICATOR */}
              {loading && (
                <div className="flex justify-start mb-4 animate-in fade-in slide-in-from-bottom-2">
                  <div className="flex gap-3 max-w-[80%]">
                    <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center flex-shrink-0 mt-1 shadow-sm">
                      <span className="text-xs font-bold">AI</span>
                    </div>
                    <div className="bg-slate-50 border border-slate-100 rounded-2xl rounded-tl-none px-4 py-3.5 shadow-sm flex items-center h-[42px]">
                      <div className="flex gap-1.5 items-center">
                        <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                        <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                        <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {sendError && (
                <div className="mb-4 animate-in fade-in slide-in-from-bottom-2">
                  <div className="p-3 bg-red-50 border border-red-100 rounded-xl text-xs text-red-600 flex items-center gap-2 text-start">
                    <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {sendError}
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* CHAT INPUT BOX */}
          <div className="bg-white px-6 py-4 border-t border-slate-100">
            <div className="max-w-4xl mx-auto bg-slate-50 rounded-2xl p-2 border border-slate-200 focus-within:border-brand-300 focus-within:ring-1 focus-within:ring-brand-300 transition-all">
              <form onSubmit={handleSend} className="flex gap-2 items-end">
                <textarea
                  ref={inputRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(e) } }}
                  rows={1}
                  placeholder={t('type_answer')}
                  className="flex-1 bg-transparent px-3 py-2 text-sm resize-none focus:outline-none max-h-32 overflow-y-auto text-start"
                  style={{ minHeight: '40px' }}
                />
                
                <div className="flex gap-1 pb-1 pr-1">
                  <button
                    type="button"
                    onClick={toggleListening}
                    className={`p-2.5 rounded-xl transition-all ${isListening
                      ? 'bg-red-500 text-white scale-110 shadow-md'
                      : 'text-slate-400 hover:bg-slate-200 hover:text-slate-600'
                      }`}
                  >
                    {isListening ? (
                      <div className="flex gap-[3px] h-4 items-center">
                        <span className="w-1 h-2 bg-white animate-bounce" />
                        <span className="w-1 h-4 bg-white animate-bounce [animation-delay:0.2s]" />
                        <span className="w-1 h-3 bg-white animate-bounce [animation-delay:0.4s]" />
                      </div>
                    ) : (
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                      </svg>
                    )}
                  </button>
                  <button
                    type="submit"
                    disabled={loading || !input.trim()}
                    className="p-2.5 bg-brand-600 text-white rounded-xl hover:bg-brand-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <svg className="w-4 h-4 rtl:-scale-x-100" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                    </svg>
                  </button>
                </div>
              </form>
            </div>
            
            {/* Context Footer */}
            <div className="max-w-4xl mx-auto flex items-center justify-between mt-3 px-2">
              <p className="text-xs text-slate-400 font-medium">
                {messages.length} {messages.length === 1 ? t('message_singular') : t('messages_plural')}
              </p>
              <button onClick={handleReset} className="text-xs font-medium text-slate-400 hover:text-slate-600 transition-colors">
                {t('reset_conv')}
              </button>
            </div>
          </div>
        </div>

        {/* ================= RIGHT SECTION: STUDIO (1/4 WIDTH, ROUNDED) ================= */}
        <div className="w-1/4 bg-white rounded-3xl shadow-sm border border-slate-200 flex flex-col overflow-hidden">
          <div className="p-6 overflow-y-auto h-full">
            
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-lg font-semibold text-slate-800">Studio</h2>
              {true && (
                <span className="flex h-2.5 w-2.5 relative">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-green-500"></span>
                </span>
              )}
            </div>

            {true && (
              <div className="mb-5 p-3 bg-green-50 border border-green-200 rounded-2xl text-xs text-green-800 flex items-start gap-2 shadow-sm">
                 <svg className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span className="leading-relaxed"><strong>{t('info_complete')}</strong> {t('ready_generate')}</span>
              </div>
            )}

            {/* NotebookLM Style Buttons Grid (2 columns) */}
            <div className="grid grid-cols-2 gap-3">
              
              {/* 1. SRS Button */}
              <button
                onClick={handleGenerateSRS}
                disabled={generating}
                className="flex flex-col items-start justify-between p-3.5 h-[90px] bg-blue-50/60 hover:bg-blue-100/80 rounded-2xl transition-all disabled:opacity-50 disabled:cursor-not-allowed group text-left border border-transparent hover:border-blue-200"
              >
                <div className="text-blue-600">
                  {generating ? (
                    <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>
                  ) : (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                  )}
                </div>
                <span className="font-medium text-slate-700 text-xs leading-tight">SRS<br/>Requirement</span>
              </button>

              {/* 2. Use Case Diagram */}
              <button 
                onClick={handleGenerateUseCase}
                disabled={!artifacts.srs}
                className="flex flex-col items-start justify-between p-3.5 h-[90px] bg-purple-50/60 hover:bg-purple-100/80 rounded-2xl transition-all disabled:opacity-50 disabled:cursor-not-allowed group text-left border border-transparent hover:border-purple-200"
              >
                <div className="text-purple-600">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>
                </div>
                <span className="font-medium text-slate-700 text-xs leading-tight">Use Case<br/>Diagram</span>
              </button>

              {/* 3. Class Diagram */}
              <button 
                onClick={handleGenerateClass}
                disabled={!artifacts.srs}
                className="flex flex-col items-start justify-between p-3.5 h-[90px] bg-yellow-50/80 hover:bg-yellow-100 rounded-2xl transition-all disabled:opacity-50 disabled:cursor-not-allowed group text-left border border-transparent hover:border-yellow-200"
              >
                <div className="text-yellow-600">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" /></svg>
                </div>
                <span className="font-medium text-slate-700 text-xs leading-tight">Class<br/>Diagram</span>
              </button>

              {/* 4. Activity Diagram */}
              <button 
                onClick={handleGenerateActivity}
                disabled={!artifacts.useCase || !artifacts.class}
                className="flex flex-col items-start justify-between p-3.5 h-[90px] bg-emerald-50/60 hover:bg-emerald-100/80 rounded-2xl transition-all disabled:opacity-50 disabled:cursor-not-allowed group text-left border border-transparent hover:border-emerald-200"
              >
                <div className="text-emerald-600">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5" /></svg>
                </div>
                <span className="font-medium text-slate-700 text-xs leading-tight">Activity<br/>Diagram</span>
              </button>

            </div>
          </div>
        </div>
      </div>
    </div>
  )
}