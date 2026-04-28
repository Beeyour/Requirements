import { useState, useCallback, useEffect } from 'react';
import { useTranslation } from 'react-i18next';

export const useTextToSpeech = () => {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const { i18n } = useTranslation();
  const speak = useCallback((text) => {
    // Check if the browser supports it
    if (!('speechSynthesis' in window)) {
      alert("Your browser does not support Text-to-Speech.");
      return;
    }
    // Cancel anything currently playing so voices don't overlap
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    // Dynamically set the voice language based on your i18n state!
    utterance.lang = i18n.language.startsWith('ar') ? 'ar-SA' : 'en-US';
    // Optional: Adjust speed and pitch here (1 is default)
    utterance.rate = 1; 
    utterance.pitch = 1;
    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);
    window.speechSynthesis.speak(utterance);
  }, [i18n.language]);
  const stop = useCallback(() => {
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
  }, []);
  // Cleanup: if the user leaves the page while it's talking, make it stop
  useEffect(() => {
    return () => {
      window.speechSynthesis.cancel();
    };
  }, []);
  return { speak, stop, isSpeaking };
};