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
        
        // Fetch the actual SVG content from the URL
        if (data.svg_url) {
          try {
            const svgResponse = await fetch(data.svg_url)
            const svgContent = await svgResponse.text()
            setDiagramSvg(svgContent)
          } catch (svgError) {
            console.error('Failed to fetch SVG content:', svgError)
            setError('Failed to load diagram content')
          }
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
    console.log('SVG clicked:', target.tagName, target.textContent?.trim())
    
    // Find the use case name using multiple strategies
    let useCaseName = ''

    // Strategy 1: Direct text click
    if (target.tagName === 'text') {
      useCaseName = target.textContent?.trim()
      console.log('Direct text found:', useCaseName)
    }
    // Strategy 2: Ellipse click - find associated text
    else if (target.tagName === 'ellipse') {
      // Look for text in the same group or nearby
      const parent = target.parentElement
      if (parent) {
        const textElement = parent.querySelector('text')
        if (textElement) {
          useCaseName = textElement.textContent?.trim()
          console.log('Ellipse associated text found:', useCaseName)
        }
      }
      
      // Fallback: look for text elements near the ellipse
      if (!useCaseName) {
        const allTexts = document.querySelectorAll('text')
        const targetRect = target.getBoundingClientRect()
        
        for (const textElement of allTexts) {
          const textRect = textElement.getBoundingClientRect()
          // Check if text is close to ellipse (within 50px)
          const distance = Math.sqrt(
            Math.pow(targetRect.left - textRect.left, 2) + 
            Math.pow(targetRect.top - textRect.top, 2)
          )
          if (distance < 50) {
            useCaseName = textElement.textContent?.trim()
            console.log('Nearby text found:', useCaseName)
            break
          }
        }
      }
    }
    // Strategy 3: Path or other element click - traverse up to find text
    else if (target.tagName === 'path' || target.tagName === 'g') {
      const textElement = target.querySelector('text') || 
                        target.parentElement?.querySelector('text')
      if (textElement) {
        useCaseName = textElement.textContent?.trim()
        console.log('Path/Group associated text found:', useCaseName)
      }
    }

    // Clean up the use case name
    if (useCaseName) {
      // Remove common prefixes/suffixes and clean
      useCaseName = useCaseName.replace(/^use case\s*/i, '').trim()
      console.log('Cleaned use case name:', useCaseName)
    }

    // Find the use case index with fuzzy matching
    if (useCaseName && useCases.length > 0) {
      console.log('Searching for use case:', useCaseName, 'in:', useCases)
      
      const foundIndex = useCases.findIndex(name => {
        const nameStr = name.toString().toLowerCase()
        const useCaseStr = useCaseName.toLowerCase()
        
        // Exact match
        if (nameStr === useCaseStr) return true
        
        // Contains match
        if (nameStr.includes(useCaseStr) || useCaseStr.includes(nameStr)) return true
        
        // Word boundary match
        const nameWords = nameStr.split(/\s+/)
        const useCaseWords = useCaseStr.split(/\s+/)
        
        // Check if any words match
        return nameWords.some(word => 
          word.length > 3 && useCaseWords.some(uw => uw.includes(word) || word.includes(uw))
        )
      })

      console.log('Found index:', foundIndex)
      
      if (foundIndex !== -1) {
        console.log('Navigating to sequence diagram for use case:', foundIndex)
        navigate(`/project/${projectId}/diagram/sequence?usecase_idx=${foundIndex}`)
      } else {
        console.log('Use case not found:', useCaseName)
      }
    } else {
      console.log('No use case name detected')
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
        <div className="w-full mx-auto">
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200">
            <div className="p-6 overflow-auto">
              {diagramSvg ? (
                <div 
                  ref={svgContainerRef}
                  className={`min-w-max flex justify-center ${diagramType === 'usecase' ? 'cursor-pointer' : ''}`}
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