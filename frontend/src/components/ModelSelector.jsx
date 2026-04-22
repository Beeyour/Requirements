import { useTranslation } from 'react-i18next' // 1. Import the hook

const PROVIDER_LABELS = {
  openai:    'OpenAI',
  anthropic: 'Anthropic',
  google:    'Google',
}

const PROVIDER_COLORS = {
  openai:    'text-green-700 bg-green-50 border-green-200',
  anthropic: 'text-orange-700 bg-orange-50 border-orange-200',
  google:    'text-blue-700 bg-blue-50 border-blue-200',
}

export default function ModelSelector({ value, onChange, models, compact = false }) {
  const { t } = useTranslation() // 2. Initialize the hook

  // value = "provider:model_name"
  const [provider, modelName] = (value || '').split(':')

  // 3. Replace hardcoded text with translation
  const displayName = models?.[provider]?.[modelName] || modelName || t('select_model')
  const providerLabel = PROVIDER_LABELS[provider] || provider
  const colorClass = PROVIDER_COLORS[provider] || 'text-slate-700 bg-slate-50 border-slate-200'

  if (compact) {
    return (
      <div className="relative inline-block">
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          // 4. TAILWIND FIX: Changed pr-6 to pe-6 (padding-end) and added text-start
          className={`appearance-none text-start text-xs font-medium px-2.5 py-1 pe-6 rounded-full border cursor-pointer focus:outline-none focus:ring-2 focus:ring-brand-500 ${colorClass}`}
        >
          {models &&
            Object.entries(models).map(([prov, modelMap]) => (
              <optgroup key={prov} label={PROVIDER_LABELS[prov] || prov}>
                {Object.entries(modelMap).map(([mKey, mName]) => (
                  <option key={mKey} value={`${prov}:${mKey}`}>
                    {mName}
                  </option>
                ))}
              </optgroup>
            ))}
        </select>
        <svg
          // 5. TAILWIND FIX: Changed right-1.5 to end-1.5
          className="pointer-events-none absolute end-1.5 top-1/2 -translate-y-1/2 w-3 h-3 opacity-60"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    )
  }

  return (
    <div>
      {models && (
        <div className="relative">
          <select
            value={value}
            onChange={(e) => onChange(e.target.value)}
            // 6. TAILWIND FIX: Changed pr-9 to pe-9 and added text-start
            className="w-full appearance-none border border-slate-300 rounded-lg px-3 py-2.5 pe-9 text-start text-sm text-slate-800 bg-white focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent cursor-pointer"
          >
            {Object.entries(models).map(([prov, modelMap]) => (
              <optgroup key={prov} label={PROVIDER_LABELS[prov] || prov}>
                {Object.entries(modelMap).map(([mKey, mName]) => (
                  <option key={mKey} value={`${prov}:${mKey}`}>
                    {mName}
                  </option>
                ))}
              </optgroup>
            ))}
          </select>
          <svg
            // 7. TAILWIND FIX: Changed right-3 to end-3
            className="pointer-events-none absolute end-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      )}
      {value && (
        // Added text-start here just to ensure the caption respects RTL naturally
        <p className="mt-1.5 text-xs text-slate-400 text-start">
          {providerLabel} &mdash; {displayName}
        </p>
      )}
    </div>
  )
}