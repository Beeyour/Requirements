import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

import Navbar from '../components/Navbar'
import apiClient from '../api/client'

export default function DiagramViewerPage() {
  const { id: projectId, type: diagramType } = useParams()
  const navigate = useNavigate()
  const { t } = useTranslation()

  const [project, setProject] = useState(null)
  const [diagramSvg, setDiagramSvg] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [useCases, setUseCases] = useState([])
  const svgContainerRef = useRef(null)

  useEffect(() => {
    const fetchProject = async () => {
      try {
        const { data } = await apiClient.get(`/projects/${projectId}`)
        setProject(data)
      } catch (err) {
        setError('Failed to load project')
      }
    }
    fetchProject()
  }, [projectId])

  useEffect(() => {
    const fetchDiagram = async () => {
      setLoading(true)
      setError(null)
      
      try {
        let endpoint
        switch (diagramType) {
          case 'usecase':
            endpoint = `/generate-usecase/${projectId}`
            break
          case 'class':
            endpoint = `/generate-class/${projectId}`
            break
          case 'activity':
            endpoint = `/generate-activity/${projectId}`
            break
          case 'sequence':
            // For sequence diagrams, we need a usecase_idx
            const urlParams = new URLSearchParams(window.location.search)
            const usecaseIdx = urlParams.get('usecase_idx')
            if (!usecaseIdx) {
              throw new Error('Sequence diagram requires usecase_idx parameter')
            }
            endpoint = `/generate-sequence/${projectId}/${usecaseIdx}`
            break
          default:
            throw new Error('Invalid diagram type')
        }

        const { data } = await apiClient.get(endpoint)
        
        if (data.svg_url) {
          setDiagramSvg(data.svg_url)
        }
        
        // Store use cases for interactive navigation
        if (data.data?.use_cases) {
          setUseCases(data.data.use_cases)
        }
        
      } catch (err) {
        setError(err.response?.data?.detail || err.message || 'Failed to load diagram')
      } finally {
        setLoading(false)
      }
    }

    if (projectId && diagramType) {
      fetchDiagram()
    }
  }, [projectId, diagramType])

  const handleSvgClick = (event) => {
    // Only handle clicks for use case diagrams
    if (diagramType !== 'usecase') return

    const target = event.target
    if (target.tagName === 'ellipse' || target.tagName === 'text') {
      // Try to find the use case name from the text or parent element
      let useCaseName = ''
      let useCaseIndex = -1

      if (target.tagName === 'text') {
        useCaseName = target.textContent?.trim()
      } else if (target.tagName === 'ellipse') {
        // Look for the associated text element
        const parent = target.parentElement
        const textElement = parent?.querySelector('text')
        useCaseName = textElement?.textContent?.trim()
      }

      // Find the use case index
      const foundIndex = useCases.findIndex(name => 
        name.toLowerCase().includes(useCaseName.toLowerCase()) ||
        useCaseName.toLowerCase().includes(name.toLowerCase())
      )

      if (foundIndex !== -1) {
        navigate(`/project/${projectId}/diagram/sequence?usecase_idx=${foundIndex}`)
      }
    }
  }

  const getDiagramTitle = () => {
    switch (diagramType) {
      case 'usecase': return 'Use Case Diagram'
      case 'class': return 'Class Diagram'
      case 'activity': return 'Activity Diagram'
      case 'sequence': return 'Sequence Diagram'
      default: return 'Diagram'
    }
  }

  const getBackPath = () => {
    if (diagramType === 'sequence') {
      return `/project/${projectId}/diagram/usecase`
    }
    return `/project/${projectId}/interview`
  }

  if (loading) {
    return (
      <div className="h-screen bg-slate-100 flex flex-col overflow-hidden">
        <div className="flex-none z-50 bg-white shadow-sm border-b border-slate-200/50">
          <Navbar projectName={project?.app_name || 'Loading...'} backTo={getBackPath()} backLabel="Back" />
        </div>
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-slate-600">Loading diagram...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="h-screen bg-slate-100 flex flex-col overflow-hidden">
        <div className="flex-none z-50 bg-white shadow-sm border-b border-slate-200/50">
          <Navbar projectName={project?.app_name || 'Error'} backTo={getBackPath()} backLabel="Back" />
        </div>
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center max-w-md mx-auto p-6">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-slate-900 mb-2">Error Loading Diagram</h3>
            <p className="text-slate-600">{error}</p>
            <button
              onClick={() => navigate(getBackPath())}
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Go Back
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen bg-slate-100 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="flex-none z-50 bg-white shadow-sm border-b border-slate-200/50">
        <Navbar 
          projectName={project?.app_name || 'Diagram Viewer'} 
          backTo={getBackPath()} 
          backLabel={diagramType === 'sequence' ? 'Back to Use Case' : 'Back to Interview'} 
        />
        
        <div className="px-6 py-4 bg-slate-50/50 border-t border-slate-100">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-semibold text-slate-900">{getDiagramTitle()}</h1>
              {diagramType === 'usecase' && useCases.length > 0 && (
                <p className="text-sm text-slate-600 mt-1">
                  Click on any use case to view its sequence diagram
                </p>
              )}
            </div>
            <div className="flex items-center gap-2">
              {diagramType === 'usecase' && (
                <span className="px-3 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded-full">
                  Interactive
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
            <div className="p-6">
              {diagramSvg ? (
                <div 
                  ref={svgContainerRef}
                  className={`w-full h-auto ${diagramType === 'usecase' ? 'cursor-pointer' : ''}`}
                  onClick={handleSvgClick}
                  dangerouslySetInnerHTML={{ __html: diagramSvg }}
                />
              ) : (
                <div className="text-center py-12">
                  <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-slate-900 mb-2">No Diagram Available</h3>
                  <p className="text-slate-600">
                    {diagramType === 'sequence' 
                      ? 'Please generate a use case diagram first to access sequence diagrams.'
                      : 'This diagram has not been generated yet.'}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
