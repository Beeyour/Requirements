import { useTranslation } from 'react-i18next'

const PROVIDER_LABELS = {
  openai:    'OpenAI',
  anthropic: 'Anthropic',
  google:    'Google',
}

const PROVIDER_COLORS = {
  openai:    'text-green-700 bg-green-50 border-green-200 hover:bg-green-100',
  anthropic: 'text-orange-700 bg-orange-50 border-orange-200 hover:bg-orange-100',
  google:    'text-blue-700 bg-blue-50 border-blue-200 hover:bg-blue-100',
}

export default function ModelSelector({ value, onChange, models }) {
  const { t } = useTranslation()

  const [provider, modelName] = (value || '').split(':')
  const colorClass = PROVIDER_COLORS[provider] || 'text-slate-700 bg-slate-50 border-slate-200 hover:bg-slate-100'

  return (
    <div className="flex items-center gap-3 py-2">
      <span className="text-sm font-medium text-slate-500 whitespace-nowrap">
        {t('model')}:
      </span>

      <div className="relative group">
        {/* The "Badge" is now a styled select element */}
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className={`
            appearance-none cursor-pointer
            text-xs font-semibold px-3 py-1.5 pe-8
            rounded-full border transition-all duration-200
            focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-brand-500
            ${colorClass}
          `}
        >
          {!value && <option value="">{t('select_model')}</option>}
          
          {models && Object.entries(models).map(([prov, modelMap]) => (
            <optgroup key={prov} label={PROVIDER_LABELS[prov] || prov}>
              {Object.entries(modelMap).map(([mKey, mName]) => (
                <option key={mKey} value={`${prov}:${mKey}`}>
                  {PROVIDER_LABELS[prov]} — {mName}
                </option>
              ))}
            </optgroup>
          ))}
        </select>

        {/* Custom Chevron Icon */}
        <div className="pointer-events-none absolute end-2.5 top-1/2 -translate-y-1/2">
          <svg 
            className="w-3.5 h-3.5 opacity-50 group-hover:opacity-80 transition-opacity" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>
    </div>
  )
}