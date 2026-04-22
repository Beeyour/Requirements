import { useState, useCallback } from 'react'
import apiClient from '../api/client'

export function useProjects() {
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchProjects = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const { data } = await apiClient.get('/projects/')
      setProjects(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load projects')
    } finally {
      setLoading(false)
    }
  }, [])

  const createProject = useCallback(async (appName, modelProvider, modelName) => {
    const { data } = await apiClient.post('/projects/', {
      app_name: appName,
      model_provider: modelProvider,
      model_name: modelName,
    })
    setProjects((prev) => [data, ...prev])
    return data
  }, [])

  const updateModel = useCallback(async (projectId, modelProvider, modelName) => {
    const { data } = await apiClient.patch(`/projects/${projectId}/model`, {
      model_provider: modelProvider,
      model_name: modelName,
    })
    setProjects((prev) => prev.map((p) => (p.id === projectId ? data : p)))
    return data
  }, [])

  const deleteProject = useCallback(async (id) => {
    await apiClient.delete(`/projects/${id}`)
    setProjects((prev) => prev.filter((p) => p.id !== id))
  }, [])

  return { projects, loading, error, fetchProjects, createProject, updateModel, deleteProject }
}
