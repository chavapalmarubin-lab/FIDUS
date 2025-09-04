import React, { useEffect } from "react";
import { motion } from "framer-motion";

const LogoAnimation = ({ onComplete }) => {
  useEffect(() => {
    // Ensure animation completes after 5 seconds regardless of other issues
    const timer = setTimeout(() => {
      console.log("Logo animation force complete");
      if (onComplete) {
        onComplete();
      }
    }, 5000);

    return () => clearTimeout(timer);
  }, [onComplete]);

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100vw",
        height: "100vh",
        background: "linear-gradient(135deg, #1e3a8a 0%, #1e40af 50%, #3b82f6 100%)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 9999,
      }}
    >
      {/* Simple animated logo */}
      <motion.div
        initial={{ opacity: 0, scale: 0.5 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 2, ease: "easeOut" }}
        style={{
          textAlign: "center",
          color: "white",
        }}
      >
        <motion.div
          initial={{ y: -50 }}
          animate={{ y: 0 }}
          transition={{ duration: 1.5, delay: 0.5 }}
          style={{
            fontSize: "72px",
            fontWeight: "bold",
            marginBottom: "20px",
            textShadow: "0 0 30px rgba(255,255,255,0.5)",
          }}
        >
          FIDUS
        </motion.div>
        
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 2 }}
          style={{
            fontSize: "24px",
            color: "#a1a1aa",
            letterSpacing: "2px",
          }}
        >
          Investment Management
        </motion.div>

        <motion.div
          initial={{ width: 0 }}
          animate={{ width: "200px" }}
          transition={{ duration: 1.5, delay: 2.5 }}
          style={{
            height: "2px",
            background: "linear-gradient(90deg, transparent, white, transparent)",
            margin: "30px auto",
          }}
        />
      </motion.div>
    </div>
  );
};

export default LogoAnimation;