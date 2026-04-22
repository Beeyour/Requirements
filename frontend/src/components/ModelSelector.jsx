import { useTranslation } from 'react-i18next'

const PROVIDER_LABELS = {
  openai:   'OpenAI',
  anthropic: 'Anthropic',
  google:    'Google',
}

const PROVIDER_COLORS = {
  openai:    'text-green-700 bg-green-50 border-green-200',
  anthropic: 'text-orange-700 bg-orange-50 border-orange-200',
  google:    'text-blue-700 bg-blue-50 border-blue-200',
}

export default function ModelSelector({ value, onChange, models, compact = false }) {
  const { t } = useTranslation()

  const [provider, modelName] = (value || '').split(':')
  const displayName = models?.[provider]?.[modelName] || modelName || t('select_model')
  const colorClass = PROVIDER_COLORS[provider] || 'text-slate-700 bg-slate-50 border-slate-200'

  // Common select options shared between both modes
  const options = models && Object.entries(models).map(([prov, modelMap]) => (
    <optgroup key={prov} label={PROVIDER_LABELS[prov] || prov}>
      {Object.entries(modelMap).map(([mKey, mName]) => (
        <option key={mKey} value={`${prov}:${mKey}`}>
          {mName}
        </option>
      ))}
    </optgroup>
  ))

  if (compact) {
    return (
      <div className="relative inline-block group">
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className={`appearance-none text-start text-xs font-semibold px-3 py-1.5 pe-7 rounded-full border cursor-pointer focus:outline-none focus:ring-2 focus:ring-brand-500 transition-colors ${colorClass}`}
        >
          {options}
        </select>
        <div className="pointer-events-none absolute end-2 top-1/2 -translate-y-1/2">
          <svg className="w-3.5 h-3.5 opacity-60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>
    )
  }

  return (
    <div className="w-full">
      <div className="relative">
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-full appearance-none border border-slate-300 rounded-lg px-4 py-3 pe-10 text-start text-sm font-medium text-slate-800 bg-white hover:border-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent cursor-pointer transition-all shadow-sm"
        >
          {options}
        </select>
        
        {/* Absolute positioned indicator for the model name if you want a custom label overlay, 
            but standard <select> shows the active option text by default. 
            The icon below provides the "dropdown" affordance. */}
        <div className="pointer-events-none absolute end-3 top-1/2 -translate-y-1/2 flex items-center">
          <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l4 4 4-4" />
          </svg>
        </div>
      </div>
      
      {value && (
        <div className="mt-2 flex items-center gap-2 px-1">
          <span className={`text-[10px] uppercase tracking-wider font-bold px-1.5 py-0.5 rounded border ${colorClass}`}>
            {PROVIDER_LABELS[provider] || provider}
          </span>
          <span className="text-xs text-slate-400">
            {t('currently_active')}
          </span>
        </div>
      )}
    </div>
  )
}