import React from 'react';
import { ChevronRight, Home } from 'lucide-react';

const Breadcrumb = ({ items = [] }) => {
  if (!items.length) return null;

  return (
    <nav className="flex items-center space-x-2 text-sm text-slate-400 mb-6">
      <Home size={16} className="text-slate-500" />
      
      {items.map((item, index) => (
        <React.Fragment key={index}>
          <ChevronRight size={14} className="text-slate-600" />
          
          {item.href && !item.active ? (
            <button
              onClick={item.onClick}
              className="text-cyan-400 hover:text-cyan-300 transition-colors cursor-pointer"
            >
              {item.label}
            </button>
          ) : (
            <span 
              className={`${
                item.active 
                  ? 'text-white font-medium' 
                  : 'text-slate-400'
              }`}
            >
              {item.label}
            </span>
          )}
        </React.Fragment>
      ))}
    </nav>
  );
};

export { Breadcrumb };