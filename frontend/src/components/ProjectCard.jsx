import { useNavigate } from 'react-router-dom'

const PROVIDER_LABELS = { openai: 'OpenAI', anthropic: 'Anthropic', google: 'Google' }
const PROVIDER_COLORS = {
  openai:    'bg-green-50 text-green-700',
  anthropic: 'bg-orange-50 text-orange-700',
  google:    'bg-blue-50 text-blue-700',
}

export default function ProjectCard({ project, onDelete }) {
  const navigate = useNavigate()

  const formatted = new Date(project.created_at).toLocaleDateString(undefined, {
    year: 'numeric', month: 'short', day: 'numeric',
  })

  const providerLabel = PROVIDER_LABELS[project.model_provider] || project.model_provider
  const providerColor = PROVIDER_COLORS[project.model_provider] || 'bg-slate-50 text-slate-600'

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 hover:border-brand-300 hover:shadow-md transition-all group">
      <div className="flex items-start justify-between mb-3">
        <h3 className="font-semibold text-slate-800 text-lg leading-tight group-hover:text-brand-600 transition-colors">
          {project.app_name}
        </h3>
        <button
          onClick={(e) => { e.stopPropagation(); onDelete(project.id) }}
          className="text-slate-300 hover:text-red-500 transition-colors ml-2 flex-shrink-0"
          title="Delete project"
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
          {project.requirement_count} req{project.requirement_count !== 1 ? 's' : ''}
        </span>
      </div>

      <div className="flex gap-2">
        <button
          onClick={() => navigate(`/project/${project.id}/interview`)}
          className="flex-1 py-2 px-3 text-sm font-medium text-brand-600 border border-brand-200 rounded-lg hover:bg-brand-50 transition-colors"
        >
          Interview
        </button>
        {project.requirement_count > 0 && (
          <button
            onClick={() => navigate(`/project/${project.id}/srs`)}
            className="flex-1 py-2 px-3 text-sm font-medium text-white bg-brand-600 rounded-lg hover:bg-brand-700 transition-colors"
          >
            View SRS
          </button>
        )}
      </div>
    </div>
  )
}
