import { useState } from 'react'

export default function RequirementCard({ requirement, onEdit, hasConflict }) {
  const typeColor =
    requirement.type === 'Functional'
      ? 'bg-blue-100 text-blue-700 border-blue-200'
      : 'bg-purple-100 text-purple-700 border-purple-200'

  const borderColor = hasConflict ? 'border-amber-400 bg-amber-50' : 'border-slate-200 bg-white'

  return (
    <div className={`rounded-xl border p-4 transition-all ${borderColor}`}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2 flex-wrap">
            <span className={`text-xs font-medium px-2 py-0.5 rounded-full border ${typeColor}`}>
              {requirement.type}
            </span>
            <span className="text-xs text-slate-400 font-mono">v{requirement.version_number}</span>
            {hasConflict && (
              <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-amber-100 text-amber-700 border border-amber-200 flex items-center gap-1">
                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                    clipRule="evenodd"
                  />
                </svg>
                Conflict
              </span>
            )}
          </div>
          <p className="text-sm text-slate-700 leading-relaxed">{requirement.description}</p>
        </div>
        <button
          onClick={() => onEdit(requirement)}
          className="flex-shrink-0 p-2 text-slate-400 hover:text-brand-600 hover:bg-brand-50 rounded-lg transition-colors"
          title="Edit requirement"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
            />
          </svg>
        </button>
      </div>
    </div>
  )
}
