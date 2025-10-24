import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ProspectsPortal from './components/ProspectsPortal';

function PublicApp() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/prospects/*" element={<ProspectsPortalNew />} />
        <Route path="/prospects" element={<ProspectsPortalNew />} />
        <Route path="*" element={<ProspectsPortalNew />} />
      </Routes>
    </BrowserRouter>
  );
}

export default PublicApp;
