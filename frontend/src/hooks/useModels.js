import { useState, useEffect, useCallback } from 'react'
import apiClient from '../api/client'

export function useModels() {
  const [models, setModels] = useState(null)
  const [defaultModel, setDefaultModel] = useState('openai:gpt-4o')

  const fetchModels = useCallback(async () => {
    try {
      const { data } = await apiClient.get('/models')
      setModels(data.providers)
      setDefaultModel(`${data.default_provider}:${data.default_model}`)
    } catch {
      // fallback — still functional with OpenAI only
      setModels({ openai: { 'gpt-4o': 'GPT-4o' } })
    }
  }, [])

  useEffect(() => { fetchModels() }, [fetchModels])

  return { models, defaultModel }
}
