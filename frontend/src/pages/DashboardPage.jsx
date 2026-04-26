import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

import Navbar from '../components/Navbar'
import ProjectCard from '../components/ProjectCard'
import ModelSelector from '../components/ModelSelector'
import { useProjects } from '../hooks/useProjects'
import { useModels } from '../hooks/useModels'

export default function DashboardPage() {
  const navigate = useNavigate()
  const { t } = useTranslation()

  const { projects, loading, error, fetchProjects, createProject, deleteProject } = useProjects()
  const { models, defaultModel } = useModels()

  const [showCreate, setShowCreate] = useState(false)
  const [newName, setNewName] = useState('')
  const [selectedModel, setSelectedModel] = useState(defaultModel)
  const [creating, setCreating] = useState(false)
  const [deleteConfirm, setDeleteConfirm] = useState(null)
  
  // NEW: State for the Grid vs List view toggle
  const [viewMode, setViewMode] = useState('grid')

  useEffect(() => { fetchProjects() }, [fetchProjects])
  useEffect(() => { setSelectedModel(defaultModel) }, [defaultModel])

  const handleCreate = async (e) => {
    e.preventDefault()
    if (!newName.trim()) return
    setCreating(true)
    try {
      const [provider, model] = selectedModel.split(':')
      const project = await createProject(newName.trim(), provider, model)
      setShowCreate(false)
      setNewName('')
      navigate(`/project/${project.id}/interview`)
    } catch {
      // error handled in hook
    } finally {
      setCreating(false)
    }
  }

  const handleDelete = async (id) => {
    await deleteProject(id)
    setDeleteConfirm(null)
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      {/* 1. WIDENED CONTAINER: Changed max-w-6xl to max-w-[90rem] (1440px) */}
      <main className="max-w-[90rem] mx-auto w-full px-4 sm:px-6 lg:px-8 py-10">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">{t('projects')}</h1>
            <p className="text-slate-500 text-sm mt-1">
              {projects.length} {projects.length !== 1 ? t('projects_plural') : t('project_singular')}
            </p>
          </div>
          
          <div className="flex items-center gap-4">
            {/* 2. TOGGLE BUTTONS: Placed left of the New Project button */}
            <div className="flex items-center bg-white border border-slate-200 rounded-lg p-1 shadow-sm">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-1.5 rounded-md transition-colors ${
                  viewMode === 'grid' 
                    ? 'bg-slate-100 text-slate-800 shadow-sm' 
                    : 'text-slate-400 hover:text-slate-600 hover:bg-slate-50'
                }`}
                title="Grid View"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                </svg>
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-1.5 rounded-md transition-colors ${
                  viewMode === 'list' 
                    ? 'bg-slate-100 text-slate-800 shadow-sm' 
                    : 'text-slate-400 hover:text-slate-600 hover:bg-slate-50'
                }`}
                title="List View"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            </div>

            <button
              onClick={() => setShowCreate(true)}
              className="inline-flex items-center gap-2 px-4 py-2.5 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 transition-colors shadow-sm"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              {t('new_project')}
            </button>
          </div>
        </div>

        {showCreate && (
          <div className="mb-8 bg-white rounded-xl border border-brand-200 p-5 shadow-sm animate-in fade-in slide-in-from-top-2">
            <h3 className="font-semibold text-slate-800 mb-4">{t('new_project')}</h3>
            <form onSubmit={handleCreate} className="space-y-4 max-w-xl">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  {t('app_name_label')}
                </label>
                <input
                  type="text"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  autoFocus
                  required
                  placeholder={t('app_name_placeholder')}
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent text-start"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  {t('ai_model_label')}
                </label>
                <ModelSelector
                  value={selectedModel}
                  onChange={setSelectedModel}
                  models={models}
                />
              </div>

              <div className="flex gap-3 pt-1">
                <button
                  type="submit"
                  disabled={creating || !newName.trim()}
                  className="px-5 py-2 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 disabled:opacity-50 transition-colors"
                >
                  {creating ? t('creating') : t('create_start')}
                </button>
                <button
                  type="button"
                  onClick={() => { setShowCreate(false); setNewName('') }}
                  className="px-4 py-2 border border-slate-300 text-slate-700 text-sm font-medium rounded-lg hover:bg-slate-50 transition-colors"
                >
                  {t('cancel')}
                </button>
              </div>
            </form>
          </div>
        )}

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
            {error}
          </div>
        )}

        {loading && projects.length === 0 ? (
          <div className="flex items-center justify-center py-20">
            <div className="flex flex-col items-center gap-3 text-slate-400">
              <svg className="w-8 h-8 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              <span className="text-sm">{t('loading_projects')}</span>
            </div>
          </div>
        ) : (
          /* Conditional classes based on viewMode state */
          <div className={
            viewMode === 'grid' 
              ? "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-6" 
              : "flex flex-col gap-4 max-w-5xl w-full"
          }>
            
            {/* 3. CREATE NEW PROJECT TILE: Always shown as the first item */}
            <button
              onClick={() => setShowCreate(true)}
              className={`flex items-center justify-center bg-slate-50/50 border-2 border-dashed border-slate-300 rounded-xl hover:border-brand-400 hover:bg-brand-50/50 transition-all group text-center cursor-pointer ${
                viewMode === 'grid' 
                  ? 'flex-col p-6 min-h-[210px]' 
                  : 'flex-row p-6 h-[116px] gap-4 justify-start text-left'
              }`}
            >
              <div className={`bg-white rounded-full flex items-center justify-center shadow-sm border border-slate-200 group-hover:border-brand-300 group-hover:scale-110 transition-transform ${
                viewMode === 'grid' ? 'w-14 h-14 mb-4' : 'w-12 h-12 flex-shrink-0'
              }`}>
                <svg className="w-6 h-6 text-slate-400 group-hover:text-brand-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
              </div>
              <span className="font-semibold text-slate-600 group-hover:text-brand-700 text-lg">
                Create New Project
              </span>
            </button>

            {/* Existing Projects Mapping */}
            {projects.map((p) => (
              <ProjectCard key={p.id} project={p} onDelete={(id) => setDeleteConfirm(id)} />
            ))}
          </div>
        )}
      </main>

      {deleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="bg-white rounded-2xl shadow-xl p-6 w-full max-w-sm">
            <h3 className="font-semibold text-slate-800 mb-2">{t('delete_title')}</h3>
            <p className="text-sm text-slate-500 mb-5">
              {t('delete_desc')}
            </p>
            <div className="flex gap-3">
              <button onClick={() => setDeleteConfirm(null)} className="flex-1 py-2 border border-slate-300 text-slate-700 text-sm font-medium rounded-lg hover:bg-slate-50 transition-colors">
                {t('cancel')}
              </button>
              <button onClick={() => handleDelete(deleteConfirm)} className="flex-1 py-2 bg-red-600 text-white text-sm font-medium rounded-lg hover:bg-red-700 transition-colors">
                {t('delete')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}