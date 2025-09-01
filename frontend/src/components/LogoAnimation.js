import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";

const LogoAnimation = ({ onComplete }) => {
  const [showElements, setShowElements] = useState(true);
  const [showLogo, setShowLogo] = useState(false);

  useEffect(() => {
    // Show financial elements first, then merge into logo
    const timer1 = setTimeout(() => {
      setShowElements(false);
      setShowLogo(true);
    }, 2000);

    const timer2 = setTimeout(() => {
      onComplete();
    }, 4000);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
    };
  }, [onComplete]);

  const FinancialElements = () => (
    <>
      {/* Candlestick Chart */}
      <motion.div
        className="financial-element"
        style={{ top: "20%", left: "15%" }}
        initial={{ opacity: 0, scale: 0 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ 
          x: window.innerWidth / 2 - window.innerWidth * 0.15,
          y: window.innerHeight / 2 - window.innerHeight * 0.2,
          scale: 0,
          opacity: 0
        }}
        transition={{ duration: 1.5, delay: 0.2 }}
      >
        <svg className="candlestick-chart" viewBox="0 0 120 80" fill="none">
          <rect x="10" y="30" width="8" height="25" fill="#4caf50" />
          <line x1="14" y1="20" x2="14" y2="60" stroke="#4caf50" strokeWidth="2" />
          <rect x="30" y="40" width="8" height="15" fill="#f44336" />
          <line x1="34" y1="25" x2="34" y2="65" stroke="#f44336" strokeWidth="2" />
          <rect x="50" y="25" width="8" height="30" fill="#4caf50" />
          <line x1="54" y1="15" x2="54" y2="65" stroke="#4caf50" strokeWidth="2" />
          <rect x="70" y="35" width="8" height="20" fill="#4caf50" />
          <line x1="74" y1="20" x2="74" y2="70" stroke="#4caf50" strokeWidth="2" />
          <rect x="90" y="45" width="8" height="10" fill="#f44336" />
          <line x1="94" y1="30" x2="94" y2="60" stroke="#f44336" strokeWidth="2" />
        </svg>
      </motion.div>

      {/* Line Chart */}
      <motion.div
        className="financial-element"
        style={{ top: "15%", right: "20%" }}
        initial={{ opacity: 0, scale: 0 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ 
          x: -(window.innerWidth * 0.8 - window.innerWidth / 2),
          y: window.innerHeight / 2 - window.innerHeight * 0.15,
          scale: 0,
          opacity: 0
        }}
        transition={{ duration: 1.5, delay: 0.4 }}
      >
        <svg className="line-chart" viewBox="0 0 100 60" fill="none">
          <polyline 
            points="10,45 25,35 40,40 55,25 70,30 85,20" 
            stroke="#00bcd4" 
            strokeWidth="3" 
            fill="none"
          />
          <circle cx="10" cy="45" r="3" fill="#00bcd4" />
          <circle cx="25" cy="35" r="3" fill="#00bcd4" />
          <circle cx="40" cy="40" r="3" fill="#00bcd4" />
          <circle cx="55" cy="25" r="3" fill="#00bcd4" />
          <circle cx="70" cy="30" r="3" fill="#00bcd4" />
          <circle cx="85" cy="20" r="3" fill="#00bcd4" />
        </svg>
      </motion.div>

      {/* Pie Chart */}
      <motion.div
        className="financial-element"
        style={{ bottom: "25%", left: "20%" }}
        initial={{ opacity: 0, scale: 0 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ 
          x: window.innerWidth / 2 - window.innerWidth * 0.2,
          y: -(window.innerHeight * 0.75 - window.innerHeight / 2),
          scale: 0,
          opacity: 0
        }}
        transition={{ duration: 1.5, delay: 0.6 }}
      >
        <svg className="pie-chart" viewBox="0 0 80 80" fill="none">
          <circle cx="40" cy="40" r="30" fill="#ffa726" />
          <path d="M 40 40 L 40 10 A 30 30 0 0 1 65 50 Z" fill="#00bcd4" />
          <path d="M 40 40 L 65 50 A 30 30 0 0 1 25 65 Z" fill="#4caf50" />
        </svg>
      </motion.div>

      {/* Network Diagram */}
      <motion.div
        className="financial-element"
        style={{ bottom: "20%", right: "15%" }}
        initial={{ opacity: 0, scale: 0 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ 
          x: -(window.innerWidth * 0.85 - window.innerWidth / 2),
          y: -(window.innerHeight * 0.8 - window.innerHeight / 2),
          scale: 0,
          opacity: 0
        }}
        transition={{ duration: 1.5, delay: 0.8 }}
      >
        <svg className="network-diagram" viewBox="0 0 100 100" fill="none">
          <line x1="20" y1="30" x2="50" y2="50" stroke="#00bcd4" strokeWidth="2" />
          <line x1="50" y1="50" x2="80" y2="30" stroke="#00bcd4" strokeWidth="2" />
          <line x1="50" y1="50" x2="70" y2="75" stroke="#00bcd4" strokeWidth="2" />
          <line x1="50" y1="50" x2="30" y2="75" stroke="#00bcd4" strokeWidth="2" />
          <circle cx="20" cy="30" r="8" fill="#ffa726" />
          <circle cx="50" cy="50" r="8" fill="#00bcd4" />
          <circle cx="80" cy="30" r="8" fill="#4caf50" />
          <circle cx="70" cy="75" r="8" fill="#ffa726" />
          <circle cx="30" cy="75" r="8" fill="#4caf50" />
        </svg>
      </motion.div>

      {/* Data Blocks */}
      <motion.div
        className="financial-element"
        style={{ top: "60%", left: "50%", transform: "translateX(-50%)" }}
        initial={{ opacity: 0, scale: 0 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ 
          y: -(window.innerHeight * 0.6 - window.innerHeight / 2),
          scale: 0,
          opacity: 0
        }}
        transition={{ duration: 1.5, delay: 1 }}
      >
        <svg className="data-blocks" viewBox="0 0 90 70" fill="none">
          <rect x="5" y="10" width="15" height="12" fill="#00bcd4" />
          <rect x="25" y="15" width="15" height="8" fill="#4caf50" />
          <rect x="45" y="5" width="15" height="18" fill="#ffa726" />
          <rect x="65" y="12" width="15" height="10" fill="#00bcd4" />
          <rect x="5" y="30" width="15" height="15" fill="#4caf50" />
          <rect x="25" y="35" width="15" height="10" fill="#ffa726" />
          <rect x="45" y="25" width="15" height="20" fill="#00bcd4" />
          <rect x="65" y="32" width="15" height="13" fill="#4caf50" />
        </svg>
      </motion.div>
    </>
  );

  return (
    <div style={{
      position: "fixed",
      top: 0,
      left: 0,
      width: "100vw",
      height: "100vh",
      background: "linear-gradient(135deg, #0a0f1c 0%, #1a2238 50%, #2a3f5f 100%)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      overflow: "hidden",
      zIndex: 9999
    }}>
      {/* Background Pattern */}
      <div style={{
        position: "absolute",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundImage: `
          radial-gradient(circle at 20% 80%, rgba(0, 188, 212, 0.1) 0%, transparent 50%),
          radial-gradient(circle at 80% 20%, rgba(255, 167, 38, 0.1) 0%, transparent 50%)
        `,
        pointerEvents: "none"
      }} />

      {/* Financial Elements */}
      {showElements && <FinancialElements />}

      {/* FIDUS Logo */}
      <motion.div
        className="fidus-logo"
        initial={{ opacity: 0, scale: 0 }}
        animate={showLogo ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0 }}
        transition={{ duration: 1, delay: 0.5 }}
      >
        <span className="fidus-logo-f">F</span>
        <span>IDUS</span>
      </motion.div>

      {/* Pulsing Effect */}
      {showLogo && (
        <motion.div
          style={{
            position: "absolute",
            width: "300px",
            height: "300px",
            border: "2px solid rgba(0, 188, 212, 0.3)",
            borderRadius: "50%",
            pointerEvents: "none"
          }}
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.1, 0.3]
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
      )}
    </div>
  );
};

export default LogoAnimation;