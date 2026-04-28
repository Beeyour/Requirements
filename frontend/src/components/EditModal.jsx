import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next' // 1. Import the hook
import ConflictReport from './ConflictReport'

export default function EditModal({ requirement, onSave, onClose, saving }) {
  const { t } = useTranslation() // 2. Initialize the hook
  const [description, setDescription] = useState(requirement?.description || '')
  const [changeReason, setChangeReason] = useState('')
  const [conflictReport, setConflictReport] = useState(null)
  const [saved, setSaved] = useState(false)
  useEffect(() => {
    if (requirement) {
      setDescription(requirement.description)
      setChangeReason('')
      setConflictReport(null)
      setSaved(false)
    }
  }, [requirement])
  if (!requirement) return null
  const handleSave = async () => {
    const result = await onSave(requirement.id, description, changeReason)
    if (result) {
      setConflictReport(result.conflict_report || null)
      setSaved(true)
    }
  }
  const hasChanged = description.trim() !== requirement.description.trim()
  return (
    // 3. Added 'text-start' to the wrapper to ensure text aligns correctly based on language direction
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4 text-start">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-slate-800">{t('edit_req_title')}</h2>
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-slate-600 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div className="flex items-center gap-2 mb-4">
            <span
              className={`text-xs font-medium px-2 py-0.5 rounded-full border ${
                requirement.type === 'Functional'
                  ? 'bg-blue-100 text-blue-700 border-blue-200'
                  : 'bg-purple-100 text-purple-700 border-purple-200'
              }`}
            >
              {/* Translate the requirement type badge dynamically */}
              {t(requirement.type)}
            </span>
            <span className="text-xs text-slate-400 font-mono">
              {t('version_prefix')}{requirement.version_number}
            </span>
          </div>
          <div className="mb-4">
            <label className="block text-sm font-medium text-slate-700 mb-1">
              {t('description_label')}
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={5}
              // Added text-start here
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent resize-none text-start"
              placeholder={t('desc_placeholder')}
            />
          </div>
          <div className="mb-5">
            <label className="block text-sm font-medium text-slate-700 mb-1">
              {t('reason_label')} <span className="text-slate-400 font-normal">{t('optional')}</span>
            </label>
            <input
              type="text"
              value={changeReason}
              onChange={(e) => setChangeReason(e.target.value)}
              // Added text-start here
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent text-start"
              placeholder={t('reason_placeholder')}
            />
          </div>
          {saved && !conflictReport && (
            <p className="text-sm text-green-600 mb-4 flex items-center gap-1">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clipRule="evenodd"
                />
              </svg>
              {t('save_success')}
            </p>
          )}
          <ConflictReport report={conflictReport} />
          <div className="flex gap-3 mt-5">
            <button
              onClick={onClose}
              className="flex-1 py-2 px-4 text-sm font-medium text-slate-700 border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors"
            >
              {saved ? t('close') : t('cancel')}
            </button>
            {!saved && (
              <button
                onClick={handleSave}
                disabled={!hasChanged || saving || !description.trim()}
                className="flex-1 py-2 px-4 text-sm font-medium text-white bg-brand-600 rounded-lg hover:bg-brand-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
              >
                {saving && (
                  <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                    />
                  </svg>
                )}
                {t('save_check_conflicts')}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}