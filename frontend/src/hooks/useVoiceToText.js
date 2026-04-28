import { useState, useCallback, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next'; // 1. Import i18n
export const useVoiceToText = (onTranscript) => {
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);
  // 2. Initialize translation hook to track the active language
  const { i18n } = useTranslation(); 
  //  Keep track of the latest callback without triggering re-renders
  const onTranscriptRef = useRef(onTranscript);
  useEffect(() => {
    onTranscriptRef.current = onTranscript;
  }, [onTranscript]);
  const toggleListening = useCallback(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Browser does not support speech recognition.");
      return;
    }
    //  If it is already listening, kill it explicitly
    if (isListening) {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      setIsListening(false);
      return;
    }
    //  Create a fresh instance
    const recognition = new SpeechRecognition();
    //  SET LANGUAGE DYNAMICALLY based on current UI language
    recognition.lang = i18n.language.startsWith('ar') ? 'ar-SA' : 'en-US';
    recognition.continuous = false; 
    recognition.interimResults = false;
    recognition.onstart = () => {
      setIsListening(true);
    };
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      // Use the ref to call the function, bypassing stale closures
      if (onTranscriptRef.current) {
        onTranscriptRef.current(transcript);
      }
      // CRITICAL: Force the browser to release the microphone immediately
      recognition.stop(); 
    };
    recognition.onerror = (event) => {
      console.error("Speech Error:", event.error);
      setIsListening(false);
    };
    recognition.onend = () => {
      // Ensure UI resets when the mic turns off
      setIsListening(false);
    };
    // 4. Save to ref and try starting
    recognitionRef.current = recognition;
    try {
      recognition.start();
    } catch (error) {
      console.error("Failed to start recognition:", error);
      setIsListening(false);
    }
    
  // 5. CRITICAL: Add i18n.language here so the function rebuilds if the user clicks the language toggle!
  }, [isListening, i18n.language]); 
  return { isListening, toggleListening };
};