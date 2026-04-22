<<<<<<< HEAD
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
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 14be973 (try to solve the issue on user bubble chat)
  async (content) => {
    if (!content.trim() || !projectId) return

    // 1. CREATE AN OPTIMISTIC MESSAGE
    // This creates a fake message object that matches your ChatMessage structure
    const optimisticUserMessage = {
      id: Date.now(), // Temporary unique ID
      role: 'user',
      content: content.trim(),
      timestamp: new Date().toISOString(),
    }

    // 2. UPDATE STATE IMMEDIATELY
    // This makes the bubble appear the millisecond the user clicks send
    setMessages((prev) => [...prev, optimisticUserMessage])
    
    setLoading(true) // This triggers the AI "bouncing dots"
    setError(null)

    try {
      const { data } = await apiClient.post('/chat', {
        project_id: projectId,
        content: content.trim(),
      })

      // 3. OVERWRITE WITH REAL DATA
      // Once the backend responds, we replace our "fake" history with the official one
      setMessages(data.history)
      
      // I noticed your code had "if (true)" - you should likely use 
      // the flag returned by your FastAPI backend here:
      if (data.is_saturated) setIsSaturated(true) 
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to send message')
      // OPTIONAL: If the call fails, remove the optimistic message so the UI stays accurate
      setMessages((prev) => prev.filter(msg => msg.id !== optimisticUserMessage.id))
    } finally {
      setLoading(false)
    }
  },
  [projectId],
)
<<<<<<< HEAD
=======
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
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to send message')
      } finally {
        setLoading(false)
      }
    },
    [projectId],
  )
>>>>>>> 2e7cd96 (Revert "try to modify useChat.js for showing the button")
=======
>>>>>>> 14be973 (try to solve the issue on user bubble chat)

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
=======
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
    // This creates a fake message object that matches your ChatMessage structure
    const optimisticUserMessage = {
      id: Date.now(), // Temporary unique ID
      role: 'user',
      content: content.trim(),
      timestamp: new Date().toISOString(),
    }

    // 2. UPDATE STATE IMMEDIATELY
    // This makes the bubble appear the millisecond the user clicks send
    setMessages((prev) => [...prev, optimisticUserMessage])
    
    setLoading(true) // This triggers the AI "bouncing dots"
    setError(null)

    try {
      const { data } = await apiClient.post('/chat', {
        project_id: projectId,
        content: content.trim(),
      })

      // 3. OVERWRITE WITH REAL DATA
      // Once the backend responds, we replace our "fake" history with the official one
      setMessages(data.history)
      
      // I noticed your code had "if (true)" - you should likely use 
      // the flag returned by your FastAPI backend here:
      if (data.is_saturated) setIsSaturated(true) 
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to send message')
      // OPTIONAL: If the call fails, remove the optimistic message so the UI stays accurate
      setMessages((prev) => prev.filter(msg => msg.id !== optimisticUserMessage.id))
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
>>>>>>> 5b97499 (chore: apply .gitignore and remove cached files)
