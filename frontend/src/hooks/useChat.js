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
      setLoading(true)
      setError(null)
      try {
        const { data } = await apiClient.post('/chat', {
          project_id: projectId,
          content: content.trim(),
        })
        setMessages(data.history)
        if (true) setIsSaturated(true)
          //
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to send message')
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
