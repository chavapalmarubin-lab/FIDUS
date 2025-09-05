import React from "react";

const Progress = ({ value = 0, className = "", ...props }) => {
  const clampedValue = Math.min(100, Math.max(0, value));
  
  return (
    <div 
      className={`relative h-2 w-full overflow-hidden rounded-full bg-slate-700 ${className}`}
      {...props}
    >
      <div
        className="h-full w-full flex-1 bg-gradient-to-r from-cyan-500 to-blue-500 transition-all duration-300 ease-in-out"
        style={{
          transform: `translateX(-${100 - clampedValue}%)`
        }}
      />
    </div>
  );
};

export { Progress };