import { useState, useCallback } from 'react'
import apiClient from '../api/client'

export function useChat(projectId) {
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [isSaturated, setIsSaturated] = useState(false)
  const [error, setError] = useState(null)

  const loadHistory = useCallback(async () => {
    if (!projectId) return
    setLoading(true)
    try {
      const { data } = await apiClient.get(`/chat/${projectId}/history`)
      setMessages(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load history')
    } finally {
      setLoading(false)
    }
  }, [projectId])

  const startInterview = useCallback(async () => {
    if (!projectId) return
    try {
      const { data } = await apiClient.post(`/chat/${projectId}/start`)
      setMessages([data])
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start interview')
    }
  }, [projectId])

  const sendMessage = useCallback(
    async (content) => {
      if (!content.trim() || !projectId) return

      // 1. CREATE AN OPTIMISTIC MESSAGE
      const optimisticUserMessage = {
        id: Date.now(),
        role: 'user',
        content: content.trim(),
        timestamp: new Date().toISOString(),
      }

      // 2. UPDATE STATE IMMEDIATELY
      setMessages((prev) => [...prev, optimisticUserMessage])
      
      setLoading(true) 
      setError(null)

      try {
        const { data } = await apiClient.post('/chat', {
          project_id: projectId,
          content: content.trim(),
        })

        // 3. OVERWRITE WITH REAL DATA
        setMessages(data.history)
        if (data.is_saturated) setIsSaturated(true) 
        
      } catch (err) {
        console.error("Chat API Error:", err)
        throw err; 

      } finally {
        setLoading(false)
      }
    },
    [projectId],
  )

  const resetConversation = useCallback(async () => {
    await apiClient.post('/chat/reset', { project_id: projectId })
    setMessages([])
    setIsSaturated(false)
  }, [projectId])

  return {
    messages,
    loading,
    isSaturated,
    error,
    loadHistory,
    startInterview,
    sendMessage,
    resetConversation,
  }
}
