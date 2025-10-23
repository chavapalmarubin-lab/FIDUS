import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Mail, Phone, ArrowRight, Check, Loader2 } from 'lucide-react';
import InvestmentSimulator from './InvestmentSimulator';

const ProspectsPortal = () => {
  const [step, setStep] = useState('capture'); // 'capture' or 'simulator'
  const [formData, setFormData] = useState({
    email: '',
    phone: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [leadId, setLeadId] = useState(null);

  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  const validateEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const validatePhone = (phone) => {
    // International phone format: +[country code][number]
    const phoneRegex = /^\+?[1-9]\d{1,14}$/;
    return phoneRegex.test(phone.replace(/[\s-]/g, ''));
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validation
    if (!formData.email || !formData.phone) {
      setError('Por favor completa todos los campos');
      return;
    }

    if (!validateEmail(formData.email)) {
      setError('Por favor ingresa un email válido');
      return;
    }

    if (!validatePhone(formData.phone)) {
      setError('Por favor ingresa un teléfono válido (incluye código de país, ej: +52...)');
      return;
    }

    setLoading(true);

    try {
      console.log('[PROSPECTS] Submitting to:', `${backendUrl}/api/prospects/lead`);
      
      const response = await fetch(`${backendUrl}/api/prospects/lead`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          phone: formData.phone,
          source: 'prospects_portal'
        })
      });

      console.log('[PROSPECTS] Response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('[PROSPECTS] Error response:', errorText);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      console.log('[PROSPECTS] Response data:', data);

      if (data.success) {
        setLeadId(data.leadId);
        // Store lead info in session for tracking
        sessionStorage.setItem('fidus_lead_id', data.leadId);
        sessionStorage.setItem('fidus_lead_email', formData.email);
        // Move to simulator
        setStep('simulator');
      } else {
        setError(data.message || 'Error al procesar tu información. Intenta nuevamente.');
      }
    } catch (err) {
      console.error('[PROSPECTS] Lead submission error:', err);
      setError('Error de conexión. Por favor intenta nuevamente.');
    } finally {
      setLoading(false);
    }
  };

  // Lead Capture Form
  if (step === 'capture') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="w-full max-w-4xl"
        >
          {/* FIDUS Logo */}
          <div className="text-center mb-8">
            <h1 className="text-5xl font-bold text-white mb-4">
              FIDUS
            </h1>
            <div className="h-1 w-32 bg-gradient-to-r from-blue-400 to-cyan-400 mx-auto rounded-full" />
          </div>

          {/* Main Card */}
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl border border-white/20 shadow-2xl overflow-hidden">
            <div className="p-8 md:p-12">
              {/* Headline */}
              <div className="text-center mb-8">
                <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                  DEMOCRATIZAMOS EL MUNDO FINANCIERO
                  <br />
                  PARA TODOS
                </h2>
                <p className="text-xl text-blue-200">
                  Descubre cómo tu dinero puede crecer con FIDUS
                </p>
              </div>

              {/* Form */}
              <form onSubmit={handleSubmit} className="max-w-md mx-auto space-y-6">
                {/* Email Input */}
                <div>
                  <label className="block text-sm font-medium text-blue-100 mb-2">
                    📧 Email
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-4 top-1/2 transform -translate-y-1/2 text-blue-300 w-5 h-5" />
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) => handleInputChange('email', e.target.value)}
                      placeholder="tu@email.com"
                      className="w-full pl-12 pr-4 py-4 bg-white/10 border border-white/30 rounded-xl text-white placeholder-blue-300/50 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all"
                      required
                    />
                  </div>
                </div>

                {/* Phone Input */}
                <div>
                  <label className="block text-sm font-medium text-blue-100 mb-2">
                    📱 Teléfono
                  </label>
                  <div className="relative">
                    <Phone className="absolute left-4 top-1/2 transform -translate-y-1/2 text-blue-300 w-5 h-5" />
                    <input
                      type="tel"
                      value={formData.phone}
                      onChange={(e) => handleInputChange('phone', e.target.value)}
                      placeholder="+52 55 1234 5678"
                      className="w-full pl-12 pr-4 py-4 bg-white/10 border border-white/30 rounded-xl text-white placeholder-blue-300/50 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all"
                      required
                    />
                  </div>
                  <p className="mt-2 text-xs text-blue-300">
                    Incluye el código de país (ej: +52 para México)
                  </p>
                </div>

                {/* Error Message */}
                {error && (
                  <div className="bg-red-500/20 border border-red-500/50 rounded-xl p-4">
                    <p className="text-red-200 text-sm">{error}</p>
                  </div>
                )}

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white font-semibold py-4 px-6 rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      <span>Procesando...</span>
                    </>
                  ) : (
                    <>
                      <span>Simular Mi Inversión</span>
                      <ArrowRight className="w-5 h-5" />
                    </>
                  )}
                </button>
              </form>

              {/* Trust Indicators */}
              <div className="mt-8 flex flex-wrap items-center justify-center gap-6 text-blue-200 text-sm">
                <div className="flex items-center space-x-2">
                  <Check className="w-4 h-4 text-green-400" />
                  <span>Sin compromiso</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Check className="w-4 h-4 text-green-400" />
                  <span>Gratis</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Check className="w-4 h-4 text-green-400" />
                  <span>En 2 minutos</span>
                </div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="text-center mt-8 text-blue-200 text-sm">
            <p>30 años democratizando el mundo financiero</p>
          </div>
        </motion.div>
      </div>
    );
  }

  // Simulator View
  if (step === 'simulator') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-white mb-2">
              FIDUS
            </h1>
            <p className="text-blue-200">
              Simula tu inversión personalizada
            </p>
          </div>

          {/* Simulator Component */}
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl border border-white/20 shadow-2xl p-6 md:p-8">
            <InvestmentSimulator />
          </div>

          {/* CTA Section */}
          <div className="mt-8 text-center">
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl border border-white/20 p-6 max-w-2xl mx-auto">
              <h3 className="text-2xl font-bold text-white mb-4">
                ¿Listo para invertir?
              </h3>
              <p className="text-blue-200 mb-6">
                Habla con uno de nuestros asesores para comenzar
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button className="bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white font-semibold py-3 px-8 rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200">
                  📞 Agendar Llamada
                </button>
                <button className="bg-white/10 hover:bg-white/20 border border-white/30 text-white font-semibold py-3 px-8 rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200">
                  📄 Descargar Brochure
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return null;
};

export default ProspectsPortal;
