import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import LanguageSelector from './LanguageSelector';
import ReferralCodeInput from './referrals/ReferralCodeInput';

const ProspectsPortalNew = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [searchParams] = useSearchParams();
  const [formData, setFormData] = useState({ email: '', phone: '', referral_code: '' });
  const [salesperson, setSalesperson] = useState(null);
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Check for referral code in URL
  useEffect(() => {
    const refCode = searchParams.get('ref');
    if (refCode) {
      setFormData(prev => ({ ...prev, referral_code: refCode }));
    }
  }, [searchParams]);

  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  const validateForm = () => {
    const newErrors = {};
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!formData.email) {
      newErrors.email = t('prospects.contact.emailRequired');
    } else if (!emailRegex.test(formData.email)) {
      newErrors.email = t('prospects.contact.emailInvalid');
    }
    const phoneRegex = /^[+]?[0-9\s\-().]{8,20}$/;
    if (!formData.phone) {
      newErrors.phone = t('prospects.contact.phoneRequired');
    } else if (!phoneRegex.test(formData.phone)) {
      newErrors.phone = t('prospects.contact.phoneInvalid');
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleReferralChange = (code, salespersonData) => {
    setFormData(prev => ({ ...prev, referral_code: code }));
    setSalesperson(salespersonData);
  };

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
          source: 'prospects_portal',
          referral_code: formData.referral_code || null,
          referred_by: salesperson?.id || null,
          referred_by_name: salesperson?.name || null
        })
      });
      const data = await response.json();
      if (data.success || response.ok) {
        const leadId = data.leadId || data.lead_id || data.id;
        if (leadId) {
          localStorage.setItem('fidus_lead_id', leadId);
          navigate(`/prospects/simulator/${leadId}`);
        } else {
          setErrors({ submit: t('prospects.contact.submitError') });
        }
      } else {
        setErrors({ submit: data.message || t('prospects.contact.submitError') });
      }
    } catch (error) {
      console.error('Form submission error:', error);
      setErrors({ submit: t('prospects.contact.submitError') });
    } finally {
      setIsSubmitting(false);
    }
  };

  const products = [
    {
      name: t('prospects.products.core.name'),
      logo: 'https://customer-assets.emergentagent.com/job_prospects-portal/artifacts/uibusrfk_FIDUS%20CORE.png',
      tagline: t('prospects.products.core.tagline'),
      rate: t('prospects.products.core.rate'),
      annualRate: t('prospects.products.core.annualRate'),
      minInvestment: t('prospects.products.core.minInvestment'),
      redemption: t('prospects.products.core.redemption'),
      color: '#ffffff',
      textColor: '#1e293b',
      buttonColor: '#1e3a8a',
      features: t('prospects.products.core.features', { returnObjects: true })
    },
    {
      name: t('prospects.products.balance.name'),
      logo: 'https://customer-assets.emergentagent.com/job_prospects-portal/artifacts/yav4r65z_FIDUS%20BALANCE.png',
      tagline: t('prospects.products.balance.tagline'),
      rate: t('prospects.products.balance.rate'),
      annualRate: t('prospects.products.balance.annualRate'),
      minInvestment: t('prospects.products.balance.minInvestment'),
      redemption: t('prospects.products.balance.redemption'),
      color: '#0891b2',
      textColor: '#ffffff',
      buttonColor: '#0891b2',
      popular: true,
      popularText: t('prospects.products.balance.popular'),
      features: t('prospects.products.balance.features', { returnObjects: true })
    },
    {
      name: t('prospects.products.dynamic.name'),
      logo: 'https://customer-assets.emergentagent.com/job_prospects-portal/artifacts/u4yztdby_FIDUS%20DYNAMIC.png',
      tagline: t('prospects.products.dynamic.tagline'),
      rate: t('prospects.products.dynamic.rate'),
      annualRate: t('prospects.products.dynamic.annualRate'),
      minInvestment: t('prospects.products.dynamic.minInvestment'),
      redemption: t('prospects.products.dynamic.redemption'),
      color: '#1e3a8a',
      textColor: '#ffffff',
      buttonColor: '#1e3a8a',
      features: t('prospects.products.dynamic.features', { returnObjects: true })
    },
    {
      name: t('prospects.products.unlimited.name'),
      logo: 'https://customer-assets.emergentagent.com/job_prospects-portal/artifacts/5wp93uqz_FIDUS%20LOGO%20COMPLETE.png',
      tagline: t('prospects.products.unlimited.tagline'),
      rate: t('prospects.products.unlimited.rate'),
      annualRate: t('prospects.products.unlimited.annualRate'),
      minInvestment: t('prospects.products.unlimited.minInvestment'),
      redemption: t('prospects.products.unlimited.redemption'),
      color: '#7c3aed',
      textColor: '#ffffff',
      buttonColor: '#7c3aed',
      features: t('prospects.products.unlimited.features', { returnObjects: true })
    }
  ];

  const benefits = [
    { 
      icon: '🎯', 
      title: t('prospects.benefits.experience.title'), 
      desc: t('prospects.benefits.experience.description') 
    },
    { 
      icon: '💎', 
      title: t('prospects.benefits.transparency.title'), 
      desc: t('prospects.benefits.transparency.description') 
    },
    { 
      icon: '📈', 
      title: t('prospects.benefits.returns.title'), 
      desc: t('prospects.benefits.returns.description') 
    },
    { 
      icon: '🔒', 
      title: t('prospects.benefits.security.title'), 
      desc: t('prospects.benefits.security.description') 
    },
    { 
      icon: '💰', 
      title: t('prospects.benefits.accessible.title'), 
      desc: t('prospects.benefits.accessible.description') 
    },
    { 
      icon: '⚡', 
      title: t('prospects.benefits.simple.title'), 
      desc: t('prospects.benefits.simple.description') 
    }
  ];

  return (
    <div style={{ 
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
      background: '#0f1419',
      minHeight: '100vh'
    }}>
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
            style={{ height: 'auto', width: '200px', display: 'block' }}
          />
        </div>

        <div style={{ position: 'absolute', top: '2rem', right: '2rem', zIndex: 10 }}>
          <LanguageSelector position="relative" />
        </div>

        <div style={{
          position: 'absolute',
          top: 0, left: 0, right: 0, bottom: 0,
          opacity: 0.1,
          background: 'radial-gradient(circle at 30% 50%, #06b6d4 0%, transparent 50%), radial-gradient(circle at 70% 80%, #3b82f6 0%, transparent 50%)'
        }} />

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
            {t('prospects.hero.title').toUpperCase()}
          </h1>

          <p style={{
            fontSize: 'clamp(1rem, 2vw, 1.25rem)',
            color: 'rgba(255, 255, 255, 0.95)',
            textAlign: 'center',
            maxWidth: '700px',
            margin: '0 auto 2.5rem',
            lineHeight: '1.6'
          }}>
            {t('prospects.hero.subtitle')}
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
              {t('prospects.hero.cta')} →
            </button>
          </div>
        </div>
      </section>

      <section style={{ padding: '5rem 2rem', background: '#0f1419' }}>
        <h2 style={{
          fontSize: 'clamp(2rem, 4vw, 2.5rem)',
          fontWeight: '600',
          color: '#ffffff',
          textAlign: 'center',
          marginBottom: '3rem'
        }}>
          {t('prospects.benefits.title')}
        </h2>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '2rem',
          maxWidth: '1200px',
          margin: '0 auto'
        }}>
          {benefits.map((benefit, index) => (
            <div key={index} style={{
              padding: '2rem',
              background: '#1f2937',
              borderRadius: '12px',
              textAlign: 'center',
              transition: 'transform 0.3s ease, box-shadow 0.3s ease',
              cursor: 'pointer',
              border: '1px solid rgba(59, 130, 246, 0.1)'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-5px)';
              e.currentTarget.style.boxShadow = '0 8px 25px rgba(59, 130, 246, 0.2)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
            }}
            >
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>{benefit.icon}</div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#ffffff', marginBottom: '0.75rem' }}>
                {benefit.title}
              </h3>
              <p style={{ fontSize: '0.95rem', color: '#9ca3af', lineHeight: '1.6' }}>
                {benefit.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      <section style={{ padding: '5rem 2rem', background: '#1a1f2e' }}>
        <h2 style={{
          fontSize: 'clamp(2rem, 4vw, 2.5rem)',
          fontWeight: '600',
          color: '#ffffff',
          textAlign: 'center',
          marginBottom: '1rem'
        }}>
          {t('prospects.products.title')}
        </h2>
        <p style={{
          fontSize: '1.125rem',
          color: '#9ca3af',
          textAlign: 'center',
          marginBottom: '3rem',
          maxWidth: '700px',
          margin: '0 auto 3rem'
        }}>
          {t('prospects.products.subtitle')}
        </p>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '2rem',
          maxWidth: '1400px',
          margin: '0 auto'
        }}>
          {products.map((fund, index) => (
            <div key={index} style={{
              background: '#1f2937',
              borderRadius: '16px',
              overflow: 'hidden',
              boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)',
              position: 'relative',
              border: fund.popular ? `2px solid ${fund.color}` : '1px solid rgba(255,255,255,0.1)',
              transform: fund.popular ? 'scale(1.02)' : 'scale(1)',
              transition: 'all 0.3s ease'
            }}>
              {fund.popular && (
                <div style={{
                  position: 'absolute',
                  top: '1rem',
                  right: '1rem',
                  background: fund.color,
                  color: 'white',
                  padding: '0.375rem 0.875rem',
                  borderRadius: '20px',
                  fontSize: '0.75rem',
                  fontWeight: '600',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px',
                  zIndex: 1
                }}>
                  {fund.popularText}
                </div>
              )}

              <div style={{ background: fund.color, padding: '2rem', color: fund.textColor || 'white' }}>
                <div style={{ marginBottom: '1rem', display: 'flex', justifyContent: 'center' }}>
                  <img 
                    src={fund.logo}
                    alt={fund.name}
                    style={{ height: '80px', width: 'auto', objectFit: 'contain' }}
                  />
                </div>
                
                <h3 style={{ fontSize: '1.75rem', fontWeight: '700', marginBottom: '0.5rem' }}>
                  {fund.name}
                </h3>
                <p style={{ fontSize: '1rem', opacity: 0.9, marginBottom: '1.5rem' }}>
                  {fund.tagline}
                </p>

                <div style={{ marginBottom: '1rem' }}>
                  <div style={{ fontSize: '3rem', fontWeight: '700', lineHeight: '1' }}>
                    {fund.rate}
                  </div>
                  <div style={{ fontSize: '1rem', opacity: 0.9 }}>
                    {t('prospects.products.monthlyReturn')} ({fund.annualRate} {t('prospects.products.annualReturn')})
                  </div>
                </div>

                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  paddingTop: '1rem',
                  borderTop: '1px solid rgba(255, 255, 255, 0.2)',
                  fontSize: '0.9rem'
                }}>
                  <div>
                    <div style={{ opacity: 0.8 }}>{t('prospects.products.minInvest')}</div>
                    <div style={{ fontWeight: '600' }}>{fund.minInvestment}</div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ opacity: 0.8 }}>{t('prospects.products.redemptionPeriod')}</div>
                    <div style={{ fontWeight: '600' }}>{fund.redemption}</div>
                  </div>
                </div>
              </div>

              <div style={{ padding: '2rem', background: '#1f2937' }}>
                <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 2rem 0' }}>
                  {fund.features.map((feature, idx) => (
                    <li key={idx} style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.75rem',
                      marginBottom: '0.75rem',
                      color: '#9ca3af',
                      fontSize: '0.95rem'
                    }}>
                      <span style={{ color: fund.color, fontSize: '1.25rem', fontWeight: 'bold' }}>✓</span>
                      {feature}
                    </li>
                  ))}
                </ul>

                <button
                  onClick={() => scrollToSection('lead-capture')}
                  style={{
                    width: '100%',
                    padding: '1rem',
                    fontSize: '1rem',
                    fontWeight: '600',
                    color: 'white',
                    background: fund.buttonColor || fund.color,
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease'
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.transform = 'translateY(-2px)';
                    e.target.style.boxShadow = '0 6px 20px rgba(0, 0, 0, 0.3)';
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.transform = 'translateY(0)';
                    e.target.style.boxShadow = 'none';
                  }}
                >
                  {t('prospects.hero.cta')}
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section id="lead-capture" style={{ padding: '5rem 2rem', background: '#0f1419' }}>
        <div style={{ maxWidth: '550px', margin: '0 auto' }}>
          <h2 style={{
            fontSize: 'clamp(1.75rem, 3vw, 2rem)',
            fontWeight: '600',
            color: '#ffffff',
            textAlign: 'center',
            marginBottom: '0.5rem'
          }}>
            {t('prospects.contact.title')}
          </h2>
          <p style={{ fontSize: '1rem', color: '#9ca3af', textAlign: 'center', marginBottom: '2rem' }}>
            {t('prospects.contact.subtitle')}
          </p>

          <form onSubmit={handleSubmit} style={{
            background: '#1f2937',
            padding: '2.5rem',
            borderRadius: '12px',
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)',
            border: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{
                display: 'block',
                fontSize: '0.95rem',
                fontWeight: '500',
                color: '#ffffff',
                marginBottom: '0.5rem'
              }}>
                📧 {t('prospects.contact.email')}
              </label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder={t('prospects.contact.emailPlaceholder')}
                style={{
                  width: '100%',
                  padding: '0.875rem',
                  fontSize: '1rem',
                  border: errors.email ? '2px solid #ef4444' : '2px solid rgba(59, 130, 246, 0.3)',
                  borderRadius: '8px',
                  outline: 'none',
                  transition: 'border-color 0.3s ease',
                  boxSizing: 'border-box',
                  background: '#0f1419',
                  color: '#ffffff'
                }}
                onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
                onBlur={(e) => e.target.style.borderColor = errors.email ? '#ef4444' : 'rgba(59, 130, 246, 0.3)'}
              />
              {errors.email && (
                <span style={{ color: '#ef4444', fontSize: '0.875rem', marginTop: '0.25rem', display: 'block' }}>
                  {errors.email}
                </span>
              )}
            </div>

            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{
                display: 'block',
                fontSize: '0.95rem',
                fontWeight: '500',
                color: '#ffffff',
                marginBottom: '0.5rem'
              }}>
                📱 {t('prospects.contact.phone')} (WhatsApp)
              </label>
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                placeholder={t('prospects.contact.phonePlaceholder')}
                style={{
                  width: '100%',
                  padding: '0.875rem',
                  fontSize: '1rem',
                  border: errors.phone ? '2px solid #ef4444' : '2px solid rgba(59, 130, 246, 0.3)',
                  borderRadius: '8px',
                  outline: 'none',
                  transition: 'border-color 0.3s ease',
                  boxSizing: 'border-box',
                  background: '#0f1419',
                  color: '#ffffff'
                }}
                onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
                onBlur={(e) => e.target.style.borderColor = errors.phone ? '#ef4444' : 'rgba(59, 130, 246, 0.3)'}
              />
              {errors.phone && (
                <span style={{ color: '#ef4444', fontSize: '0.875rem', marginTop: '0.25rem', display: 'block' }}>
                  {errors.phone}
                </span>
              )}
            </div>

            {errors.submit && (
              <div style={{
                padding: '1rem',
                background: 'rgba(239, 68, 68, 0.1)',
                border: '1px solid #ef4444',
                borderRadius: '8px',
                marginBottom: '1.5rem',
                color: '#ef4444',
                fontSize: '0.9rem'
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
                color: 'white',
                background: isSubmitting ? '#6b7280' : '#3b82f6',
                border: 'none',
                borderRadius: '8px',
                cursor: isSubmitting ? 'not-allowed' : 'pointer',
                transition: 'all 0.3s ease',
                marginBottom: '1rem'
              }}
            >
              {isSubmitting ? t('prospects.contact.submitting') : t('prospects.contact.submit')}
            </button>

            <p style={{
              fontSize: '0.75rem',
              color: '#9ca3af',
              textAlign: 'center',
              lineHeight: '1.4'
            }}>
              {t('prospects.contact.privacyNotice')}
            </p>
          </form>
        </div>
      </section>

      <footer style={{
        padding: '3rem 2rem 2rem',
        background: '#1a1f2e',
        color: 'white',
        textAlign: 'center',
        borderTop: '1px solid rgba(255, 255, 255, 0.1)'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <img 
            src="https://customer-assets.emergentagent.com/job_prospects-portal/artifacts/5wp93uqz_FIDUS%20LOGO%20COMPLETE.png" 
            alt="FIDUS Investment Management"
            style={{
              height: '50px',
              width: 'auto',
              marginBottom: '1.5rem',
              filter: 'brightness(0) invert(1)'
            }}
          />

          <p style={{ fontSize: '1.125rem', marginBottom: '2rem', color: '#9ca3af' }}>
            {t('prospects.footer.tagline')}
          </p>

          <div style={{
            display: 'flex',
            justifyContent: 'center',
            gap: '2rem',
            marginBottom: '2rem',
            flexWrap: 'wrap',
            fontSize: '0.95rem',
            color: '#9ca3af'
          }}>
            <div>📧 hq@getfidus.com</div>
            <div>📱 WhatsApp: +1917-456-2151</div>
          </div>

          <div style={{
            paddingTop: '2rem',
            borderTop: '1px solid rgba(255, 255, 255, 0.1)',
            fontSize: '0.875rem',
            color: '#6b7280'
          }}>
            {t('prospects.footer.copyright')}
          </div>
        </div>
      </footer>
    </div>
  );
};

export default ProspectsPortalNew;
