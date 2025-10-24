import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ProspectsPortal from './components/ProspectsPortal';

function PublicApp() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/prospects/*" element={<ProspectsPortal />} />
        <Route path="/prospects" element={<ProspectsPortal />} />
        <Route path="*" element={<ProspectsPortal />} />
      </Routes>
    </BrowserRouter>
  );
}

export default PublicApp;
