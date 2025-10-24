import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

// Main Prospects Portal Component - Matching Client Portal Dark Theme
const ProspectsPortalNew = () => {
  const navigate = useNavigate();
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
      newErrors.email = 'El correo es requerido';
    } else if (!emailRegex.test(formData.email)) {
      newErrors.email = 'Correo inválido';
    }

    // Phone validation - more flexible
    const phoneRegex = /^[+]?[0-9\s\-().]{8,20}$/;
    if (!formData.phone) {
      newErrors.phone = 'El teléfono es requerido';
    } else if (!phoneRegex.test(formData.phone)) {
      newErrors.phone = 'Teléfono inválido (mínimo 8 dígitos)';
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
          setErrors({ submit: 'Error al crear registro. Intenta de nuevo.' });
        }
      } else {
        setErrors({ submit: data.message || 'Error al crear registro. Intenta de nuevo.' });
      }
    } catch (error) {
      console.error('Form submission error:', error);
      setErrors({ submit: 'Error de conexión. Verifica tu internet.' });
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
          zIndex: 10
        }}>
          <img 
            src="/assets/logos/fidus-logo-complete.png" 
            alt="FIDUS Investment Management"
            style={{
              height: '120px',
              width: 'auto'
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
            DEMOCRATIZAMOS EL MUNDO<br />
            FINANCIERO PARA TODOS
          </h1>

          <p style={{
            fontSize: 'clamp(1rem, 2vw, 1.25rem)',
            color: 'rgba(255, 255, 255, 0.95)',
            textAlign: 'center',
            maxWidth: '700px',
            margin: '0 auto 2.5rem',
            lineHeight: '1.6'
          }}>
            Invierte con transparencia total y rendimientos profesionales.<br />
            30 años de experiencia en trading algorítmico a tu alcance.
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
              Simula Tu Inversión →
            </button>
          </div>

          {/* Trust Indicators */}
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            gap: '2rem',
            marginTop: '3rem',
            flexWrap: 'wrap'
          }}>
            {['Sin compromiso', 'Gratis', 'En 2 minutos'].map((text, i) => (
              <div key={i} style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                color: 'rgba(255, 255, 255, 0.9)',
                fontSize: '0.95rem'
              }}>
                <span style={{ fontSize: '1.25rem' }}>✓</span>
                <span>{text}</span>
              </div>
            ))}
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
          Por Qué Elegir FIDUS
        </h2>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '2rem',
          maxWidth: '1200px',
          margin: '0 auto'
        }}>
          {[
            { icon: '🎯', title: '30 Años de Experiencia', desc: 'Trading algorítmico profesional con historial comprobado en mercados globales.' },
            { icon: '💎', title: 'Transparencia Total', desc: 'Acceso completo a tu cuenta, portal de cliente. Ve tus inversiones en tiempo real, 24/7.' },
            { icon: '📈', title: 'Rendimientos Profesionales', desc: 'Desde 1.5% hasta 4% mensual según tu perfil de inversión y capital.' },
            { icon: '🔒', title: 'Seguridad Garantizada', desc: 'Brokers regulados internacionalmente. Tu capital siempre protegido.' },
            { icon: '💰', title: 'Desde $10,000 USD', desc: 'Acceso a inversiones institucionales con montos accesibles.' },
            { icon: '⚡', title: 'Proceso Simple', desc: 'Apertura de cuenta 100% digital. Invierte en menos de 48 horas.' }
          ].map((benefit, index) => (
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
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>
                {benefit.icon}
              </div>
              <h3 style={{
                fontSize: '1.25rem',
                fontWeight: '600',
                color: '#ffffff',
                marginBottom: '0.75rem'
              }}>
                {benefit.title}
              </h3>
              <p style={{
                fontSize: '0.95rem',
                color: '#9ca3af',
                lineHeight: '1.6'
              }}>
                {benefit.desc}
              </p>
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
          Nuestros Fondos de Inversión
        </h2>
        <p style={{
          fontSize: '1.125rem',
          color: '#9ca3af',
          textAlign: 'center',
          marginBottom: '3rem',
          maxWidth: '700px',
          margin: '0 auto 3rem'
        }}>
          Elige el fondo que mejor se adapte a tu perfil de riesgo y objetivos financieros
        </p>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '2rem',
          maxWidth: '1200px',
          margin: '0 auto'
        }}>
          {[
            {
              name: 'FIDUS CORE',
              logo: '/assets/logos/fidus-core.png',
              tagline: 'Estabilidad y Crecimiento',
              rate: '1.5%',
              annualRate: '18%',
              minInvestment: '$10,000',
              redemption: 'Mensual',
              color: '#f97316',
              features: ['Ideal para principiantes', 'Liquidez mensual', 'Menor riesgo']
            },
            {
              name: 'FIDUS BALANCE',
              logo: '/assets/logos/fidus-balance.png',
              tagline: 'Equilibrio Perfecto',
              rate: '2.5%',
              annualRate: '30%',
              minInvestment: '$50,000',
              redemption: 'Trimestral',
              color: '#06b6d4',
              popular: true,
              features: ['Más popular', 'Rendimiento balanceado', 'Estrategia diversificada']
            },
            {
              name: 'FIDUS DYNAMIC',
              logo: '/assets/logos/fidus-dynamic.png',
              tagline: 'Máximo Rendimiento',
              rate: '3.5%',
              annualRate: '42%',
              minInvestment: '$250,000',
              redemption: 'Semestral',
              color: '#8b5cf6',
              features: ['Para inversionistas avanzados', 'Máximo potencial', 'Gestión activa']
            }
          ].map((fund, index) => (
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
                  Más Popular
                </div>
              )}

              <div style={{
                background: fund.color,
                padding: '2rem',
                color: 'white'
              }}>
                {/* Fund Logo */}
                <div style={{
                  marginBottom: '1rem',
                  display: 'flex',
                  justifyContent: 'center'
                }}>
                  <img 
                    src={fund.logo}
                    alt={fund.name}
                    style={{
                      height: '80px',
                      width: 'auto',
                      objectFit: 'contain'
                    }}
                  />
                </div>
                
                <h3 style={{
                  fontSize: '1.75rem',
                  fontWeight: '700',
                  marginBottom: '0.5rem'
                }}>
                  {fund.name}
                </h3>
                <p style={{
                  fontSize: '1rem',
                  opacity: 0.9,
                  marginBottom: '1.5rem'
                }}>
                  {fund.tagline}
                </p>

                <div style={{ marginBottom: '1rem' }}>
                  <div style={{
                    fontSize: '3rem',
                    fontWeight: '700',
                    lineHeight: '1'
                  }}>
                    {fund.rate}
                  </div>
                  <div style={{
                    fontSize: '1rem',
                    opacity: 0.9
                  }}>
                    mensual ({fund.annualRate} anual)
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
                    <div style={{ opacity: 0.8 }}>Mínimo</div>
                    <div style={{ fontWeight: '600' }}>{fund.minInvestment}</div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ opacity: 0.8 }}>Redención</div>
                    <div style={{ fontWeight: '600' }}>{fund.redemption}</div>
                  </div>
                </div>
              </div>

              <div style={{ padding: '2rem', background: '#1f2937' }}>
                <ul style={{
                  listStyle: 'none',
                  padding: 0,
                  margin: '0 0 2rem 0'
                }}>
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
                    background: fund.color,
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
                  Simular Inversión
                </button>
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
        <div style={{ maxWidth: '550px', margin: '0 auto' }}>
          <h2 style={{
            fontSize: 'clamp(1.75rem, 3vw, 2rem)',
            fontWeight: '600',
            color: '#ffffff',
            textAlign: 'center',
            marginBottom: '0.5rem'
          }}>
            Comienza Tu Simulación de Inversión
          </h2>
          <p style={{
            fontSize: '1rem',
            color: '#9ca3af',
            textAlign: 'center',
            marginBottom: '2rem'
          }}>
            Ingresa tus datos para acceder al simulador interactivo
          </p>

          <form onSubmit={handleSubmit} style={{
            background: '#1f2937',
            padding: '2.5rem',
            borderRadius: '12px',
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)',
            border: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            {/* Email Field */}
            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{
                display: 'block',
                fontSize: '0.95rem',
                fontWeight: '500',
                color: '#ffffff',
                marginBottom: '0.5rem'
              }}>
                📧 Correo Electrónico
              </label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder="tu@email.com"
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

            {/* Phone Field */}
            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{
                display: 'block',
                fontSize: '0.95rem',
                fontWeight: '500',
                color: '#ffffff',
                marginBottom: '0.5rem'
              }}>
                📱 Teléfono (WhatsApp)
              </label>
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                placeholder="+1917-456-2151"
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

            {/* Submit Error */}
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

            {/* Submit Button */}
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
              {isSubmitting ? 'Procesando...' : 'Acceder al Simulador →'}
            </button>

            {/* Privacy Notice */}
            <p style={{
              fontSize: '0.75rem',
              color: '#9ca3af',
              textAlign: 'center',
              lineHeight: '1.4'
            }}>
              Al continuar, aceptas nuestra política de privacidad y términos de uso
            </p>
          </form>
        </div>
      </section>

      {/* SECTION 5: Footer */}
      <footer style={{
        padding: '3rem 2rem 2rem',
        background: '#1a1f2e',
        color: 'white',
        textAlign: 'center',
        borderTop: '1px solid rgba(255, 255, 255, 0.1)'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <img 
            src="/assets/LOGO_FULL_FIDUS.png" 
            alt="FIDUS Investment Management"
            style={{
              height: '50px',
              width: 'auto',
              marginBottom: '1.5rem',
              filter: 'brightness(0) invert(1)'
            }}
          />

          <p style={{
            fontSize: '1.125rem',
            marginBottom: '2rem',
            color: '#9ca3af'
          }}>
            Democratizamos el mundo financiero para todos
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
            © 2025 FIDUS Investment Management. Todos los derechos reservados.
          </div>
        </div>
      </footer>
    </div>
  );
};

export default ProspectsPortalNew;
