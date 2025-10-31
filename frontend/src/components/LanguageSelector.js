import React from 'react';
import { useTranslation } from 'react-i18next';

const LanguageSelector = ({ position = 'fixed' }) => {
  const { i18n } = useTranslation();

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
    localStorage.setItem('fidus_language', lng);
  };

  const languages = [
    { code: 'en', flag: '🇬🇧', name: 'English' },
    { code: 'pt', flag: '🇧🇷', name: 'Português' },
    { code: 'fr', flag: '🇫🇷', name: 'Français' }
  ];

  const containerStyle = {
    [position]: position === 'fixed' ? '2rem' : 'auto',
    top: position === 'fixed' ? '2rem' : 'auto',
    right: position === 'fixed' ? '2rem' : 'auto',
    zIndex: 1000,
    display: 'flex',
    gap: '0.5rem',
    background: 'rgba(26, 34, 56, 0.95)',
    padding: '0.75rem',
    borderRadius: '12px',
    backdropFilter: 'blur(10px)',
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)',
    border: '1px solid rgba(255, 255, 255, 0.1)'
  };

  const buttonStyle = (isActive) => ({
    background: isActive 
      ? 'linear-gradient(135deg, #00bcd4 0%, #0097a7 100%)'
      : 'rgba(255, 255, 255, 0.05)',
    border: isActive 
      ? '2px solid #00bcd4' 
      : '2px solid transparent',
    borderRadius: '8px',
    padding: '0.5rem 0.75rem',
    cursor: 'pointer',
    fontSize: '1.5rem',
    transition: 'all 0.3s ease',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    minWidth: '44px',
    minHeight: '44px',
    position: 'relative',
    overflow: 'hidden'
  });

  const buttonHoverStyle = {
    transform: 'translateY(-2px)',
    boxShadow: '0 4px 12px rgba(0, 188, 212, 0.3)'
  };

  return (
    <div style={containerStyle}>
      {languages.map((lang) => (
        <button
          key={lang.code}
          onClick={() => changeLanguage(lang.code)}
          style={buttonStyle(i18n.language === lang.code)}
          onMouseEnter={(e) => {
            if (i18n.language !== lang.code) {
              Object.assign(e.target.style, {
                background: 'rgba(0, 188, 212, 0.2)',
                transform: 'translateY(-2px)'
              });
            }
          }}
          onMouseLeave={(e) => {
            if (i18n.language !== lang.code) {
              Object.assign(e.target.style, {
                background: 'rgba(255, 255, 255, 0.05)',
                transform: 'translateY(0)'
              });
            }
          }}
          title={lang.name}
          aria-label={`Switch to ${lang.name}`}
        >
          {lang.flag}
        </button>
      ))}
    </div>
  );
};

export default LanguageSelector;
