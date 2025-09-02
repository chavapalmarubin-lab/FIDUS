import React, { useState, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "./ui/button";
import { 
  Camera, 
  CameraOff, 
  RotateCcw, 
  Check, 
  X,
  AlertCircle,
  Loader2
} from "lucide-react";

const CameraCapture = ({ onCapture, onClose, isOpen }) => {
  const [stream, setStream] = useState(null);
  const [capturedImage, setCapturedImage] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [cameraActive, setCameraActive] = useState(false);
  const [permissionState, setPermissionState] = useState("unknown");
  
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  // Check camera permission status
  const checkPermissions = useCallback(async () => {
    try {
      if (navigator.permissions && navigator.permissions.query) {
        const result = await navigator.permissions.query({ name: 'camera' });
        setPermissionState(result.state);
        
        result.addEventListener('change', () => {
          setPermissionState(result.state);
        });
      }
    } catch (err) {
      console.log("Permission API not supported");
      setPermissionState("unknown");
    }
  }, []);

  // Initialize permission checking when modal opens
  React.useEffect(() => {
    if (isOpen) {
      checkPermissions();
    }
  }, [isOpen, checkPermissions]);

  const startCamera = useCallback(async () => {
    try {
      setIsLoading(true);
      setError("");
      
      // Check if navigator.mediaDevices is available
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error("Camera not supported in this browser");
      }
      
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { 
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'environment' // Use back camera on mobile
        },
        audio: false
      });
      
      setStream(mediaStream);
      setCameraActive(true);
      
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
    } catch (err) {
      console.error("Error accessing camera:", err);
      
      let errorMessage = "Unable to access camera. ";
      
      if (err.name === 'NotAllowedError') {
        errorMessage = "Camera access denied. Please allow camera permissions in your browser settings and try again.";
      } else if (err.name === 'NotFoundError') {
        errorMessage = "No camera found on this device.";
      } else if (err.name === 'NotSupportedError') {
        errorMessage = "Camera not supported in this browser.";
      } else if (err.name === 'NotReadableError') {
        errorMessage = "Camera is being used by another application.";
      } else if (err.name === 'OverconstrainedError') {
        errorMessage = "Camera doesn't meet the required specifications.";
      } else if (err.message === "Camera not supported in this browser") {
        errorMessage = err.message;
      } else {
        errorMessage += "Please check your browser permissions and ensure you're using HTTPS.";
      }
      
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const stopCamera = useCallback(() => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
      setCameraActive(false);
    }
  }, [stream]);

  const capturePhoto = useCallback(() => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');

    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw the video frame to canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert to blob
    canvas.toBlob((blob) => {
      if (blob) {
        const imageUrl = URL.createObjectURL(blob);
        setCapturedImage({
          blob,
          url: imageUrl,
          timestamp: new Date().toISOString()
        });
        stopCamera();
      }
    }, 'image/jpeg', 0.8);
  }, [stopCamera]);

  const retakePhoto = useCallback(() => {
    if (capturedImage) {
      URL.revokeObjectURL(capturedImage.url);
      setCapturedImage(null);
    }
    startCamera();
  }, [capturedImage, startCamera]);

  const confirmCapture = useCallback(() => {
    if (capturedImage && onCapture) {
      // Create a File object from the blob
      const file = new File([capturedImage.blob], `document-${Date.now()}.jpg`, {
        type: 'image/jpeg',
        lastModified: Date.now()
      });
      
      onCapture(file);
      handleClose();
    }
  }, [capturedImage, onCapture]);

  const handleClose = useCallback(() => {
    stopCamera();
    if (capturedImage) {
      URL.revokeObjectURL(capturedImage.url);
      setCapturedImage(null);
    }
    setError("");
    if (onClose) onClose();
  }, [stopCamera, capturedImage, onClose]);

  // Start camera when modal opens
  React.useEffect(() => {
    if (isOpen && !cameraActive && !capturedImage) {
      startCamera();
    }
    
    // Cleanup on unmount
    return () => {
      stopCamera();
      if (capturedImage) {
        URL.revokeObjectURL(capturedImage.url);
      }
    };
  }, [isOpen, cameraActive, capturedImage, startCamera, stopCamera]);

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/90 flex items-center justify-center z-50"
        onClick={handleClose}
      >
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.8, opacity: 0 }}
          className="bg-slate-800 rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-hidden"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold text-white">
              {cameraActive ? "Take Photo" : capturedImage ? "Review Photo" : "Camera Access"}
            </h3>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={handleClose}
              className="text-slate-400 hover:text-white"
            >
              <X size={20} />
            </Button>
          </div>

          {/* Error Display */}
          {error && (
            <div className="mb-4 p-4 bg-red-900/20 border border-red-500/50 rounded-lg">
              <div className="flex items-start gap-3">
                <AlertCircle className="text-red-400 flex-shrink-0 mt-0.5" size={20} />
                <div>
                  <span className="text-red-300 font-medium">Camera Access Issue</span>
                  <p className="text-red-300 text-sm mt-1">{error}</p>
                  
                  {/* Permission help for common errors */}
                  {error.includes("denied") && (
                    <div className="mt-3 p-3 bg-blue-900/20 border border-blue-500/30 rounded text-xs text-blue-300">
                      <strong>How to enable camera:</strong>
                      <ul className="mt-1 space-y-1 list-disc list-inside">
                        <li><strong>Desktop:</strong> Click the camera icon in your browser's address bar</li>
                        <li><strong>Mobile:</strong> Check browser settings → Site permissions → Camera</li>
                        <li><strong>Safari:</strong> Settings → Safari → Camera → Allow</li>
                        <li><strong>Chrome:</strong> Settings → Privacy → Site Settings → Camera</li>
                      </ul>
                    </div>
                  )}
                  
                  {error.includes("HTTPS") && (
                    <div className="mt-3 p-3 bg-yellow-900/20 border border-yellow-500/30 rounded text-xs text-yellow-300">
                      <strong>Security Note:</strong> Camera access requires a secure connection (HTTPS). 
                      Make sure you're accessing the site with HTTPS://
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Camera/Image Display Area */}
          <div className="relative bg-black rounded-lg overflow-hidden mb-4" style={{ aspectRatio: '16/9' }}>
            {/* Loading State */}
            {isLoading && (
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <Loader2 className="animate-spin text-cyan-400 mx-auto mb-2" size={32} />
                  <p className="text-white">Starting camera...</p>
                </div>
              </div>
            )}

            {/* Video Stream */}
            {cameraActive && (
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-full object-cover"
              />
            )}

            {/* Captured Image */}
            {capturedImage && (
              <img
                src={capturedImage.url}
                alt="Captured document"
                className="w-full h-full object-cover"
              />
            )}

            {/* Camera Overlay */}
            {cameraActive && (
              <div className="absolute inset-0 pointer-events-none">
                {/* Corner guidelines */}
                <div className="absolute top-4 left-4 w-8 h-8 border-t-2 border-l-2 border-cyan-400"></div>
                <div className="absolute top-4 right-4 w-8 h-8 border-t-2 border-r-2 border-cyan-400"></div>
                <div className="absolute bottom-4 left-4 w-8 h-8 border-b-2 border-l-2 border-cyan-400"></div>
                <div className="absolute bottom-4 right-4 w-8 h-8 border-b-2 border-r-2 border-cyan-400"></div>
                
                {/* Center guideline */}
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="border border-cyan-400/50 rounded-lg" style={{ width: '60%', height: '40%' }}></div>
                </div>
              </div>
            )}
          </div>

          {/* Hidden canvas for image processing */}
          <canvas ref={canvasRef} className="hidden" />

          {/* Control Buttons */}
          <div className="flex gap-3">
            {/* Camera not started or error state */}
            {!cameraActive && !capturedImage && !isLoading && (
              <>
                <Button
                  onClick={startCamera}
                  className="flex-1 bg-cyan-600 hover:bg-cyan-700"
                  disabled={isLoading}
                >
                  <Camera size={16} className="mr-2" />
                  Start Camera
                </Button>
                <Button
                  variant="outline"
                  onClick={handleClose}
                  className="border-slate-600 text-slate-300"
                >
                  Cancel
                </Button>
              </>
            )}

            {/* Camera active - capture controls */}
            {cameraActive && (
              <>
                <Button
                  onClick={capturePhoto}
                  className="flex-1 bg-cyan-600 hover:bg-cyan-700"
                >
                  <Camera size={16} className="mr-2" />
                  Capture Photo
                </Button>
                <Button
                  variant="outline"
                  onClick={stopCamera}
                  className="border-slate-600 text-slate-300"
                >
                  <CameraOff size={16} className="mr-2" />
                  Stop Camera
                </Button>
              </>
            )}

            {/* Photo captured - review controls */}
            {capturedImage && (
              <>
                <Button
                  onClick={confirmCapture}
                  className="flex-1 bg-green-600 hover:bg-green-700"
                >
                  <Check size={16} className="mr-2" />
                  Use Photo
                </Button>
                <Button
                  onClick={retakePhoto}
                  variant="outline"
                  className="border-slate-600 text-slate-300"
                >
                  <RotateCcw size={16} className="mr-2" />
                  Retake
                </Button>
                <Button
                  variant="outline"
                  onClick={handleClose}
                  className="border-slate-600 text-slate-300"
                >
                  Cancel
                </Button>
              </>
            )}
          </div>

          {/* Instructions */}
          <div className="mt-4 text-sm text-slate-400">
            {cameraActive && (
              <div className="text-center">
                📸 Position the document within the guidelines and click capture
              </div>
            )}
            {capturedImage && (
              <div className="text-center">
                👀 Review your photo and confirm to use it or retake if needed
              </div>
            )}
            {!cameraActive && !capturedImage && !isLoading && (
              <div className="space-y-2">
                <div className="text-center">
                  🎥 Your browser will ask for camera permission when you click "Start Camera"
                </div>
                <div className="text-xs text-slate-500 text-center">
                  Make sure to click "Allow" when prompted. Camera access is required to take photos of your documents.
                </div>
              </div>
            )}
            {isLoading && (
              <div className="text-center">
                ⏳ Requesting camera access... Please allow when prompted by your browser
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default CameraCapture;