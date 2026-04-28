import { useState, useCallback } from 'react'
import apiClient from '../api/client'

export function useRequirements(projectId) {
  const [requirements, setRequirements] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const fetchRequirements = useCallback(async () => {
    if (!projectId) return
    setLoading(true)
    setError(null)
    try {
      const { data } = await apiClient.get(`/requirements/${projectId}`)
      setRequirements(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load requirements')
    } finally {
      setLoading(false)
    }
  }, [projectId])
  const generateSRS = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const { data } = await apiClient.post('/generate-srs', { project_id: projectId })
      setRequirements(data)
      return data
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate SRS')
      return null
    } finally {
      setLoading(false)
    }
  }, [projectId])
  const updateRequirement = useCallback(async (id, description, changeReason) => {
    const { data } = await apiClient.put(`/requirements/update-requirement/${id}`, {
      description,
      change_reason: changeReason,
    })
    setRequirements((prev) =>
      prev.map((r) => (r.id === id ? data.requirement : r)).filter((r) => r.is_active),
    )
    return data
  }, [])
  return {
    requirements,
    loading,
    error,
    fetchRequirements,
    generateSRS,
    updateRequirement,
  }
}
