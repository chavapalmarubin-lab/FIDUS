import React from 'react';
import { Routes, Route } from 'react-router-dom';
import ProspectsPortalNew from './components/ProspectsPortalNew';

function PublicApp() {
  return (
    <Routes>
      <Route path="/prospects/*" element={<ProspectsPortalNew />} />
      <Route path="/prospects" element={<ProspectsPortalNew />} />
      <Route path="*" element={<ProspectsPortalNew />} />
    </Routes>
  );
}

export default PublicApp;
