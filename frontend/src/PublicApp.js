import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ProspectsPortalNew from './components/ProspectsPortalNew';

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
