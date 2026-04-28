import { useTranslation } from 'react-i18next'
import { useTextToSpeech } from '../hooks/useTextToSpeech'

export default function ChatMessage({ message }) {
  const { t, i18n } = useTranslation()
  const isUser = message.role === 'user'
  const { speak, stop, isSpeaking } = useTextToSpeech()
  // THE FIX: Ensure the string is treated as UTC
  const formatTime = (rawTimestamp) => {
    if (!rawTimestamp) return ''
    // If the string doesn't end with 'Z', add it to force UTC interpretation
    const utcString = rawTimestamp.endsWith('Z') ? rawTimestamp : `${rawTimestamp}Z`
    return new Date(utcString).toLocaleTimeString(i18n.language, {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true,
    })
  }
  const time = formatTime(message.timestamp)
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      {/* AI Avatar */}
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-brand-600 flex items-center justify-center text-white text-xs font-bold me-2 flex-shrink-0 mt-1">
          AI
        </div>
      )}
      {/* Message Bubble Container */}
      <div className={`max-w-[75%] ${isUser ? 'items-end' : 'items-start'} flex flex-col`}>
        <div
          className={`px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap text-start ${isUser
              ? 'bg-brand-600 text-white rounded-ee-sm'
              : 'bg-white border border-slate-200 text-slate-800 rounded-es-sm shadow-sm'
            }`}
        >
          {message.content}
        </div>
        {/* Time and Audio Controls Container */}
        <div className="flex items-center gap-2 mt-1 px-1">
          <span className="text-xs text-slate-400">{time}</span>
          {/* 3. ONLY show the speaker icon for AI messages */}
          {!isUser && (
            <button
              onClick={() => isSpeaking ? stop() : speak(message.content)}
              className={`text-slate-400 hover:text-brand-600 transition-colors ${isSpeaking ? 'text-brand-600' : ''}`}
              title={isSpeaking ? "Stop playback" : "Listen to message"}
            >
              {isSpeaking ? (
                // Stop/Square Icon
                <svg className="w-3.5 h-3.5 animate-pulse" fill="currentColor" viewBox="0 0 20 20">
                  <rect x="5" y="5" width="10" height="10" />
                </svg>
              ) : (
                // Play/Speaker Icon
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                </svg>
              )}
            </button>
          )}
        </div>
      </div>
      {/* User Avatar */}
      {isUser && (
        <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center text-slate-600 text-xs font-bold ms-2 flex-shrink-0 mt-1">
          You
        </div>
      )}
    </div>
  )
}