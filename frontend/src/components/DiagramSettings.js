import React, { useState } from 'react';

/**
 * DiagramSettings - Settings modal for diagram customization
 * Allows users to configure layout, animations, and display options
 */
export default function DiagramSettings({ isOpen, onClose, onSave }) {
  const [settings, setSettings] = useState(() => {
    const saved = localStorage.getItem('fidus_diagram_settings');
    return saved ? JSON.parse(saved) : {
      layout: 'horizontal',
      showMiniMap: true,
      showLabels: true,
      showGrid: true,
      animationSpeed: 'normal',
      enableNodeAnimations: true,
      enableFlowAnimation: true,
      savePositions: true,
      saveZoom: true,
      autoRefresh: true,
      nodeSpacing: 150,
      connectionCurve: 0.5
    };
  });

  const saveSettings = () => {
    localStorage.setItem('fidus_diagram_settings', JSON.stringify(settings));
    onSave?.(settings);
    onClose();
  };

  const resetSettings = () => {
    const defaults = {
      layout: 'horizontal',
      showMiniMap: true,
      showLabels: true,
      showGrid: true,
      animationSpeed: 'normal',
      enableNodeAnimations: true,
      enableFlowAnimation: true,
      savePositions: true,
      saveZoom: true,
      autoRefresh: true,
      nodeSpacing: 150,
      connectionCurve: 0.5
    };
    setSettings(defaults);
    localStorage.setItem('fidus_diagram_settings', JSON.stringify(defaults));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 animate-fade-in">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto animate-scale-in">
        {/* Header */}
        <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-blue-500 text-white p-4 flex items-center justify-between rounded-t-xl">
          <div className="flex items-center gap-2">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <h2 className="text-xl font-bold">Diagram Settings</h2>
          </div>
          <button 
            onClick={onClose} 
            className="hover:bg-white/20 p-1 rounded transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Layout Section */}
          <section>
            <h3 className="font-bold text-lg mb-3 text-gray-900">Layout & View</h3>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium mb-2 text-gray-700">Layout Type</label>
                <div className="flex gap-2">
                  {['horizontal', 'vertical', 'radial'].map(type => (
                    <button
                      key={type}
                      onClick={() => setSettings({...settings, layout: type})}
                      className={`px-4 py-2 rounded-lg capitalize transition-colors ${
                        settings.layout === type
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {type}
                    </button>
                  ))}
                </div>
              </div>

              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.showMiniMap}
                  onChange={(e) => setSettings({...settings, showMiniMap: e.target.checked})}
                  className="w-4 h-4 text-blue-600 rounded"
                />
                <span className="text-gray-700">Show mini-map</span>
              </label>

              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.showLabels}
                  onChange={(e) => setSettings({...settings, showLabels: e.target.checked})}
                  className="w-4 h-4 text-blue-600 rounded"
                />
                <span className="text-gray-700">Show connection labels</span>
              </label>

              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.showGrid}
                  onChange={(e) => setSettings({...settings, showGrid: e.target.checked})}
                  className="w-4 h-4 text-blue-600 rounded"
                />
                <span className="text-gray-700">Show grid background</span>
              </label>
            </div>
          </section>

          {/* Animation Section */}
          <section className="border-t border-gray-200 pt-6">
            <h3 className="font-bold text-lg mb-3 text-gray-900">Animation Settings</h3>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium mb-2 text-gray-700">Animation Speed</label>
                <div className="flex gap-2">
                  {['slow', 'normal', 'fast', 'off'].map(speed => (
                    <button
                      key={speed}
                      onClick={() => setSettings({...settings, animationSpeed: speed})}
                      className={`px-4 py-2 rounded-lg capitalize transition-colors ${
                        settings.animationSpeed === speed
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {speed}
                    </button>
                  ))}
                </div>
              </div>

              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.enableNodeAnimations}
                  onChange={(e) => setSettings({...settings, enableNodeAnimations: e.target.checked})}
                  className="w-4 h-4 text-blue-600 rounded"
                />
                <span className="text-gray-700">Enable node animations</span>
              </label>

              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.enableFlowAnimation}
                  onChange={(e) => setSettings({...settings, enableFlowAnimation: e.target.checked})}
                  className="w-4 h-4 text-blue-600 rounded"
                />
                <span className="text-gray-700">Enable connection flow animation</span>
              </label>
            </div>
          </section>

          {/* Auto-Save Section */}
          <section className="border-t border-gray-200 pt-6">
            <h3 className="font-bold text-lg mb-3 text-gray-900">Auto-Save</h3>
            <div className="space-y-3">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.savePositions}
                  onChange={(e) => setSettings({...settings, savePositions: e.target.checked})}
                  className="w-4 h-4 text-blue-600 rounded"
                />
                <span className="text-gray-700">Save node positions</span>
              </label>

              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.saveZoom}
                  onChange={(e) => setSettings({...settings, saveZoom: e.target.checked})}
                  className="w-4 h-4 text-blue-600 rounded"
                />
                <span className="text-gray-700">Save zoom level</span>
              </label>

              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.autoRefresh}
                  onChange={(e) => setSettings({...settings, autoRefresh: e.target.checked})}
                  className="w-4 h-4 text-blue-600 rounded"
                />
                <span className="text-gray-700">Auto-refresh every 30 seconds</span>
              </label>
            </div>
          </section>

          {/* Advanced Section */}
          <section className="border-t border-gray-200 pt-6">
            <h3 className="font-bold text-lg mb-3 text-gray-900">Advanced</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2 text-gray-700">
                  Node Spacing: {settings.nodeSpacing}px
                </label>
                <input
                  type="range"
                  min="100"
                  max="300"
                  value={settings.nodeSpacing}
                  onChange={(e) => setSettings({...settings, nodeSpacing: parseInt(e.target.value)})}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2 text-gray-700">
                  Connection Curve: {settings.connectionCurve.toFixed(1)}
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={settings.connectionCurve}
                  onChange={(e) => setSettings({...settings, connectionCurve: parseFloat(e.target.value)})}
                  className="w-full"
                />
              </div>
            </div>
          </section>
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-gray-50 p-4 flex justify-between rounded-b-xl border-t border-gray-200">
          <button
            onClick={resetSettings}
            className="px-4 py-2 text-gray-700 hover:bg-gray-200 rounded-lg transition-colors font-medium"
          >
            Reset to Defaults
          </button>
          <button
            onClick={saveSettings}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Save Settings
          </button>
        </div>
      </div>
    </div>
  );
}
