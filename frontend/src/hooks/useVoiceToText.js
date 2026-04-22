import { useState, useCallback, useRef } from 'react';

export const useVoiceToText = (onTranscript) => {
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);

  const toggleListening = useCallback(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert("Browser does not support speech recognition.");
      return;
    }

    // If already listening, stop it and bail out
    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
      return;
    }

    // Create a NEW instance every time we start
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.continuous = false; // Set to true if you want it to keep listening after pauses
    recognition.interimResults = false;

    recognition.onstart = () => {
      setIsListening(true);
      console.log("Mic on");
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      if (onTranscript) onTranscript(transcript);
    };

    recognition.onerror = (event) => {
      console.error("Speech Error:", event.error);
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
      console.log("Mic off");
    };

    recognitionRef.current = recognition;
    recognition.start();
  }, [isListening, onTranscript]);

  return { isListening, toggleListening };
};