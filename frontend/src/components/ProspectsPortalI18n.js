import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import LanguageSelector from './LanguageSelector';

// Main Prospects Portal Component - With i18n Support
const ProspectsPortalNew = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [formData, setFormData] = useState({ email: '', phone: '' });
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Smooth scroll function
  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  // Form validation
  const validateForm = () => {
    const newErrors = {};
    
    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!formData.email) {
      newErrors.email = t('leadCapture.form.emailRequired');
    } else if (!emailRegex.test(formData.email)) {
      newErrors.email = t('leadCapture.form.emailInvalid');
    }

    // Phone validation - more flexible
    const phoneRegex = /^[+]?[0-9\s\-().]{8,20}$/;
    if (!formData.phone) {
      newErrors.phone = t('leadCapture.form.phoneRequired');
    } else if (!phoneRegex.test(formData.phone)) {
      newErrors.phone = t('leadCapture.form.phoneInvalid');
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setIsSubmitting(true);

    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(`${backendUrl}/api/prospects/lead`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: formData.email,
          phone: formData.phone,
          source: 'prospects_portal'
        })
      });

      const data = await response.json();

      if (data.success || response.ok) {
        const leadId = data.leadId || data.lead_id || data.id;
        if (leadId) {
          localStorage.setItem('fidus_lead_id', leadId);
          navigate(`/prospects/simulator/${leadId}`);
        } else {
          setErrors({ submit: t('leadCapture.form.submitError') });
        }
      } else {
        setErrors({ submit: data.message || t('leadCapture.form.submitError') });
      }
    } catch (error) {
      console.error('Form submission error:', error);
      setErrors({ submit: t('leadCapture.form.connectionError') });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div style={{ 
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
      background: '#0f1419',
      minHeight: '100vh'
    }}>
      {/* Language Selector */}
      <LanguageSelector position="fixed" />

      {/* SECTION 1: Hero Section */}
      <section style={{
        background: 'linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%)',
        minHeight: '70vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '4rem 2rem',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {/* Logo */}
        <div style={{
          position: 'absolute',
          top: '2rem',
          left: '2rem',
          zIndex: 10,
          background: 'rgba(255, 255, 255, 0.95)',
          padding: '1rem 1.5rem',
          borderRadius: '12px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.3)'
        }}>
          <img 
            src="https://customer-assets.emergentagent.com/job_prospects-portal/artifacts/5wp93uqz_FIDUS%20LOGO%20COMPLETE.png" 
            alt="FIDUS Investment Management"
            style={{
              height: 'auto',
              width: '200px',
              display: 'block'
            }}
          />
        </div>

        {/* Decorative elements */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          opacity: 0.1,
          background: 'radial-gradient(circle at 30% 50%, #06b6d4 0%, transparent 50%), radial-gradient(circle at 70% 80%, #3b82f6 0%, transparent 50%)'
        }} />

        {/* Main Content */}
        <div style={{ position: 'relative', zIndex: 5, maxWidth: '900px', width: '100%' }}>
          <h1 style={{
            fontSize: 'clamp(2rem, 5vw, 3.5rem)',
            fontWeight: '700',
            color: '#ffffff',
            textAlign: 'center',
            marginBottom: '1rem',
            letterSpacing: '-0.02em',
            lineHeight: '1.2'
          }}>
            {t('hero.title')}
          </h1>

          <p style={{
            fontSize: 'clamp(1rem, 2vw, 1.25rem)',
            color: 'rgba(255, 255, 255, 0.95)',
            textAlign: 'center',
            maxWidth: '700px',
            margin: '0 auto 2.5rem',
            lineHeight: '1.6'
          }}>
            {t('hero.subtitle')}
          </p>

          <div style={{ textAlign: 'center' }}>
            <button 
              onClick={() => scrollToSection('lead-capture')}
              style={{
                background: '#3b82f6',
                color: '#ffffff',
                padding: '1rem 3rem',
                fontSize: '1.125rem',
                fontWeight: '600',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                boxShadow: '0 4px 20px rgba(59, 130, 246, 0.3)'
              }}
              onMouseEnter={(e) => {
                e.target.style.transform = 'translateY(-2px)';
                e.target.style.boxShadow = '0 6px 25px rgba(59, 130, 246, 0.5)';
              }}
              onMouseLeave={(e) => {
                e.target.style.transform = 'translateY(0)';
                e.target.style.boxShadow = '0 4px 20px rgba(59, 130, 246, 0.3)';
              }}
            >
              {t('hero.cta.start')} →
            </button>
          </div>
        </div>
      </section>

      {/* SECTION 2: Value Propositions */}
      <section style={{
        padding: '5rem 2rem',
        background: '#0f1419'
      }}>
        <h2 style={{
          fontSize: 'clamp(2rem, 4vw, 2.5rem)',
          fontWeight: '600',
          color: '#ffffff',
          textAlign: 'center',
          marginBottom: '3rem'
        }}>
          {t('valueProps.title')}
        </h2>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '2rem',
          maxWidth: '1200px',
          margin: '0 auto'
        }}>
          {[
            { icon: '📈', title: t('valueProps.profitability.title'), desc: t('valueProps.profitability.description') },
            { icon: '💎', title: t('valueProps.transparency.title'), desc: t('valueProps.transparency.description') },
            { icon: '⚡', title: t('valueProps.flexibility.title'), desc: t('valueProps.flexibility.description') }
          ].map((benefit, index) => (
            <div key={index} style={{
              padding: '2rem',
              background: '#1f2937',
              borderRadius: '12px',
              textAlign: 'center',
              transition: 'transform 0.3s ease, box-shadow 0.3s ease',
              cursor: 'pointer',
              border: '1px solid rgba(255, 255, 255, 0.05)'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-5px)';
              e.currentTarget.style.boxShadow = '0 8px 30px rgba(59, 130, 246, 0.2)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
            }}>
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>{benefit.icon}</div>
              <h3 style={{ fontSize: '1.5rem', color: '#ffffff', marginBottom: '1rem' }}>{benefit.title}</h3>
              <p style={{ color: 'rgba(255, 255, 255, 0.7)', lineHeight: '1.6' }}>{benefit.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* SECTION 3: Fund Showcase */}
      <section style={{
        padding: '5rem 2rem',
        background: '#1a1f2e'
      }}>
        <h2 style={{
          fontSize: 'clamp(2rem, 4vw, 2.5rem)',
          fontWeight: '600',
          color: '#ffffff',
          textAlign: 'center',
          marginBottom: '1rem'
        }}>
          {t('funds.title')}
        </h2>
        
        <p style={{
          fontSize: '1.125rem',
          color: 'rgba(255, 255, 255, 0.7)',
          textAlign: 'center',
          maxWidth: '700px',
          margin: '0 auto 3rem'
        }}>
          {t('funds.subtitle')}
        </p>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '2rem',
          maxWidth: '1400px',
          margin: '0 auto'
        }}>
          {[
            {
              name: t('funds.core.name'),
              risk: t('funds.core.risk'),
              returns: t('funds.core.returns'),
              minInvestment: t('funds.core.minimumInvestment'),
              description: t('funds.core.description'),
              color: '#10b981',
              gradient: 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
            },
            {
              name: t('funds.balance.name'),
              risk: t('funds.balance.risk'),
              returns: t('funds.balance.returns'),
              minInvestment: t('funds.balance.minimumInvestment'),
              description: t('funds.balance.description'),
              color: '#3b82f6',
              gradient: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)'
            },
            {
              name: t('funds.dynamic.name'),
              risk: t('funds.dynamic.risk'),
              returns: t('funds.dynamic.returns'),
              minInvestment: t('funds.dynamic.minimumInvestment'),
              description: t('funds.dynamic.description'),
              color: '#f59e0b',
              gradient: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)'
            },
            {
              name: t('funds.unlimited.name'),
              risk: t('funds.unlimited.risk'),
              returns: t('funds.unlimited.returns'),
              minInvestment: t('funds.unlimited.minimumInvestment'),
              description: t('funds.unlimited.description'),
              color: '#ef4444',
              gradient: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)'
            }
          ].map((fund, index) => (
            <div key={index} style={{
              background: '#1f2937',
              borderRadius: '16px',
              padding: '2rem',
              border: `2px solid ${fund.color}20`,
              transition: 'transform 0.3s ease, box-shadow 0.3s ease',
              cursor: 'pointer'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-8px)';
              e.currentTarget.style.boxShadow = `0 12px 40px ${fund.color}40`;
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
            }}>
              <div style={{
                background: fund.gradient,
                borderRadius: '8px',
                padding: '0.75rem 1.5rem',
                marginBottom: '1.5rem',
                textAlign: 'center'
              }}>
                <h3 style={{
                  fontSize: '1.5rem',
                  color: '#ffffff',
                  fontWeight: '700',
                  margin: 0
                }}>
                  {fund.name}
                </h3>
              </div>

              <p style={{
                color: 'rgba(255, 255, 255, 0.85)',
                fontSize: '1rem',
                lineHeight: '1.6',
                marginBottom: '1.5rem'
              }}>
                {fund.description}
              </p>

              <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '0.75rem'
              }}>
                <div style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  padding: '0.75rem',
                  borderRadius: '8px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}>
                  <span style={{ color: 'rgba(255, 255, 255, 0.6)' }}>{fund.risk}</span>
                </div>

                <div style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  padding: '0.75rem',
                  borderRadius: '8px'
                }}>
                  <span style={{ color: fund.color, fontWeight: '600' }}>{fund.returns}</span>
                </div>

                <div style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  padding: '0.75rem',
                  borderRadius: '8px'
                }}>
                  <span style={{ color: 'rgba(255, 255, 255, 0.9)', fontWeight: '600' }}>{fund.minInvestment}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* SECTION 4: Lead Capture Form */}
      <section id="lead-capture" style={{
        padding: '5rem 2rem',
        background: '#0f1419'
      }}>
        <div style={{ maxWidth: '600px', margin: '0 auto' }}>
          <h2 style={{
            fontSize: 'clamp(2rem, 4vw, 2.5rem)',
            fontWeight: '600',
            color: '#ffffff',
            textAlign: 'center',
            marginBottom: '1rem'
          }}>
            {t('leadCapture.title')}
          </h2>
          
          <p style={{
            fontSize: '1.125rem',
            color: 'rgba(255, 255, 255, 0.7)',
            textAlign: 'center',
            marginBottom: '2.5rem'
          }}>
            {t('leadCapture.subtitle')}
          </p>

          <form onSubmit={handleSubmit} style={{
            background: '#1f2937',
            padding: '2.5rem',
            borderRadius: '16px',
            border: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <div style={{ marginBottom: '1.5rem' }}>
              <input
                type="email"
                placeholder={t('leadCapture.form.emailPlaceholder')}
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                style={{
                  width: '100%',
                  padding: '1rem',
                  fontSize: '1rem',
                  border: errors.email ? '2px solid #ef4444' : '2px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '8px',
                  background: '#0f1419',
                  color: '#ffffff',
                  outline: 'none',
                  transition: 'border-color 0.3s ease'
                }}
                onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
                onBlur={(e) => e.target.style.borderColor = errors.email ? '#ef4444' : 'rgba(255, 255, 255, 0.1)'}
              />
              {errors.email && (
                <p style={{ color: '#ef4444', fontSize: '0.875rem', marginTop: '0.5rem' }}>
                  {errors.email}
                </p>
              )}
            </div>

            <div style={{ marginBottom: '1.5rem' }}>
              <input
                type="tel"
                placeholder={t('leadCapture.form.phonePlaceholder')}
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                style={{
                  width: '100%',
                  padding: '1rem',
                  fontSize: '1rem',
                  border: errors.phone ? '2px solid #ef4444' : '2px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '8px',
                  background: '#0f1419',
                  color: '#ffffff',
                  outline: 'none',
                  transition: 'border-color 0.3s ease'
                }}
                onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
                onBlur={(e) => e.target.style.borderColor = errors.phone ? '#ef4444' : 'rgba(255, 255, 255, 0.1)'}
              />
              {errors.phone && (
                <p style={{ color: '#ef4444', fontSize: '0.875rem', marginTop: '0.5rem' }}>
                  {errors.phone}
                </p>
              )}
            </div>

            {errors.submit && (
              <div style={{
                background: 'rgba(239, 68, 68, 0.1)',
                border: '1px solid #ef4444',
                borderRadius: '8px',
                padding: '1rem',
                marginBottom: '1.5rem',
                color: '#ef4444',
                textAlign: 'center'
              }}>
                {errors.submit}
              </div>
            )}

            <button
              type="submit"
              disabled={isSubmitting}
              style={{
                width: '100%',
                padding: '1rem',
                fontSize: '1.125rem',
                fontWeight: '600',
                color: '#ffffff',
                background: isSubmitting ? 'rgba(59, 130, 246, 0.5)' : '#3b82f6',
                border: 'none',
                borderRadius: '8px',
                cursor: isSubmitting ? 'not-allowed' : 'pointer',
                transition: 'all 0.3s ease'
              }}
              onMouseEnter={(e) => {
                if (!isSubmitting) {
                  e.target.style.background = '#2563eb';
                  e.target.style.transform = 'translateY(-2px)';
                  e.target.style.boxShadow = '0 8px 25px rgba(59, 130, 246, 0.4)';
                }
              }}
              onMouseLeave={(e) => {
                if (!isSubmitting) {
                  e.target.style.background = '#3b82f6';
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = 'none';
                }
              }}
            >
              {isSubmitting ? t('leadCapture.form.submitting') : t('leadCapture.form.submit')}
            </button>
          </form>
        </div>
      </section>

      {/* SECTION 5: Footer */}
      <footer style={{
        background: '#1a1f2e',
        padding: '3rem 2rem',
        textAlign: 'center',
        borderTop: '1px solid rgba(255, 255, 255, 0.05)'
      }}>
        <div style={{ maxWidth: '900px', margin: '0 auto' }}>
          <p style={{
            color: 'rgba(255, 255, 255, 0.5)',
            fontSize: '0.875rem',
            lineHeight: '1.6'
          }}>
            {t('footer.disclaimer')}
          </p>
        </div>
      </footer>
    </div>
  );
};

export default ProspectsPortalNew;
