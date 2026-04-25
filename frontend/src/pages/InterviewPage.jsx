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

export default function InterviewPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const projectId = parseInt(id)

  const { t } = useTranslation()

  // --- States ---
  const [project, setProject] = useState(null)
  const [input, setInput] = useState('')
  const [srsLoading, setSrsLoading] = useState(false)
  const [pendingModel, setPendingModel] = useState('')
  const [savingModel, setSavingModel] = useState(false)
  const [sendError, setSendError] = useState(null)
  const [srsError, setSrsError] = useState(null)
  const [umlError, setUmlError] = useState(null)
  const [requirementsReady, setRequirementsReady] = useState(false)
  const [activeDiagram, setActiveDiagram] = useState('')
  const [sequenceOptions, setSequenceOptions] = useState([])
  const [selectedUsecaseIdx, setSelectedUsecaseIdx] = useState(null)
  const [forceRefresh, setForceRefresh] = useState(0) // تم نقله للداخل

  const [diagramSvgs, setDiagramSvgs] = useState({
    useCase: '',
    class: '',
    activity: '',
    sequence: '',
  })
  const [umlLoading, setUmlLoading] = useState({
    useCase: false,
    class: false,
    activity: false,
    sequence: false,
  })

  const [artifacts, setArtifacts] = useState({
    srs: false,
    useCase: false,
    class: false,
    activity: false,
    sequence: false,
  })

  const [persistedArtifacts, setPersistedArtifacts] = useState({
    srs: false,
    useCase: false,
    class: false,
    activity: false,
    sequence: false,
  })

  // --- Refs ---
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  const initializationLock = useRef(null) // قفل لمنع تكرار الطلبات

  // --- Custom Hooks ---
  const { models } = useModels()
  const { 
    messages, 
    loading, 
    isSaturated, 
    error, 
    loadHistory, 
    startInterview, 
    sendMessage, 
    resetConversation 
  } = useChat(projectId)

  // --- Helpers ---
  const checkRequirementsExist = async () => {
    try {
      const { data } = await apiClient.get(`/requirements/${projectId}`)
      const exists = Array.isArray(data) && data.length > 0
      setRequirementsReady(exists)
      setArtifacts((prev) => ({ ...prev, srs: exists }))
      return exists
    } catch { return false }
  }

  const syncPersistedArtifacts = async () => {
    try {
      const { data } = await apiClient.get(`/projects/${projectId}/artifacts`)
      const synced = {
        srs:      !!data.srs,
        useCase:  !!data.use_case,
        class:    !!data.class,
        activity: !!data.activity,
        sequence: !!data.sequence,
      }
      setPersistedArtifacts(synced)
      setArtifacts((prev) => ({ ...prev, ...synced }))
      if (synced.srs) setRequirementsReady(true)
    } catch { }
  }

  // --- Effects ---

  // 1. جلب بيانات المشروع
  useEffect(() => {
    let isMounted = true
    apiClient.get(`/projects/${projectId}`)
      .then(async ({ data }) => {
        if (!isMounted) return
        setProject(data)
        setPendingModel(`${data.model_provider}:${data.model_name}`)
        await Promise.allSettled([checkRequirementsExist(), syncPersistedArtifacts()])
      })
      .catch(() => {})
    return () => { isMounted = false }
  }, [projectId])

  // 2. حل مشكلة تكرار الطلبات وعدم ظهور الرسائل عند الانتقال
  useEffect(() => {
    // إذا تم تفعيل القفل لهذا المشروع مسبقاً، لا تفعل شيئاً
    if (initializationLock.current === projectId) return;
    initializationLock.current = projectId;

    let isMounted = true;
    const setupChat = async () => {
      try {
        const history = await loadHistory();
        if (!isMounted) return;

        const hasHistory = Array.isArray(history) && history.length > 0;
        
        if (!hasHistory) {
          await startInterview();
        }
        
        // إجبار الواجهة على التحديث بعد تحميل البيانات
        setForceRefresh(prev => prev + 1);
      } catch (err) {
        console.error("Chat setup failed:", err);
      }
    };

    setupChat();
    return () => { isMounted = false; };
  }, [projectId]); 

  // 3. التمرير التلقائي
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  // --- Voice Handlers ---
  const { isListening, toggleListening } = useVoiceToText((transcript) => {
    setInput((prev) => {
      const newText = prev.trim() ? `${prev} ${transcript}` : transcript
      return newText
    })
  })

  // --- Action Handlers ---
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
    setSrsError(null)
    setSrsLoading(true)
    try {
      const hasRequirements = await checkRequirementsExist()
      if (!hasRequirements) {
        await apiClient.post('/requirements/generate-srs', { project_id: projectId })
        setRequirementsReady(true)
        setArtifacts((prev) => ({ ...prev, srs: true }))
      }
      navigate(`/project/${projectId}/srs`)
    } catch (err) {
      setSrsError(err.response?.data?.detail || t('err_generate_srs'))
    } finally {
      setSrsLoading(false)
    }
  }

  const handleOpenRequirementsUpdate = () => {
    navigate(`/project/${projectId}/srs`)
  }

  const callDiagramApi = async (key, endpoint) => {
    setUmlError(null)
    setUmlLoading((prev) => ({ ...prev, [key]: true }))
    try {
      const { data } = await apiClient.get(endpoint)
      const nextSvg = data?.svg_url || ''
      setDiagramSvgs((prev) => ({ ...prev, [key]: nextSvg }))
      setArtifacts((prev) => ({ ...prev, [key]: true }))
      setActiveDiagram(key)
      return data
    } catch (err) {
      setUmlError(err.response?.data?.detail || t('err_generate_uml'))
      return null
    } finally {
      setUmlLoading((prev) => ({ ...prev, [key]: false }))
    }
  }

  const handleGenerateUseCase = async () => {
    const data = await callDiagramApi('useCase', `/generate-usecase/${projectId}`)
    if (!data?.data?.use_cases) return
    const options = data.data.use_cases.map((name, idx) => ({ idx, name }))
    setSequenceOptions(options)
    if (options.length > 0) setSelectedUsecaseIdx(options[0].idx)
  }

  const handleGenerateClass = async () => {
    await callDiagramApi('class', `/generate-class/${projectId}`)
  }

  const handleGenerateActivity = async () => {
    await callDiagramApi('activity', `/generate-activity/${projectId}`)
  }

  const handleGenerateSequence = async () => {
    if (selectedUsecaseIdx === null || selectedUsecaseIdx === undefined) return
    await callDiagramApi('sequence', `/generate-sequence/${projectId}/${selectedUsecaseIdx}`)
  }

  const handleReset = async () => {
    if (!window.confirm(t('archive_confirm'))) return
    initializationLock.current = null; // فك القفل ليتمكن من البدء مجدداً
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

  // --- Constants for UI ---
  const currentModelKey = project ? `${project.model_provider}:${project.model_name}` : ''
  const studioReady = isSaturated || requirementsReady
  const canGenerateBaseDiagrams = requirementsReady || isSaturated
  const canGenerateDependentDiagrams = artifacts.useCase && artifacts.class
  const buttonBaseClass =
    'flex flex-col items-start justify-between p-3.5 h-[90px] rounded-2xl transition-all disabled:opacity-50 disabled:cursor-not-allowed group text-left border border-transparent'
  const activeSvgUrl = activeDiagram ? diagramSvgs[activeDiagram] : ''

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

      {/* --- MAIN LAYOUT --- */}
      <div className="flex-1 flex flex-row overflow-hidden p-4 gap-4">
        
        {/* LEFT SECTION: CHAT */}
        <div className="w-3/4 flex flex-col bg-white rounded-3xl shadow-sm border border-slate-200 overflow-hidden relative">
          
          <div className="flex-1 overflow-y-auto px-6 py-8 w-full scrollbar-hide">
            <div className="max-w-4xl mx-auto">
              {error && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700 text-start">{error}</div>
              )}

              {/* MESSAGES LIST */}
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

          {/* INPUT BAR */}
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

        {/* RIGHT SECTION: STUDIO */}
        <div className="w-1/4 bg-white rounded-3xl shadow-sm border border-slate-200 flex flex-col overflow-hidden">
          <div className="p-6 overflow-y-auto h-full">
            
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-lg font-semibold text-slate-800">Studio</h2>
              {studioReady && (
                <span className="flex h-2.5 w-2.5 relative">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-green-500"></span>
                </span>
              )}
            </div>

            {studioReady ? (
              <div className="mb-5 p-3 bg-green-50 border border-green-200 rounded-2xl text-xs text-green-800 flex items-start gap-2 shadow-sm">
                 <svg className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span className="leading-relaxed"><strong>{t('info_complete')}</strong> {t('ready_generate')}</span>
              </div>
            ) : !requirementsReady && !isSaturated ? (
              <div className="mb-5 p-3 bg-slate-50 border border-slate-200 rounded-2xl text-xs text-slate-600">
                Continue the interview to unlock SRS and diagrams.
              </div>
            ) : null}

            {srsError && <div className="mb-3 p-2.5 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700">{srsError}</div>}
            {umlError && <div className="mb-3 p-2.5 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700">{umlError}</div>}

            <div className="mb-3 flex gap-2">
              <button
                onClick={handleGenerateSRS}
                disabled={srsLoading}
                className="flex-1 h-10 px-3 bg-blue-600 text-white rounded-xl text-xs font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                {srsLoading ? 'Generating...' : 'Generate SRS'}
              </button>
              <button
                onClick={handleOpenRequirementsUpdate}
                disabled={!requirementsReady}
                className="flex-1 h-10 px-3 bg-white border border-slate-300 text-slate-700 rounded-xl text-xs font-medium hover:bg-slate-50 disabled:opacity-50 transition-colors"
              >
                Update
              </button>
            </div>

            <h3 className="text-sm font-semibold text-slate-700 mb-3">Diagrams</h3>
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={handleGenerateUseCase}
                disabled={!canGenerateBaseDiagrams || umlLoading.useCase}
                className={`${buttonBaseClass} bg-purple-50/60 hover:bg-purple-100/80 hover:border-purple-200`}
              >
                <div className="text-purple-600">
                   {umlLoading.useCase ? <svg className="w-5 h-5 animate-spin" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg> : <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/></svg>}
                </div>
                <span className="font-medium text-slate-700 text-xs leading-tight">Use Case<br/>Diagram</span>
              </button>

              <button 
                onClick={handleGenerateClass}
                disabled={!canGenerateBaseDiagrams || umlLoading.class}
                className={`${buttonBaseClass} bg-yellow-50/80 hover:bg-yellow-100 hover:border-yellow-200`}
              >
                <div className="text-yellow-600">
                  {umlLoading.class ? <svg className="w-5 h-5 animate-spin" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg> : <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/></svg>}
                </div>
                <span className="font-medium text-slate-700 text-xs leading-tight">Class<br/>Diagram</span>
              </button>

              <button 
                onClick={handleGenerateActivity}
                disabled={!canGenerateDependentDiagrams || umlLoading.activity}
                className={`${buttonBaseClass} bg-emerald-50/60 hover:bg-emerald-100/80 hover:border-emerald-200`}
              >
                <div className="text-emerald-600">
                  {umlLoading.activity ? <svg className="w-5 h-5 animate-spin" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg> : <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5"/></svg>}
                </div>
                <span className="font-medium text-slate-700 text-xs leading-tight">Activity<br/>Diagram</span>
              </button>

              <button 
                onClick={handleGenerateSequence}
                disabled={!canGenerateDependentDiagrams || umlLoading.sequence || selectedUsecaseIdx === null}
                className={`${buttonBaseClass} bg-indigo-50/70 hover:bg-indigo-100/80 hover:border-indigo-200`}
              >
                <div className="text-indigo-600">
                  {umlLoading.sequence ? <svg className="w-5 h-5 animate-spin" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg> : <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5h18M3 12h18M3 19h18" /></svg>}
                </div>
                <span className="font-medium text-slate-700 text-xs leading-tight">Sequence<br/>Diagram</span>
              </button>
            </div>

            <div className="mt-4">
              <label className="block text-xs text-slate-600 mb-1">Sequence Use Case</label>
              <select
                value={selectedUsecaseIdx ?? ''}
                onChange={(e) => setSelectedUsecaseIdx(e.target.value === '' ? null : Number(e.target.value))}
                disabled={sequenceOptions.length === 0}
                className="w-full h-9 px-2 rounded-lg border border-slate-200 text-xs bg-white disabled:bg-slate-50"
              >
                {sequenceOptions.length === 0 ? (
                  <option value="">Generate Use Case first</option>
                ) : (
                  sequenceOptions.map((option) => (
                    <option key={option.idx} value={option.idx}>
                      {option.idx}: {option.name}
                    </option>
                  ))
                )}
              </select>
            </div>

            {activeSvgUrl && (
              <div className="mt-4 border border-slate-200 rounded-xl overflow-hidden bg-slate-50">
                <div className="px-3 py-2 text-xs font-medium text-slate-700 border-b border-slate-200 capitalize">
                  {activeDiagram} diagram
                </div>
                <img src={activeSvgUrl} alt={`${activeDiagram} diagram`} className="w-full h-auto bg-white" />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}