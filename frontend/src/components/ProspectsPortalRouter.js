import React from 'react';
import { Routes, Route, useParams } from 'react-router-dom';
import ProspectsPortal from './ProspectsPortal';
import InvestmentSimulator from './InvestmentSimulator';

// Wrapper component to handle prospects portal routes
const ProspectsPortalRouter = () => {
  return (
    <Routes>
      <Route path="/" element={<ProspectsPortal />} />
      <Route path="/simulator/:leadId" element={<SimulatorPage />} />
    </Routes>
  );
};

// Simulator page component
const SimulatorPage = () => {
  const { leadId } = useParams();
  
  return (
    <div style={{
      minHeight: '100vh',
      background: '#0f1419',
      padding: '2rem 1rem'
    }}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto'
      }}>
        <InvestmentSimulator isPublic={true} leadInfo={{ id: leadId }} />
      </div>
    </div>
  );
};

export default ProspectsPortalRouter;
