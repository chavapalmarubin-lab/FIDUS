import React from 'react';
import { Loader2, PlayCircle, CheckCircle, AlertCircle } from 'lucide-react';

const ActionCard = ({ 
  icon, 
  title, 
  description, 
  loading, 
  onClick, 
  badge,
  success,
  error,
  result 
}) => {
  // Get action status styling
  const getStatusStyle = () => {
    if (loading) {
      return {
        border: 'border-blue-300',
        bg: 'bg-blue-50'
      };
    }
    if (success) {
      return {
        border: 'border-green-300',
        bg: 'bg-green-50'
      };
    }
    if (error) {
      return {
        border: 'border-red-300',
        bg: 'bg-red-50'
      };
    }
    return {
      border: 'border-gray-200',
      bg: 'bg-white'
    };
  };

  const statusStyle = getStatusStyle();

  return (
    <div className={`${statusStyle.bg} border-2 ${statusStyle.border} rounded-lg p-5 card-hover-effect animate-fadeIn`}>
      {/* Icon and Badge */}
      <div className="flex items-start justify-between mb-4">
        <span className="text-4xl">{icon}</span>
        {badge && (
          <span className="bg-red-100 text-red-600 text-xs font-semibold px-2 py-1 rounded-full">
            {badge}
          </span>
        )}
        {loading && (
          <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
        )}
        {success && (
          <CheckCircle className="w-5 h-5 text-green-600" />
        )}
        {error && (
          <AlertCircle className="w-5 h-5 text-red-600" />
        )}
      </div>

      {/* Title */}
      <h4 className="font-bold text-lg text-gray-900 mb-2">{title}</h4>

      {/* Description */}
      <p className="text-sm text-gray-600 mb-4 min-h-[40px]">{description}</p>

      {/* Result/Error Message */}
      {result && (
        <div className="mb-4 p-3 bg-white border border-gray-200 rounded-md">
          <p className="text-xs text-gray-700">{result}</p>
        </div>
      )}

      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-200 rounded-md">
          <p className="text-xs text-red-700 font-medium">{error}</p>
        </div>
      )}

      {/* Execute Button */}
      <button
        onClick={onClick}
        disabled={loading}
        className={`w-full py-3 rounded-lg font-medium transition-all duration-200 flex items-center justify-center space-x-2 ${
          loading
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
            : success
            ? 'bg-green-600 text-white hover:bg-green-700'
            : error
            ? 'bg-red-600 text-white hover:bg-red-700'
            : 'bg-blue-600 text-white hover:bg-blue-700 hover:shadow-md'
        }`}
      >
        {loading ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            <span className="text-sm">Processing...</span>
          </>
        ) : (
          <>
            <PlayCircle className="w-4 h-4" />
            <span className="text-sm">Execute</span>
          </>
        )}
      </button>
    </div>
  );
};

export default ActionCard;
