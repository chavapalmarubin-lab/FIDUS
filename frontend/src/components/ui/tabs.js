import React, { createContext, useContext, useState } from "react";
import { motion } from "framer-motion";

const TabsContext = createContext();

export const Tabs = ({ defaultValue, value, onValueChange, className = "", children, ...props }) => {
  const [selectedTab, setSelectedTab] = useState(defaultValue || value);
  
  const handleTabChange = (newValue) => {
    setSelectedTab(newValue);
    if (onValueChange) {
      onValueChange(newValue);
    }
  };

  const contextValue = {
    selectedTab: value || selectedTab,
    onTabChange: handleTabChange
  };

  return (
    <TabsContext.Provider value={contextValue}>
      <div className={`w-full ${className}`} {...props}>
        {children}
      </div>
    </TabsContext.Provider>
  );
};

export const TabsList = ({ className = "", children, ...props }) => {
  return (
    <div 
      className={`inline-flex h-10 items-center justify-center rounded-md bg-muted p-1 text-muted-foreground ${className}`} 
      {...props}
    >
      {children}
    </div>
  );
};

export const TabsTrigger = ({ value, className = "", children, disabled = false, ...props }) => {
  const { selectedTab, onTabChange } = useContext(TabsContext);
  const isSelected = selectedTab === value;

  return (
    <button
      type="button"
      disabled={disabled}
      onClick={() => !disabled && onTabChange(value)}
      className={`
        inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5 text-sm font-medium 
        ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 
        focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50
        ${isSelected 
          ? 'bg-background text-foreground shadow-sm' 
          : 'hover:bg-muted/50 hover:text-foreground'
        }
        ${className}
      `}
      {...props}
    >
      {children}
    </button>
  );
};

export const TabsContent = ({ value, className = "", children, ...props }) => {
  const { selectedTab } = useContext(TabsContext);
  
  if (selectedTab !== value) {
    return null;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.2 }}
      className={`mt-2 ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 ${className}`}
      {...props}
    >
      {children}
    </motion.div>
  );
};