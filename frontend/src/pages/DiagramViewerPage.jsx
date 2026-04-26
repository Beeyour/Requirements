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
    const target = event.target

    // 1. Handle Sequence Diagram "Back" button click
    if (diagramType === 'sequence') {
      const linkTag = target.closest('a');
      const textContent = target.textContent?.toLowerCase() || '';
      
      // Check if clicked element is part of a back link
      if (
        (linkTag && (linkTag.getAttribute('href')?.includes('usecase') || linkTag.textContent?.toLowerCase().includes('back'))) ||
        textContent.includes('back to use case')
      ) {
        event.preventDefault()
        event.stopPropagation()
        navigate(`/project/${projectId}/diagram/usecase`)
      }
      return; // Sequence diagrams don't need the usecase logic below
    }

    // 2. Only handle clicks for use case diagrams
    if (diagramType !== 'usecase') return

    console.log('SVG clicked:', target.tagName, target.textContent?.trim())
    
    // Prevent default browser navigation
    event.preventDefault()
    event.stopPropagation()
    
    // Check if this is an <a> tag click from PlantUML
    if (target.tagName === 'a') {
      const href = target.getAttribute('href')
      console.log('Intercepted PlantUML link:', href)
      
      // Check for "Back to Use Case Diagram" button
      if (href && href.includes('usecase')) {
        console.log('Intercepted Back to Use Case Diagram button')
        navigate(`/project/${projectId}/diagram/usecase`)
        return
      }
      
      // Extract usecase_idx from href pattern /generate-sequence/{project_id}/{usecase_idx}
      const match = href.match(/\/generate-sequence\/\d+\/(\d+)/)
      if (match) {
        const usecaseIdx = parseInt(match[1])
        console.log('Extracted usecase_idx:', usecaseIdx)
        navigate(`/project/${projectId}/diagram/sequence?usecase_idx=${usecaseIdx}`)
        return
      }
    }
    
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

  const handleBack = () => {
    if (diagramType === 'sequence') {
      navigate(`/project/${projectId}/diagram/usecase`)
    } else {
      navigate(`/project/${projectId}/interview`)
    }
  }

  return (
    <div className="h-screen bg-slate-100 flex flex-col overflow-hidden">
      {/* --- HEADER --- */}
      <div className="flex-none z-50 bg-slate-100">
        {/* Same Navbar as Interview/Dashboard */}
        <Navbar projectName={project?.app_name} />
      </div>

      {/* --- MAIN PADDED LAYOUT --- */}
      <div className="flex-1 flex flex-col overflow-hidden p-6 gap-4">
        
        {/* Unified Tile for Title and Diagram */}
        <div className="bg-white rounded-3xl shadow-sm border border-slate-200 flex flex-col overflow-hidden h-full max-w-7xl mx-auto w-full relative">
          
          {/* Header section with bottom border */}
          <div className="px-6 py-5 border-b border-slate-200 flex items-center justify-between bg-white z-10 flex-shrink-0">
            <div className="flex items-center gap-3">
              {/* Back Button */}
              <button 
                onClick={handleBack}
                className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
                title="Go Back"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
              </button>
              
              <div>
                <h1 className="text-lg font-semibold text-slate-800 leading-tight">{getDiagramTitle()}</h1>
                {diagramType === 'usecase' && useCases.length > 0 && (
                  <p className="text-xs text-slate-500 mt-0.5">
                    Click on any use case to view its sequence diagram
                  </p>
                )}
              </div>
            </div>

            {/* Interactive Badge */}
            {diagramType === 'usecase' && (
              <span className="px-2.5 py-1 bg-blue-50 text-blue-600 text-xs font-medium rounded-md border border-blue-100">
                Interactive
              </span>
            )}
          </div>

          {/* Diagram Area */}
          <div className="flex-1 overflow-auto p-6 bg-slate-50/30 flex items-center justify-center">
            {loading ? (
              <div className="text-center">
                <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                <p className="text-slate-500 text-sm font-medium">Loading diagram...</p>
              </div>
            ) : error ? (
              <div className="text-center max-w-md mx-auto">
                <div className="w-14 h-14 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-4 border border-red-100">
                  <svg className="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h3 className="text-base font-semibold text-slate-800 mb-1">Error Loading Diagram</h3>
                <p className="text-sm text-slate-500 mb-4">{error}</p>
                <button
                  onClick={handleBack}
                  className="px-4 py-2 bg-white border border-slate-200 text-slate-700 text-sm font-medium rounded-lg hover:bg-slate-50 transition-colors shadow-sm"
                >
                  Go Back
                </button>
              </div>
            ) : diagramSvg ? (
              <div 
                ref={svgContainerRef}
                className={`min-w-max bg-white rounded-xl shadow-sm border border-slate-100 p-8 ${diagramType === 'usecase' ? 'cursor-pointer hover:border-blue-200 transition-colors' : ''}`}
                onClick={handleSvgClick}
                dangerouslySetInnerHTML={{ __html: diagramSvg }}
              />
            ) : (
              <div className="text-center">
                <div className="w-14 h-14 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-6 h-6 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <h3 className="text-base font-medium text-slate-800 mb-1">No Diagram Available</h3>
                <p className="text-sm text-slate-500">
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
  )
}