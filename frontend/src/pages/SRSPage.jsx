import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next' // 1. Import the hook

import Navbar from '../components/Navbar'
import RequirementCard from '../components/RequirementCard'
import EditModal from '../components/EditModal'
import { useRequirements } from '../hooks/useRequirements'
import apiClient from '../api/client'

export default function SRSPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const projectId = parseInt(id)
  
  const { t } = useTranslation() // 2. Initialize the hook

  const [projectName, setProjectName] = useState('')
  const [activeTab, setActiveTab] = useState('Functional')
  const [editingReq, setEditingReq] = useState(null)
  const [saving, setSaving] = useState(false)
  const [conflictMap, setConflictMap] = useState({})

  const { requirements, loading, error, fetchRequirements, updateRequirement } =
    useRequirements(projectId)

  useEffect(() => {
    apiClient.get(`/projects/${projectId}`).then(({ data }) => setProjectName(data.app_name))
    fetchRequirements()
  }, [projectId, fetchRequirements])

  const functional = requirements.filter((r) => r.type === 'Functional')
  const nonFunctional = requirements.filter((r) => r.type === 'Non-Functional')
  const displayed = activeTab === 'Functional' ? functional : nonFunctional

  const handleSave = async (reqId, description, changeReason) => {
    setSaving(true)
    try {
      const result = await updateRequirement(reqId, description, changeReason)
      if (result.conflict_report?.has_conflicts) {
        setConflictMap((prev) => ({ ...prev, [result.requirement.id]: true }))
      } else {
        setConflictMap((prev) => {
          const next = { ...prev }
          delete next[result.requirement.id]
          return next
        })
      }
      return result
    } finally {
      setSaving(false)
    }
  }

  // 3. Translate the tab labels dynamically using the keys we set earlier
  const tabs = [
    { key: 'Functional', label: t('Functional'), count: functional.length, color: 'blue' },
    { key: 'Non-Functional', label: t('Non-Functional'), count: nonFunctional.length, color: 'purple' },
  ]

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar projectName={projectName} backTo={`/project/${id}/interview`} backLabel={t('interview_back')} />

      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-between mb-6">
          <div className="text-start">
            <h1 className="text-2xl font-bold text-slate-900">{projectName}</h1>
            <p className="text-slate-500 text-sm mt-1">
              {t('srs_title')} &mdash; {requirements.length} {t('total_reqs')}
            </p>
          </div>
          <button
            onClick={() => navigate(`/project/${id}/interview`)}
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-brand-600 border border-brand-200 rounded-lg hover:bg-brand-50 transition-colors"
          >
            {/* Flip arrow if RTL */}
            <svg className="w-4 h-4 rtl:-scale-x-100" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            {t('continue_interview')}
          </button>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700 text-start">
            {error}
          </div>
        )}

        {Object.keys(conflictMap).length > 0 && (
          <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-lg text-sm text-amber-800 flex items-center gap-2 text-start">
            <svg className="w-4 h-4 text-amber-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <span>
              {Object.keys(conflictMap).length}{' '}
              {Object.keys(conflictMap).length !== 1 ? t('req_has_conflict_plural') : t('req_has_conflict_singular')}
            </span>
          </div>
        )}

        <div className="flex border-b border-slate-200 mb-6">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`px-5 py-3 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${
                activeTab === tab.key
                  ? tab.color === 'blue'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-purple-600 text-purple-600'
                  : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
            >
              {tab.label}
              <span
                className={`text-xs px-1.5 py-0.5 rounded-full font-semibold ${
                  activeTab === tab.key
                    ? tab.color === 'blue'
                      ? 'bg-blue-100 text-blue-700'
                      : 'bg-purple-100 text-purple-700'
                    : 'bg-slate-100 text-slate-500'
                }`}
              >
                {tab.count}
              </span>
            </button>
          ))}
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-16">
            <svg className="w-6 h-6 animate-spin text-slate-400" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          </div>
        ) : displayed.length === 0 ? (
          <div className="text-center py-16 text-slate-400">
            {/* 4. Use interpolation to inject the correct translated category name */}
            <p className="text-sm">
              {t('no_reqs_yet', { 
                type: t(activeTab === 'Functional' ? 'functional_lower' : 'non_functional_lower') 
              })}
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {displayed.map((req) => (
              <RequirementCard
                key={req.id}
                requirement={req}
                hasConflict={!!conflictMap[req.id]}
                onEdit={setEditingReq}
              />
            ))}
          </div>
        )}
      </main>

      <EditModal
        requirement={editingReq}
        onSave={handleSave}
        onClose={() => setEditingReq(null)}
        saving={saving}
      />
    </div>
  )
}