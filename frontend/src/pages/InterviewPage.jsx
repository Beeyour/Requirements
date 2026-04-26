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

  const [project, setProject] = useState(null)
  const [input, setInput] = useState('')
  const [srsLoading, setSrsLoading] = useState(false)
  const [pendingModel, setPendingModel] = useState('')
  const [savingModel, setSavingModel] = useState(false)
  const [sendError, setSendError] = useState(null)
  const [srsError, setSrsError] = useState(null)
  const [umlError, setUmlError] = useState(null)
  const [requirementsReady, setRequirementsReady] = useState(false)
  const [sequenceOptions, setSequenceOptions] = useState([])
  const [selectedUsecaseIdx, setSelectedUsecaseIdx] = useState(null)
  const [forceRefresh, setForceRefresh] = useState(0)
  const [pdfLoading, setPdfLoading] = useState(false)
  const [pdfError, setPdfError] = useState(null)

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

  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  const currentLoadingId = useRef(null)

  const { models } = useModels()
  const { messages, loading, isSaturated, error, loadHistory, startInterview, sendMessage, resetConversation } =
    useChat(projectId)

  const checkRequirementsExist = async () => {
    const { data } = await apiClient.get(`/requirements/${projectId}`)
    const exists = Array.isArray(data) && data.length > 0
    setRequirementsReady(exists)
    setArtifacts((prev) => ({ ...prev, srs: exists }))
    return exists
  }

  const syncPersistedArtifacts = async () => {
    try {
      const { data } = await apiClient.get(`/projects/${projectId}/artifacts`)
      const synced = {
        srs: !!data.srs,
        useCase: !!data.use_case,
        class: !!data.class,
        activity: !!data.activity,
        sequence: !!data.sequence,
      }
      setPersistedArtifacts(synced)
      setArtifacts((prev) => ({ ...prev, ...synced }))
      if (synced.srs) setRequirementsReady(true)
    } catch {
      // Endpoint may not exist yet — fail silently
    }
  }

  useEffect(() => {
    setProject(null)
    setRequirementsReady(false)
    setSequenceOptions([])
    setSelectedUsecaseIdx(null)
    setArtifacts({
      srs: false,
      useCase: false,
      class: false,
      activity: false,
      sequence: false,
    })
  }, [projectId])

  useEffect(() => {
    let isMounted = true;

    apiClient
      .get(`/projects/${projectId}`)
      .then(async ({ data }) => {
        if (!isMounted) return;
        setProject(data)
        setPendingModel(`${data.model_provider}:${data.model_name}`)
        await Promise.allSettled([checkRequirementsExist(), syncPersistedArtifacts()])
      })
      .catch(() => { })

    return () => { isMounted = false };
  }, [projectId])

  useEffect(() => {
    if (currentLoadingId.current === projectId) return;
    currentLoadingId.current = projectId;

    let isMounted = true;

    const setupChat = async () => {
      try {
        const history = await loadHistory();
        if (!isMounted) return;
        const hasHistory = Array.isArray(history) && history.length > 0;
        if (!hasHistory) {
          await startInterview();
        }
        setForceRefresh(prev => prev + 1);
      } catch (err) {
        console.error("Failed to initialize chat:", err);
      }
    };

    setupChat();

    return () => {
      isMounted = false;
      currentLoadingId.current = null;
    };
  }, [projectId]);

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

  const handleUpdateRequirements = async () => {
    setSrsError(null)
    setSrsLoading(true)
    try {
      await apiClient.post(`/requirements/update-requirements/${projectId}`)
      navigate(`/project/${projectId}/srs`)
    } catch (err) {
      setSrsError(err.response?.data?.detail || "Failed to update requirements")
    } finally {
      setSrsLoading(false)
    }
  }

  const handleViewSrs = async () => {
    if (!requirementsReady) return;
    try {
      await apiClient.get(`/requirements/${projectId}`);
      navigate(`/project/${projectId}/srs`);
    } catch (err) {
      setSrsError("Failed to fetch SRS document.");
      console.error("Error fetching SRS:", err);
    }
  }

  const callDiagramApi = async (key, endpoint) => {
    setUmlError(null)
    setUmlLoading((prev) => ({ ...prev, [key]: true }))
    try {
      const { data } = await apiClient.get(endpoint)

      // Navigate to diagram viewer instead of showing inline
      if (key === 'useCase') {
        navigate(`/project/${projectId}/diagram/usecase`)
      } else if (key === 'class') {
        navigate(`/project/${projectId}/diagram/class`)
      } else if (key === 'activity') {
        navigate(`/project/${projectId}/diagram/activity`)
      } else if (key === 'sequence') {
        navigate(`/project/${projectId}/diagram/sequence?usecase_idx=${selectedUsecaseIdx}`)
      }

      // Store data for potential future use
      if (data?.data?.use_cases) {
        const options = data.data.use_cases.map((name, idx) => ({ idx, name }))
        setSequenceOptions(options)
        if (options.length > 0 && selectedUsecaseIdx === null) {
          setSelectedUsecaseIdx(options[0].idx)
        }
      }

      setArtifacts((prev) => ({ ...prev, [key]: true }))
      return data
    } catch (err) {
      setUmlError(err.response?.data?.detail || t('err_generate_uml'))
      return null
    } finally {
      setUmlLoading((prev) => ({ ...prev, [key]: false }))
    }
  }

  const handleGenerateUseCase = async () => {
    await callDiagramApi('useCase', `/generate-usecase/${projectId}`)
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

  const getFriendlyErrorMessage = (error) => {
    const errorMessage = error?.toString().toLowerCase()
    if (errorMessage.includes('not found') || errorMessage.includes('404')) {
      return 'Diagram not generated yet. Please generate the required diagrams first.'
    }
    if (errorMessage.includes('no active functional requirements')) {
      return 'Please complete the interview and generate SRS first.'
    }
    if (errorMessage.includes('requirements')) {
      return 'Please generate SRS requirements first.'
    }
    return error || 'An error occurred. Please try again.'
  }

  const handleGeneratePDF = async () => {
    setPdfError(null)
    setPdfLoading(true)
    try {
      const { data } = await apiClient.get(`/generate-pdf/${projectId}`)
      // Create a download link for the PDF
      const link = document.createElement('a')
      link.href = data.pdf_url
      link.download = `${project?.app_name || 'SRS'}_Comprehensive_Report.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    } catch (err) {
      setPdfError(err.response?.data?.detail || 'Failed to generate PDF')
    } finally {
      setPdfLoading(false)
    }
  }

  const handleReset = async () => {
    if (!window.confirm(t('archive_confirm'))) return
    currentLoadingId.current = null;
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

  const studioReady = isSaturated || requirementsReady
  const canGenerateBaseDiagrams = requirementsReady || isSaturated
  const canGenerateDependentDiagrams = artifacts.useCase && artifacts.class
  const buttonBaseClass =
    'flex flex-col items-start justify-between p-3.5 h-[90px] rounded-2xl transition-all disabled:opacity-50 disabled:cursor-not-allowed group text-left border border-transparent'

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

      {/* --- MAIN PADDED LAYOUT --- */}
      <div className="flex-1 flex flex-row overflow-hidden p-4 gap-4">
        {/* ================= LEFT SECTION: CHAT ================= */}
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

        {/* ================= RIGHT SECTION: STUDIO ================= */}
        <div className="w-1/4 bg-white rounded-3xl shadow-sm border border-slate-200 flex flex-col overflow-hidden">
          <div className="p-6 overflow-y-auto h-full">

            {/* HEADER WITH VIEW BUTTON */}
            <div className="flex items-center justify-between mb-5">
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-semibold text-slate-800">Studio</h2>
                {studioReady && (
                  <span className="flex h-2.5 w-2.5 relative">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-green-500"></span>
                  </span>
                )}
              </div>

              <button
                onClick={handleViewSrs}
                disabled={!requirementsReady}
                title={!requirementsReady ? 'Generate SRS first.' : 'View SRS Document'}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all text-xs font-medium ${requirementsReady
                  ? 'bg-slate-100 text-slate-700 hover:bg-slate-200 cursor-pointer'
                  : 'bg-slate-50 text-slate-400 opacity-50 cursor-not-allowed'
                  }`}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                View
              </button>
            </div>

            {/* INFO BANNERS */}
            {studioReady ? (
              <div className="mb-5 p-3 bg-green-50 border border-green-200 rounded-2xl text-xs text-green-800 flex items-start gap-2 shadow-sm">
                <svg className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span className="leading-relaxed"><strong>{t('info_complete')}</strong> {t('ready_generate')}</span>
              </div>
            ) : !requirementsReady && !isSaturated ? (
              <div className="mb-5 p-3 bg-slate-50 border border-slate-200 rounded-2xl text-xs text-slate-600">
                Continue the interview until saturation to unlock full diagram generation. Or click Generate SRS to begin.
              </div>
            ) : null}

            {srsError && (
              <div className="mb-3 p-2.5 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-700">
                <div className="flex items-start gap-2">
                  <svg className="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                  <span>{getFriendlyErrorMessage(srsError)}</span>
                </div>
              </div>
            )}
            {umlError && (
              <div className="mb-3 p-2.5 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-700">
                <div className="flex items-start gap-2">
                  <svg className="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                  <span>{getFriendlyErrorMessage(umlError)}</span>
                </div>
              </div>
            )}
            {pdfError && (
              <div className="mb-3 p-2.5 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-700">
                <div className="flex items-start gap-2">
                  <svg className="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                  <span>{getFriendlyErrorMessage(pdfError)}</span>
                </div>
              </div>
            )}

            {/* SRS AND PDF ACTION BUTTONS */}
            <div className="mb-5 flex gap-3">

              {/* LEFT BUTTON: Generate / Update SRS */}
              <button
                onClick={requirementsReady ? handleUpdateRequirements : handleGenerateSRS}
                disabled={srsLoading}
                className={`flex-1 flex items-center justify-center gap-1.5 h-11 px-3 rounded-xl text-xs font-medium transition-all shadow-sm disabled:opacity-50 disabled:cursor-not-allowed ${requirementsReady
                    ? 'bg-emerald-600 hover:bg-emerald-700 text-white'
                    : 'bg-blue-600 hover:bg-blue-700 text-white'
                  }`}
              >
                {srsLoading ? (
                  <>
                    <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    {requirementsReady ? 'Updating...' : 'Generating...'}
                  </>
                ) : requirementsReady ? (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    Update SRS
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Generate SRS
                  </>
                )}
              </button>

              {/* RIGHT BUTTON: Export PDF */}
              <button
                onClick={handleGeneratePDF}
                disabled={pdfLoading || !requirementsReady}
                title={!requirementsReady ? 'Generate SRS first to enable PDF export.' : 'Download complete PDF'}
                className="flex-1 flex items-center justify-center gap-1.5 h-11 px-3 bg-white border border-slate-200 text-slate-700 rounded-xl text-xs font-medium hover:bg-slate-50 hover:border-slate-300 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm"
              >
                {pdfLoading ? (
                  <>
                    <svg className="w-4 h-4 animate-spin text-slate-400" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Exporting...
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4 text-rose-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Generate PDF
                  </>
                )}
              </button>
            </div>

            <h3 className="text-sm font-semibold text-slate-700 mb-3">Diagrams</h3>
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={handleGenerateUseCase}
                disabled={!canGenerateBaseDiagrams || umlLoading.useCase}
                title={!canGenerateBaseDiagrams ? 'Generate/confirm SRS and complete interview first.' : ''}
                className={`${buttonBaseClass} bg-purple-50/60 hover:bg-purple-100/80 hover:border-purple-200`}
              >
                <div className="text-blue-600">
                  {umlLoading.useCase ? (
                    <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                  ) : (
                    <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                  )}
                </div>
                <span className="font-medium text-slate-700 text-xs leading-tight">Use Case<br />Diagram</span>
              </button>

              <button
                onClick={handleGenerateClass}
                disabled={!canGenerateBaseDiagrams || umlLoading.class}
                title={!canGenerateBaseDiagrams ? 'Generate/confirm SRS and complete interview first.' : ''}
                className={`${buttonBaseClass} bg-yellow-50/80 hover:bg-yellow-100 hover:border-yellow-200`}
              >
                <div className="text-yellow-600">
                  {umlLoading.class ? (
                    <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                  ) : (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                    </svg>
                  )}
                </div>
                <span className="font-medium text-slate-700 text-xs leading-tight">Class<br />Diagram</span>
              </button>

              <button
                onClick={handleGenerateActivity}
                disabled={!canGenerateDependentDiagrams || umlLoading.activity}
                title={!canGenerateDependentDiagrams ? 'Generate Use Case and Class first.' : ''}
                className={`${buttonBaseClass} bg-emerald-50/60 hover:bg-emerald-100/80 hover:border-emerald-200`}
              >
                <div className="text-emerald-600">
                  {umlLoading.activity ? (
                    <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                  ) : (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5" />
                    </svg>
                  )}
                </div>
                <span className="font-medium text-slate-700 text-xs leading-tight">Activity<br />Diagram</span>
              </button>

              <button
                onClick={handleGenerateSequence}
                disabled={!canGenerateDependentDiagrams || umlLoading.sequence || selectedUsecaseIdx === null}
                title={!canGenerateDependentDiagrams ? 'Generate Use Case and Class first.' : ''}
                className={`${buttonBaseClass} bg-indigo-50/70 hover:bg-indigo-100/80 hover:border-indigo-200`}
              >
                <div className="text-indigo-600">
                  {umlLoading.sequence ? (
                    <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                  ) : (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5h18M3 12h18M3 19h18" />
                    </svg>
                  )}
                </div>
                <span className="font-medium text-slate-700 text-xs leading-tight">Sequence<br />Diagram</span>
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
          </div>
        </div>
      </div>
    </div>
  )
}
