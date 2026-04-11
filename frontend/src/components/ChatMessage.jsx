export default function ChatMessage({ message }) {
  const isUser = message.role === 'user'

  const time = new Date().toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  })//

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-brand-600 flex items-center justify-center text-white text-xs font-bold mr-2 flex-shrink-0 mt-1">
          AI
        </div>
      )}
      <div className={`max-w-[75%] ${isUser ? 'items-end' : 'items-start'} flex flex-col`}>
        <div
          className={`px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap ${
            isUser
              ? 'bg-brand-600 text-white rounded-br-sm'
              : 'bg-white border border-slate-200 text-slate-800 rounded-bl-sm shadow-sm'
          }`}
        >
          {message.content}
        </div>
        <span className="text-xs text-slate-400 mt-1 px-1">{time}</span>
      </div>
      {isUser && (
        <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center text-slate-600 text-xs font-bold ml-2 flex-shrink-0 mt-1">
          You
        </div>
      )}
    </div>
  )
}
