import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import axios from 'axios';
import { CheckCircle, TrendingUp, Shield, DollarSign, AlertCircle } from 'lucide-react';

const ProspectSignup = () => {
  const [searchParams] = useSearchParams();
  const referralCode = searchParams.get('ref');
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: ''
  });
  
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [agentName, setAgentName] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const API_URL = process.env.REACT_APP_BACKEND_URL || '';
      const response = await axios.post(
        `${API_URL}/api/public/prospect-signup`,
        {
          ...formData,
          referral_code: referralCode
        }
      );

      if (response.data.success) {
        setSubmitted(true);
        setAgentName(response.data.agentName || '');
      }
    } catch (err) {
      console.error('Signup error:', err);
      setError(err.response?.data?.detail || 'Error al procesar tu solicitud. Por favor intenta nuevamente.');
    } finally {
      setLoading(false);
    }
  };

  if (!referralCode) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
        <div className="bg-white rounded-xl shadow-2xl p-8 max-w-md text-center">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-slate-900 mb-2">Código de Referencia Inválido</h2>
          <p className="text-slate-600 mb-6">
            Por favor verifica el enlace y vuelve a intentarlo.
          </p>
          <a
            href="https://fidus-investment-platform.onrender.com"
            className="inline-block bg-cyan-600 hover:bg-cyan-700 text-white font-semibold px-6 py-3 rounded-lg transition-colors"
          >
            Ir a FIDUS
          </a>
        </div>
      </div>
    );
  }

  if (submitted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
        <div className="bg-white rounded-xl shadow-2xl p-8 max-w-md text-center">
          <div className="bg-green-100 rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="w-12 h-12 text-green-500" />
          </div>
          <h2 className="text-3xl font-bold text-slate-900 mb-3">
            ¡Gracias por tu Interés!
          </h2>
          <p className="text-lg text-slate-600 mb-2">
            Hemos recibido tu información correctamente.
          </p>
          {agentName && (
            <p className="text-slate-600 mb-6">
              <span className="font-semibold text-cyan-600">{agentName}</span> se pondrá en contacto contigo en las próximas 24 horas.
            </p>
          )}
          <div className="bg-cyan-50 border border-cyan-200 rounded-lg p-4 mb-6">
            <p className="text-sm text-cyan-800">
              📧 Te enviaremos un correo de confirmación a <strong>{formData.email}</strong>
            </p>
          </div>
          <a
            href="https://fidus-investment-platform.onrender.com"
            className="inline-block text-cyan-600 hover:text-cyan-700 font-semibold"
          >
            Conocer más sobre FIDUS →
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <div className="bg-slate-900/80 backdrop-blur-sm border-b border-slate-700 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-5">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white">FIDUS</h1>
              <p className="text-cyan-400 text-sm">Investment Management</p>
            </div>
            <div className="text-right">
              <p className="text-slate-400 text-sm">Código de Referencia</p>
              <p className="text-cyan-400 font-bold">{referralCode}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 py-12">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left: Benefits */}
          <div className="text-white">
            <h2 className="text-5xl font-bold mb-4 bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
              Invierte con Confianza
            </h2>
            <p className="text-2xl text-slate-300 mb-10">
              Obtén rendimientos garantizados desde <span className="text-cyan-400 font-bold">1.5% hasta 2.5%</span> mensual
            </p>

            <div className="space-y-6 mb-10">
              <div className="flex gap-4 bg-slate-800/50 backdrop-blur-sm rounded-xl p-5 border border-slate-700">
                <div className="bg-gradient-to-br from-cyan-600 to-cyan-800 rounded-lg p-3 h-fit">
                  <TrendingUp className="w-7 h-7 text-white" />
                </div>
                <div>
                  <h3 className="font-bold text-xl mb-2 text-cyan-400">Alto Rendimiento</h3>
                  <p className="text-slate-300">
                    Hasta <strong className="text-white">30% anual</strong> en nuestros fondos premium
                  </p>
                </div>
              </div>

              <div className="flex gap-4 bg-slate-800/50 backdrop-blur-sm rounded-xl p-5 border border-slate-700">
                <div className="bg-gradient-to-br from-green-600 to-green-800 rounded-lg p-3 h-fit">
                  <Shield className="w-7 h-7 text-white" />
                </div>
                <div>
                  <h3 className="font-bold text-xl mb-2 text-green-400">100% Garantizado</h3>
                  <p className="text-slate-300">
                    Tu capital está <strong className="text-white">protegido</strong> con contratos legales
                  </p>
                </div>
              </div>

              <div className="flex gap-4 bg-slate-800/50 backdrop-blur-sm rounded-xl p-5 border border-slate-700">
                <div className="bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg p-3 h-fit">
                  <DollarSign className="w-7 h-7 text-white" />
                </div>
                <div>
                  <h3 className="font-bold text-xl mb-2 text-blue-400">Pagos Mensuales</h3>
                  <p className="text-slate-300">
                    Recibe intereses <strong className="text-white">cada mes</strong> directo a tu cuenta
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-r from-cyan-600/20 to-blue-600/20 border border-cyan-500/50 rounded-xl p-6">
              <p className="text-cyan-300 text-lg">
                💼 <strong>Inversión mínima:</strong> $50,000 MXN
              </p>
              <p className="text-slate-300 text-sm mt-2">
                Sin comisiones ocultas • Retiro flexible • Asesoría personalizada
              </p>
            </div>
          </div>

          {/* Right: Form */}
          <div className="bg-white rounded-2xl shadow-2xl p-8 lg:p-10">
            <div className="text-center mb-8">
              <div className="bg-gradient-to-r from-cyan-600 to-blue-600 text-white text-sm font-semibold px-4 py-2 rounded-full inline-block mb-4">
                ✨ Oferta Especial
              </div>
              <h3 className="text-3xl font-bold text-slate-900 mb-2">
                Comienza Tu Inversión
              </h3>
              <p className="text-slate-600">
                Déjanos tus datos y te contactaremos en <strong>menos de 24 horas</strong>
              </p>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6 flex items-start gap-3">
                <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                <span className="text-sm">{error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  Nombre Completo *
                </label>
                <input
                  type="text"
                  required
                  className="w-full px-4 py-3 border-2 border-slate-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition-all"
                  placeholder="Ej: Juan Pérez González"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  Correo Electrónico *
                </label>
                <input
                  type="email"
                  required
                  className="w-full px-4 py-3 border-2 border-slate-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition-all"
                  placeholder="juan@ejemplo.com"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  Teléfono / WhatsApp *
                </label>
                <input
                  type="tel"
                  required
                  className="w-full px-4 py-3 border-2 border-slate-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition-all"
                  placeholder="+52 555 123 4567"
                  value={formData.phone}
                  onChange={(e) => setFormData({...formData, phone: e.target.value})}
                />
                <p className="text-xs text-slate-500 mt-1">
                  Incluye código de área para WhatsApp
                </p>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-700 hover:to-blue-700 text-white font-bold py-4 px-6 rounded-lg transition-all disabled:opacity-50 shadow-lg hover:shadow-xl transform hover:scale-[1.02]"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    Enviando...
                  </span>
                ) : (
                  <>
                    💰 Quiero Invertir Ahora →
                  </>
                )}
              </button>

              <p className="text-xs text-slate-500 text-center mt-4">
                🔒 Tu información está protegida. Al enviar aceptas nuestros{' '}
                <a href="#" className="text-cyan-600 hover:underline">términos y condiciones</a>
              </p>
            </form>
          </div>
        </div>

        {/* Footer Trust Badges */}
        <div className="mt-16 text-center">
          <p className="text-slate-400 text-sm mb-4">Confiado por más de 500 inversionistas en México</p>
          <div className="flex justify-center gap-8 text-slate-500">
            <div>✓ Regulado</div>
            <div>✓ Seguro</div>
            <div>✓ Transparente</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProspectSignup;
