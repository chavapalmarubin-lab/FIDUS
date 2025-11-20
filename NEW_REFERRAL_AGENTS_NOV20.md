# New Referral Agents - Login Credentials

**Created:** November 20, 2025

---

## 📋 Agent 1: Carlos Ramos

**Name:** Carlos Ramos  
**Company:** Grupo Tevian  
**Email:** carlos.ramos@grupotevian.com  
**Temporary Password:** `Vwgioezsjws4BZHY`  
**Referral Code:** CR-2025-E8D8  
**Referral Link:** https://fidus-investment-platform.onrender.com/prospects?ref=CR-2025-E8D8  
**Status:** ✅ Active  
**MongoDB ID:** 691f80bf7ba31cabf6f9a34a

---

## 📋 Agent 2: Guillermo Garcia

**Name:** Guillermo Garcia  
**Company:** Bosch GH  
**Email:** ggarcia@boschgh.com  
**Temporary Password:** `SjI3PgRQz00YOMPb`  
**Referral Code:** GG-2025-5AAF  
**Referral Link:** https://fidus-investment-platform.onrender.com/prospects?ref=GG-2025-5AAF  
**Status:** ✅ Active  
**MongoDB ID:** 691f80bf7ba31cabf6f9a34b

---

## 🔐 Login Instructions

**Agent Portal URL:** https://fidus-investment-platform.onrender.com/agent-portal

### First Login Steps:
1. Go to the Agent Portal
2. Enter your email and temporary password
3. After successful login, change your password immediately
4. Configure your payment preferences (wallet details)

### Features Available:
- ✅ View referral dashboard with real-time stats
- ✅ Track leads through pipeline stages
- ✅ Monitor commissions and earnings
- ✅ Access unique referral links and QR codes
- ✅ Manage prospect communications
- ✅ View conversion analytics

---

## 📊 Current System Status

**Total Referral Agents:** 11  
**Active Agents:** 6

### All Active Agents:
1. Salvador Palma (chava@alyarglobal.com) - SP-2025
2. Josselyn Arellano López (Jazioni@yahoo.com.mx) - JA-2025
3. Oscar Camargo Toledano (orcamargot@gmail.com) - OC-2025-F1B3
4. Muñeca Treviño Salinas (muneca.trevino@gmail.com) - MT-2025-1A68
5. **Carlos Ramos (carlos.ramos@grupotevian.com) - CR-2025-E8D8** ⭐ NEW
6. **Guillermo Garcia (ggarcia@boschgh.com) - GG-2025-5AAF** ⭐ NEW

### Inactive Agents:
- Various test accounts and inactive referrals

---

## ⚠️ IMPORTANT SECURITY NOTES

1. **Change Password Immediately** - These temporary passwords should be changed after first login
2. **Do Not Share** - Credentials are personal and should not be shared
3. **Secure Storage** - Store passwords in a secure password manager
4. **Two-Factor Auth** - Enable if available in portal settings

---

## 🔧 Technical Details

**MongoDB Collection:** `salespeople`  
**Account Type:** Referral Agent  
**Default Language:** Spanish (es)  
**Timezone:** America/Mexico_City  
**Commission Method:** Crypto Wallet (default, can be changed)  

### Agent Features:
- Lead pipeline management with customizable stages
- Real-time commission tracking
- Email/SMS notification preferences
- Analytics dashboard with conversion metrics
- QR code generation for offline marketing
- Referral link tracking and click analytics

---

## 📞 Support

If agents have any issues:
1. **Password Reset:** Available via "Forgot Password" link on login page
2. **Technical Support:** Contact admin for technical assistance
3. **Dashboard Questions:** Help documentation available in portal
4. **Commission Questions:** Contact finance team

---

## 📧 Email Template for Agents

**Subject:** Welcome to FIDUS Referral Program - Your Login Credentials

**Body:**

```
Hola [Nombre],

¡Bienvenido al Programa de Referencias de FIDUS!

Tus credenciales de acceso al Portal de Agentes:

Portal: https://fidus-investment-platform.onrender.com/agent-portal
Email: [email]
Contraseña Temporal: [password]
Código de Referido: [referral_code]

Tu Link de Referido Personal:
[referral_link]

IMPORTANTE:
- Por favor cambia tu contraseña después del primer inicio de sesión
- Configura tus preferencias de pago en la sección de perfil
- Tu link de referido es único y rastrea todos tus clientes

Características del Portal:
✓ Dashboard con estadísticas en tiempo real
✓ Gestión de leads y pipeline de ventas
✓ Seguimiento de comisiones
✓ Generación de código QR
✓ Análisis de conversión

¿Necesitas ayuda? Contáctanos en cualquier momento.

Saludos,
Equipo FIDUS
```

---

## 🧪 Testing

To verify the agents can log in:

```bash
# Test login endpoint
curl -X POST "http://localhost:8001/api/referral-agent/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "carlos.ramos@grupotevian.com",
    "password": "Vwgioezsjws4BZHY"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "token": "eyJ...",
  "salesperson": {
    "name": "Carlos Ramos",
    "email": "carlos.ramos@grupotevian.com",
    "referral_code": "CR-2025-E8D8"
  }
}
```

---

**Document Generated:** 2025-11-20  
**Created By:** Emergent Agent E1  
**Session:** Phase 2 Referral Agent Setup
