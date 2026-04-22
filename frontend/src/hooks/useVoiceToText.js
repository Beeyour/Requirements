import { useState, useEffect, useCallback } from 'react';

export const useVoiceToText = (onTranscript) => {
  const [isListening, setIsListening] = useState(false);
  const [browserSupportsSpeech, setBrowserSupportsSpeech] = useState(true);

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  useEffect(() => {
    if (!SpeechRecognition) {
      setBrowserSupportsSpeech(false);
    }
  }, [SpeechRecognition]);

  const toggleListening = useCallback(() => {
    if (!SpeechRecognition) return;

    const recognition = new SpeechRecognition();
    recognition.continuous = false; // Stops after you finish a sentence
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);
    
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      if (onTranscript) onTranscript(transcript);
    };

    if (isListening) {
      recognition.stop();
    } else {
      recognition.start();
    }
  }, [isListening, SpeechRecognition, onTranscript]);

  return { isListening, toggleListening, browserSupportsSpeech };
};