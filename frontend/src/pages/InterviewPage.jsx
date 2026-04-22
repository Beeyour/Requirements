import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next' // 1. Import the hook

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

  const { t } = useTranslation() // 2. Initialize the hook

  const [project, setProject] = useState(null)
  const [input, setInput] = useState('')
  const [generating, setGenerating] = useState(false)
  const [showModelModal, setShowModelModal] = useState(false)
  const [pendingModel, setPendingModel] = useState('')
  const [savingModel, setSavingModel] = useState(false)
  const [sendError, setSendError] = useState(null)

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

  const handleGenerateSRS = async () => {
    setGenerating(true)
    try {
      await apiClient.post('/generate-srs', { project_id: projectId })
      navigate(`/project/${projectId}/srs`)
    } catch (err) {
      // 3. Translate API error fallback
      alert(err.response?.data?.detail || t('err_generate_srs'))
    } finally {
      setGenerating(false)
    }
  }

  const handleReset = async () => {
    // 4. Translate browser confirm dialog
    if (!window.confirm(t('archive_confirm'))) return
    await resetConversation()
    await startInterview()
  }


  const handleModelChange = async (newModelValue) => {

    if (newModelValue === currentModelKey) return;

    // Split the direct input instead of pendingModel
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
  const providerColorClass = project ? (PROVIDER_COLORS[project.model_provider] || 'bg-slate-50 text-slate-700 border-slate-200') : ''

  return (
    <div className="h-screen bg-slate-50 flex flex-col">

      {/* --- STICKY HEADER WRAPPER --- */}
      <div className="sticky top-0 z-50 bg-white">
        <Navbar projectName={project?.app_name} backTo="/" backLabel={t('dashboard')} />

        {/* Model badge bar */}
        {project && (
          <div className="border-b border-slate-100 px-6 bg-white/50">
            <ModelSelector
              value={currentModelKey}
              onChange={handleModelChange}
              models={models}
            />
          </div>
        )}

        {/* SRS Banner */}
        {isSaturated && (
          <div className="bg-green-50 border-b border-green-200 px-6 py-3 flex items-center justify-between">
            <div className="flex items-center gap-2 text-green-800 text-sm">
              <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              <strong>{t('info_complete')}</strong> {t('ready_generate')}
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
              {generating ? t('generating') : t('generate_srs')}
            </button>
          </div>
        )}
      </div>
      {/* --- END STICKY HEADER --- */}

      <div className="flex-1 overflow-y-auto px-4 py-6 max-w-3xl mx-auto w-full scrollbar-hide">
        {/* General Error (like Load History failure) */}
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700 text-start">{error}</div>
        )}

        {/* CHAT MESSAGES */}
        {messages.map((msg) => <ChatMessage key={msg.id} message={msg} />)}

        {/* LOADING INDICATOR */}
        {loading && (
          <div className="flex justify-start mb-4 animate-in fade-in slide-in-from-bottom-2">
            <div className="flex gap-3 max-w-[80%]">
              {/* AI Avatar */}
              <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center flex-shrink-0 mt-1 shadow-sm">
                <span className="text-xs font-bold">AI</span>
              </div>

              {/* Thinking Bubble */}
              <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-none px-4 py-3.5 shadow-sm flex items-center h-[42px]">
                <div className="flex gap-1.5 items-center">
                  <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* SPECIFIC SEND ERROR - Appears at the bottom of the chat list */}
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

      <div className="border-t border-slate-200 bg-white px-4 py-4">
        <div className="max-w-3xl mx-auto">
          <form onSubmit={handleSend} className="flex gap-3 items-end">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(e) } }}
              rows={1}
              placeholder={t('type_answer')}
              // 6. Add text-start to textarea
              className="flex-1 border border-slate-300 rounded-xl px-4 py-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent max-h-32 overflow-y-auto text-start"
              style={{ minHeight: '44px' }}
            />
            {/* MICROPHONE BUTTON */}
            <button
              type="button"
              onClick={toggleListening}
              className={`p-3 rounded-xl transition-all ${isListening
                ? 'bg-red-500 text-white scale-110 shadow-lg'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
            >
              {isListening ? (
                <div className="flex gap-1">
                  <span className="w-1 h-4 bg-white animate-bounce" />
                  <span className="w-1 h-4 bg-white animate-bounce [animation-delay:0.2s]" />
                  <span className="w-1 h-4 bg-white animate-bounce [animation-delay:0.4s]" />
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
              className="p-3 bg-brand-600 text-white rounded-xl hover:bg-brand-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex-shrink-0"
            >
              {/* Changed arrow direction implicitly by flipping if needed, but this standard Send arrow is usually fine as is. If you want it to flip in RTL, add `rtl:-scale-x-100` */}
              <svg className="w-4 h-4 rtl:-scale-x-100" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </form>
          <div className="flex items-center justify-between mt-2">
            <p className="text-xs text-slate-400">
              {messages.length} {messages.length === 1 ? t('message_singular') : t('messages_plural')}
            </p>
            <button onClick={handleReset} className="text-xs text-slate-400 hover:text-slate-600 transition-colors">
              {t('reset_conv')}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}