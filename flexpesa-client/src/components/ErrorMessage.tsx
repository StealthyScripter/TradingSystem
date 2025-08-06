import React from 'react';
import { AlertTriangle } from 'lucide-react';

const ErrorMessage = ({ message, onRetry }) => {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
      <div className="flex items-center gap-2 mb-2">
        <AlertTriangle className="text-red-600" size={20} />
        <span className="font-medium text-red-800">Error</span>
      </div>
      <p className="text-red-700 text-sm mb-3">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700"
        >
          Retry
        </button>
      )}
    </div>
  );
};

export default ErrorMessage;
