import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ProspectsPortalRouter from './components/ProspectsPortalRouter';

function PublicApp() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/prospects/*" element={<ProspectsPortalRouter />} />
        <Route path="*" element={<ProspectsPortalRouter />} />
      </Routes>
    </BrowserRouter>
  );
}

export default PublicApp;
