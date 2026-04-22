import { useTranslation } from 'react-i18next'

export default function ChatMessage({ message }) {
  const { t, i18n } = useTranslation()
  const isUser = message.role === 'user'

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
        <span className="text-xs text-slate-400 mt-1 px-1">{time}</span>
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