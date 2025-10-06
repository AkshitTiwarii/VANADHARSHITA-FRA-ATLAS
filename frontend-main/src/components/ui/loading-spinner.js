import React from 'react';
import { TreePine, Activity, Loader2 } from 'lucide-react';

export const LoadingSpinner = ({ size = 'md', message = 'Loading...', submessage = '' }) => {
  const sizes = {
    sm: 'h-8 w-8',
    md: 'h-16 w-16',
    lg: 'h-24 w-24'
  };

  const iconSizes = {
    sm: 'w-3 h-3',
    md: 'w-6 h-6',
    lg: 'w-10 h-10'
  };

  return (
    <div className="flex items-center justify-center min-h-96">
      <div className="text-center">
        <div className="relative">
          <div className={`animate-spin rounded-full ${sizes[size]} border-4 border-blue-200 border-t-blue-900 mx-auto`}></div>
          <TreePine className={`${iconSizes[size]} text-blue-900 absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2`} />
        </div>
        {message && (
          <>
            <p className="mt-4 text-lg font-medium text-slate-700">{message}</p>
            {submessage && <p className="text-sm text-slate-500 mt-1">{submessage}</p>}
          </>
        )}
      </div>
    </div>
  );
};

export const InlineLoader = ({ text = 'Processing...' }) => {
  return (
    <div className="flex items-center justify-center space-x-2 text-blue-600">
      <Loader2 className="w-4 h-4 animate-spin" />
      <span className="text-sm font-medium">{text}</span>
    </div>
  );
};

export const CardLoader = () => {
  return (
    <div className="animate-pulse space-y-4">
      <div className="h-4 bg-slate-200 rounded w-3/4"></div>
      <div className="h-4 bg-slate-200 rounded w-1/2"></div>
      <div className="h-4 bg-slate-200 rounded w-5/6"></div>
    </div>
  );
};
