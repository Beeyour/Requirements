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
  // value = "provider:model_name"
  const [provider, modelName] = (value || '').split(':')

  const displayName = models?.[provider]?.[modelName] || modelName || 'Select model'
  const providerLabel = PROVIDER_LABELS[provider] || provider
  const colorClass = PROVIDER_COLORS[provider] || 'text-slate-700 bg-slate-50 border-slate-200'

  if (compact) {
    return (
      <div className="relative inline-block">
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className={`appearance-none text-xs font-medium px-2.5 py-1 pr-6 rounded-full border cursor-pointer focus:outline-none focus:ring-2 focus:ring-brand-500 ${colorClass}`}
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
          className="pointer-events-none absolute right-1.5 top-1/2 -translate-y-1/2 w-3 h-3 opacity-60"
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
            className="w-full appearance-none border border-slate-300 rounded-lg px-3 py-2.5 pr-9 text-sm text-slate-800 bg-white focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent cursor-pointer"
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
            className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      )}
      {value && (
        <p className="mt-1.5 text-xs text-slate-400">
          {providerLabel} &mdash; {displayName}
        </p>
      )}
    </div>
  )
}
