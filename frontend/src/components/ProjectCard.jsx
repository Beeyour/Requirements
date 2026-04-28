import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

const PROVIDER_LABELS = { openai: 'OpenAI', anthropic: 'Anthropic', google: 'Google' }
const PROVIDER_COLORS = {
  openai:    'bg-green-50 text-green-700',
  anthropic: 'bg-orange-50 text-orange-700',
  google:    'bg-blue-50 text-blue-700',
}

export default function ProjectCard({ project, onDelete, viewMode = 'grid' }) {
  const navigate = useNavigate()
  const { t, i18n } = useTranslation()
  const formatted = new Date(project.created_at).toLocaleDateString(i18n.language, {
    year: 'numeric', month: 'short', day: 'numeric',
  })
  const providerLabel = PROVIDER_LABELS[project.model_provider] || project.model_provider
  const providerColor = PROVIDER_COLORS[project.model_provider] || 'bg-slate-50 text-slate-600'
  // ================= LIST VIEW FORMAT =================
  if (viewMode === 'list') {
    return (
      <div 
        onClick={() => navigate(`/project/${project.id}/interview`)}
        className="grid grid-cols-[4fr_3fr_3fr_3fr_48px] items-center gap-4 py-4 px-6 border-b border-slate-100 last:border-0 hover:bg-slate-50 transition-colors group cursor-pointer text-left"
      >
        <div className="flex items-center gap-3">
          <span className="text-xl">💻</span>
          <span className="font-medium text-slate-800">{project.app_name}</span>
        </div>
        <div className="text-sm text-slate-600">{formatted}</div>
        <div>
          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${providerColor}`}>
            {providerLabel}
          </span>
        </div>
        <div className="text-sm text-slate-600">
          {project.requirement_count} {project.requirement_count !== 1 ? t('reqs_plural') : t('req_singular')}
        </div>
        <div className="flex justify-end">
          <button
            onClick={(e) => { e.stopPropagation(); onDelete(project.id) }}
            className="text-slate-400 hover:text-red-600 p-2 rounded-full hover:bg-slate-100 transition-colors opacity-0 group-hover:opacity-100"
            title={t('delete_project_title')}
          >
            {/* 3 vertical dots icon matching the screenshot */}
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
            </svg>
          </button>
        </div>
      </div>
    )
  }

  // ================= GRID VIEW FORMAT (Original) =================
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 hover:border-brand-300 hover:shadow-md transition-all group text-start">
      <div className="flex items-start justify-between mb-3">
        <h3 className="font-semibold text-slate-800 text-lg leading-tight group-hover:text-brand-600 transition-colors">
          {project.app_name}
        </h3>
        <button
          onClick={(e) => { e.stopPropagation(); onDelete(project.id) }}
          className="text-slate-300 hover:text-red-500 transition-colors ms-2 flex-shrink-0"
          title={t('delete_project_title')}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      <p className="text-sm text-slate-500 mb-3">{formatted}</p>
      <div className="flex items-center gap-2 mb-4 flex-wrap">
        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${providerColor}`}>
          {providerLabel}
        </span>
        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-600">
          {project.requirement_count} {project.requirement_count !== 1 ? t('reqs_plural') : t('req_singular')}
        </span>
      </div>
      <div className="flex gap-2">
        <button
          onClick={() => navigate(`/project/${project.id}/interview`)}
          className="flex-1 py-2 px-3 text-sm font-medium text-brand-600 border border-brand-200 rounded-lg hover:bg-brand-50 transition-colors"
        >
          {t('interview_btn')}
        </button>
        {project.requirement_count > 0 && (
          <button
            onClick={() => navigate(`/project/${project.id}/srs`)}
            className="flex-1 py-2 px-3 text-sm font-medium text-white bg-brand-600 rounded-lg hover:bg-brand-700 transition-colors"
          >
            {t('view_srs_btn')}
          </button>
        )}
      </div>
    </div>
  )
}