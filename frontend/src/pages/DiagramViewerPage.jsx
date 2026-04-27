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
          try {
            const svgResponse = await fetch(data.svg_url)
            const svgContent = await svgResponse.text()
            setDiagramSvg(svgContent)
          } catch (svgError) {
            console.error('Failed to fetch SVG content:', svgError)
            setError('Failed to load diagram content')
          }
        }
        
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

    if (diagramType === 'sequence') {
      const linkTag = target.closest('a');
      const textContent = target.textContent?.toLowerCase() || '';
      
      if (
        (linkTag && (linkTag.getAttribute('href')?.includes('usecase') || linkTag.textContent?.toLowerCase().includes('back'))) ||
        textContent.includes('back to use case')
      ) {
        event.preventDefault()
        event.stopPropagation()
        navigate(`/project/${projectId}/diagram/usecase`)
      }
      return;
    }

    if (diagramType !== 'usecase') return

    event.preventDefault()
    event.stopPropagation()
    
    if (target.tagName === 'a') {
      const href = target.getAttribute('href')
      
      if (href && href.includes('usecase')) {
        navigate(`/project/${projectId}/diagram/usecase`)
        return
      }
      
      const match = href.match(/\/generate-sequence\/\d+\/(\d+)/)
      if (match) {
        const usecaseIdx = parseInt(match[1])
        navigate(`/project/${projectId}/diagram/sequence?usecase_idx=${usecaseIdx}`)
        return
      }
    }
    
    let useCaseName = ''

    if (target.tagName === 'text') {
      useCaseName = target.textContent?.trim()
    }
    else if (target.tagName === 'ellipse') {
      const parent = target.parentElement
      if (parent) {
        const textElement = parent.querySelector('text')
        if (textElement) {
          useCaseName = textElement.textContent?.trim()
        }
      }
      
      if (!useCaseName) {
        const allTexts = document.querySelectorAll('text')
        const targetRect = target.getBoundingClientRect()
        
        for (const textElement of allTexts) {
          const textRect = textElement.getBoundingClientRect()
          const distance = Math.sqrt(
            Math.pow(targetRect.left - textRect.left, 2) + 
            Math.pow(targetRect.top - textRect.top, 2)
          )
          if (distance < 50) {
            useCaseName = textElement.textContent?.trim()
            break
          }
        }
      }
    }
    else if (target.tagName === 'path' || target.tagName === 'g') {
      const textElement = target.querySelector('text') || 
                        target.parentElement?.querySelector('text')
      if (textElement) {
        useCaseName = textElement.textContent?.trim()
      }
    }

    if (useCaseName) {
      useCaseName = useCaseName.replace(/^use case\s*/i, '').trim()
    }

    if (useCaseName && useCases.length > 0) {
      const foundIndex = useCases.findIndex(name => {
        const nameStr = name.toString().toLowerCase()
        const useCaseStr = useCaseName.toLowerCase()
        
        if (nameStr === useCaseStr) return true
        if (nameStr.includes(useCaseStr) || useCaseStr.includes(nameStr)) return true
        
        const nameWords = nameStr.split(/\s+/)
        const useCaseWords = useCaseStr.split(/\s+/)
        
        return nameWords.some(word => 
          word.length > 3 && useCaseWords.some(uw => uw.includes(word) || word.includes(uw))
        )
      })
      
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
        <Navbar projectName={project?.app_name} />
      </div>

      {/* --- MAIN PADDED LAYOUT --- */}
      {/* تم تقليل الحواف (Padding) لتعظيم المساحة المستخدمة */}
      <div className="flex-1 flex flex-col overflow-hidden p-2 md:p-4 gap-4">
        
        {/* تم إزالة max-w-7xl لجعل الحاوية تأخذ عرض الشاشة بالكامل */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 flex flex-col overflow-hidden h-full w-full relative">
          
          {/* Header section */}
          <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-white z-10 flex-shrink-0">
            <div className="flex items-center gap-3">
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

            {diagramType === 'usecase' && (
              <span className="px-2.5 py-1 bg-blue-50 text-blue-600 text-xs font-medium rounded-md border border-blue-100">
                Interactive
              </span>
            )}
          </div>

          {/* Diagram Area */}
          {/* تم إزالة items-center justify-center التي كانت تسبب قص الرسمة */}
          <div className="flex-1 overflow-auto bg-slate-50/30 p-4 w-full h-full">
            {loading ? (
              <div className="flex flex-col items-center justify-center h-full">
                <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mb-4"></div>
                <p className="text-slate-500 text-sm font-medium">Loading diagram...</p>
              </div>
            ) : error ? (
              <div className="flex flex-col items-center justify-center h-full max-w-md mx-auto text-center">
                <div className="w-14 h-14 bg-red-50 rounded-full flex items-center justify-center mb-4 border border-red-100">
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
              /* تم إضافة w-max و min-w-full لضمان تمدد الرسمة بشكل صحيح مع توفير Scrollbar */
              <div 
                ref={svgContainerRef}
                className={`w-max min-w-full bg-white rounded-xl shadow-sm border border-slate-100 p-4 [&>svg]:max-w-none [&>svg]:w-auto [&>svg]:h-auto ${diagramType === 'usecase' ? 'cursor-pointer hover:border-blue-200 transition-colors' : ''}`}
                onClick={handleSvgClick}
                dangerouslySetInnerHTML={{ __html: diagramSvg }}
              />
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <div className="w-14 h-14 bg-slate-100 rounded-full flex items-center justify-center mb-4">
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