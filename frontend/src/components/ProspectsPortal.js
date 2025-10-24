import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

// Main Prospects Portal Component - Marketing-Grade Landing Page
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

    // Phone validation
    const phoneRegex = /^[+]?[(]?[0-9]{1,4}[)]?[-\s.]?[(]?[0-9]{1,4}[)]?[-\s.]?[0-9]{4,10}$/;
    if (!formData.phone) {
      newErrors.phone = 'El teléfono es requerido';
    } else if (!phoneRegex.test(formData.phone.replace(/\s/g, ''))) {
      newErrors.phone = 'Teléfono inválido';
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
          // Store leadId
          localStorage.setItem('fidus_lead_id', leadId);
          // Redirect to simulator
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
      background: '#ffffff',
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
            src="/assets/LOGO_FULL_FIDUS.png" 
            alt="FIDUS Investment Management"
            style={{
              height: '60px',
              width: 'auto',
              filter: 'brightness(0) invert(1)'
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
          background: 'radial-gradient(circle at 30% 50%, #15a4d9 0%, transparent 50%), radial-gradient(circle at 70% 80%, #f5a623 0%, transparent 50%)'
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
            { icon: '💎', title: 'Transparencia Total', desc: 'Acceso completo a tu cuenta MT5. Ve tus inversiones en tiempo real, 24/7.' },
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
              e.currentTarget.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.1)';
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
                color: '#1e2843',
                marginBottom: '0.75rem'
              }}>
                {benefit.title}
              </h3>
              <p style={{
                fontSize: '0.95rem',
                color: '#666',
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
        background: 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)'
      }}>
        <h2 style={{
          fontSize: 'clamp(2rem, 4vw, 2.5rem)',
          fontWeight: '600',
          color: '#1e2843',
          textAlign: 'center',
          marginBottom: '1rem'
        }}>
          Nuestros Fondos de Inversión
        </h2>
        <p style={{
          fontSize: '1.125rem',
          color: '#666',
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
              tagline: 'Estabilidad y Crecimiento',
              rate: '1.5%',
              annualRate: '18%',
              minInvestment: '$10,000',
              redemption: 'Mensual',
              color: '#0b5ea8',
              features: ['Ideal para principiantes', 'Liquidez mensual', 'Menor riesgo']
            },
            {
              name: 'FIDUS BALANCE',
              tagline: 'Equilibrio Perfecto',
              rate: '2.5%',
              annualRate: '30%',
              minInvestment: '$50,000',
              redemption: 'Trimestral',
              color: '#15a4d9',
              popular: true,
              features: ['Más popular', 'Rendimiento balanceado', 'Estrategia diversificada']
            },
            {
              name: 'FIDUS DYNAMIC',
              tagline: 'Máximo Rendimiento',
              rate: '3.5%',
              annualRate: '42%',
              minInvestment: '$250,000',
              redemption: 'Semestral',
              color: '#1e2843',
              features: ['Para inversionistas avanzados', 'Máximo potencial', 'Gestión activa']
            }
          ].map((fund, index) => (
            <div key={index} style={{
              background: 'white',
              borderRadius: '16px',
              overflow: 'hidden',
              boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
              position: 'relative',
              border: fund.popular ? '3px solid #f5a623' : 'none',
              transform: fund.popular ? 'scale(1.05)' : 'scale(1)',
              transition: 'all 0.3s ease'
            }}>
              {fund.popular && (
                <div style={{
                  position: 'absolute',
                  top: '1rem',
                  right: '1rem',
                  background: '#f5a623',
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

              <div style={{ padding: '2rem' }}>
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
                      color: '#666',
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
                    e.target.style.boxShadow = '0 6px 20px rgba(0, 0, 0, 0.15)';
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
        background: '#ffffff'
      }}>
        <div style={{ maxWidth: '550px', margin: '0 auto' }}>
          <h2 style={{
            fontSize: 'clamp(1.75rem, 3vw, 2rem)',
            fontWeight: '600',
            color: '#1e2843',
            textAlign: 'center',
            marginBottom: '0.5rem'
          }}>
            Comienza Tu Simulación de Inversión
          </h2>
          <p style={{
            fontSize: '1rem',
            color: '#666',
            textAlign: 'center',
            marginBottom: '2rem'
          }}>
            Ingresa tus datos para acceder al simulador interactivo
          </p>

          <form onSubmit={handleSubmit} style={{
            background: 'white',
            padding: '2.5rem',
            borderRadius: '12px',
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
            border: '1px solid #e0e0e0'
          }}>
            {/* Email Field */}
            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{
                display: 'block',
                fontSize: '0.95rem',
                fontWeight: '500',
                color: '#1e2843',
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
                  border: errors.email ? '2px solid #dc3545' : '2px solid #e0e0e0',
                  borderRadius: '8px',
                  outline: 'none',
                  transition: 'border-color 0.3s ease',
                  boxSizing: 'border-box'
                }}
                onFocus={(e) => e.target.style.borderColor = '#0b5ea8'}
                onBlur={(e) => e.target.style.borderColor = errors.email ? '#dc3545' : '#e0e0e0'}
              />
              {errors.email && (
                <span style={{ color: '#dc3545', fontSize: '0.875rem', marginTop: '0.25rem', display: 'block' }}>
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
                color: '#1e2843',
                marginBottom: '0.5rem'
              }}>
                📱 Teléfono (WhatsApp)
              </label>
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                placeholder="+52 55 1234 5678"
                style={{
                  width: '100%',
                  padding: '0.875rem',
                  fontSize: '1rem',
                  border: errors.phone ? '2px solid #dc3545' : '2px solid #e0e0e0',
                  borderRadius: '8px',
                  outline: 'none',
                  transition: 'border-color 0.3s ease',
                  boxSizing: 'border-box'
                }}
                onFocus={(e) => e.target.style.borderColor = '#0b5ea8'}
                onBlur={(e) => e.target.style.borderColor = errors.phone ? '#dc3545' : '#e0e0e0'}
              />
              {errors.phone && (
                <span style={{ color: '#dc3545', fontSize: '0.875rem', marginTop: '0.25rem', display: 'block' }}>
                  {errors.phone}
                </span>
              )}
            </div>

            {/* Submit Error */}
            {errors.submit && (
              <div style={{
                padding: '1rem',
                background: '#fee',
                border: '1px solid #fcc',
                borderRadius: '8px',
                marginBottom: '1.5rem',
                color: '#c33',
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
                background: isSubmitting ? '#ccc' : '#0b5ea8',
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
              color: '#666',
              textAlign: 'center',
              lineHeight: '1.4'
            }}>
              Al continuar, aceptas nuestra política de privacidad y términos de uso
            </p>
          </form>
        </div>
      </section>

      {/* SECTION 5: How It Works */}
      <section style={{
        padding: '5rem 2rem',
        background: '#f8f9fa'
      }}>
        <h2 style={{
          fontSize: 'clamp(2rem, 4vw, 2.5rem)',
          fontWeight: '600',
          color: '#1e2843',
          textAlign: 'center',
          marginBottom: '3rem'
        }}>
          Cómo Funciona
        </h2>

        <div style={{
          maxWidth: '1100px',
          margin: '0 auto',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '2rem',
          position: 'relative'
        }}>
          {[
            { icon: '📊', title: 'Simula Tu Inversión', desc: 'Ingresa tu correo y teléfono para acceder a nuestro simulador interactivo.' },
            { icon: '🎯', title: 'Elige Tu Fondo', desc: 'Compara rendimientos, plazos y condiciones de cada fondo FIDUS.' },
            { icon: '📝', title: 'Abre Tu Cuenta', desc: 'Proceso 100% digital con verificación de identidad en menos de 48 horas.' },
            { icon: '🚀', title: 'Comienza a Invertir', desc: 'Deposita y ve tu inversión crecer con acceso completo a tu cuenta MT5.' }
          ].map((step, index) => (
            <div key={index} style={{
              textAlign: 'center',
              position: 'relative',
              zIndex: 1
            }}>
              <div style={{
                width: '100px',
                height: '100px',
                margin: '0 auto 1.5rem',
                background: 'linear-gradient(135deg, #0b5ea8 0%, #15a4d9 100%)',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '3rem',
                boxShadow: '0 4px 15px rgba(11, 94, 168, 0.3)'
              }}>
                {step.icon}
              </div>

              <h3 style={{
                fontSize: '1.25rem',
                fontWeight: '600',
                color: '#1e2843',
                marginBottom: '0.75rem'
              }}>
                {step.title}
              </h3>
              <p style={{
                fontSize: '0.95rem',
                color: '#666',
                lineHeight: '1.6',
                maxWidth: '220px',
                margin: '0 auto'
              }}>
                {step.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* SECTION 6: Social Proof */}
      <section style={{
        padding: '5rem 2rem',
        background: 'linear-gradient(135deg, #1e2843 0%, #0b5ea8 100%)',
        color: 'white'
      }}>
        <h2 style={{
          fontSize: 'clamp(2rem, 4vw, 2.5rem)',
          fontWeight: '600',
          textAlign: 'center',
          marginBottom: '3rem'
        }}>
          Lo Que Dicen Nuestros Clientes
        </h2>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '2rem',
          maxWidth: '1200px',
          margin: '0 auto 4rem'
        }}>
          {[
            { quote: "FIDUS transformó mi manera de invertir. Transparencia total y rendimientos consistentes mes tras mes.", author: "María G.", role: "Inversionista BALANCE" },
            { quote: "Después de 2 años invirtiendo, puedo decir que FIDUS cumple todo lo que promete. Altamente recomendado.", author: "Roberto M.", role: "Inversionista DYNAMIC" },
            { quote: "El acceso directo a MT5 me da tranquilidad total. Veo mis operaciones en tiempo real, sin intermediarios.", author: "Laura S.", role: "Inversionista CORE" }
          ].map((testimonial, index) => (
            <div key={index} style={{
              background: 'rgba(255, 255, 255, 0.1)',
              backdropFilter: 'blur(10px)',
              padding: '2rem',
              borderRadius: '12px',
              border: '1px solid rgba(255, 255, 255, 0.2)'
            }}>
              <div style={{ marginBottom: '1rem', fontSize: '1.25rem' }}>
                {'⭐'.repeat(5)}
              </div>

              <p style={{
                fontSize: '1.05rem',
                lineHeight: '1.7',
                marginBottom: '1.5rem',
                fontStyle: 'italic'
              }}>
                "{testimonial.quote}"
              </p>

              <div>
                <div style={{ fontWeight: '600', fontSize: '1.05rem' }}>
                  {testimonial.author}
                </div>
                <div style={{ fontSize: '0.9rem', opacity: 0.8 }}>
                  {testimonial.role}
                </div>
              </div>
            </div>
          ))}
        </div>

        <div style={{
          textAlign: 'center',
          paddingTop: '3rem',
          borderTop: '1px solid rgba(255, 255, 255, 0.2)'
        }}>
          <p style={{ marginBottom: '1.5rem', opacity: 0.9 }}>
            Operamos con brokers regulados internacionalmente
          </p>
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            gap: '3rem',
            flexWrap: 'wrap',
            alignItems: 'center'
          }}>
            {['MEXAtlantic', 'Regulación Internacional', 'Seguridad Garantizada'].map((text, i) => (
              <div key={i} style={{ opacity: 0.7, fontSize: '0.9rem' }}>{text}</div>
            ))}
          </div>
        </div>
      </section>

      {/* SECTION 7: Final CTA */}
      <section style={{
        padding: '5rem 2rem',
        background: '#f5a623',
        textAlign: 'center'
      }}>
        <h2 style={{
          fontSize: 'clamp(2rem, 4vw, 2.5rem)',
          fontWeight: '700',
          color: '#1e2843',
          marginBottom: '1rem'
        }}>
          ¿Listo para Empezar a Invertir?
        </h2>
        <p style={{
          fontSize: '1.25rem',
          color: '#1e2843',
          opacity: 0.9,
          marginBottom: '2.5rem',
          maxWidth: '600px',
          margin: '0 auto 2.5rem'
        }}>
          Simula tu inversión ahora y descubre tu potencial de rendimiento con FIDUS
        </p>

        <button
          onClick={() => scrollToSection('lead-capture')}
          style={{
            background: '#1e2843',
            color: 'white',
            padding: '1.25rem 3.5rem',
            fontSize: '1.25rem',
            fontWeight: '600',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            transition: 'all 0.3s ease',
            boxShadow: '0 4px 20px rgba(30, 40, 67, 0.3)'
          }}
          onMouseEnter={(e) => {
            e.target.style.transform = 'translateY(-3px)';
            e.target.style.boxShadow = '0 6px 25px rgba(30, 40, 67, 0.4)';
          }}
          onMouseLeave={(e) => {
            e.target.style.transform = 'translateY(0)';
            e.target.style.boxShadow = '0 4px 20px rgba(30, 40, 67, 0.3)';
          }}
        >
          Comenzar Simulación Gratis →
        </button>

        <p style={{
          marginTop: '1.5rem',
          fontSize: '0.95rem',
          color: '#1e2843',
          opacity: 0.7
        }}>
          Sin compromiso • Gratis • En menos de 2 minutos
        </p>
      </section>

      {/* SECTION 8: Footer */}
      <footer style={{
        padding: '3rem 2rem 2rem',
        background: '#1e2843',
        color: 'white',
        textAlign: 'center'
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
            opacity: 0.9
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
            opacity: 0.8
          }}>
            <div>📧 info@fidusinvestment.com</div>
            <div>📱 WhatsApp: +52 55 1234 5678</div>
          </div>

          <div style={{
            paddingTop: '2rem',
            borderTop: '1px solid rgba(255, 255, 255, 0.2)',
            fontSize: '0.875rem',
            opacity: 0.7
          }}>
            © 2025 FIDUS Investment Management. Todos los derechos reservados.
          </div>
        </div>
      </footer>
    </div>
  );
};

export default ProspectsPortalNew;
