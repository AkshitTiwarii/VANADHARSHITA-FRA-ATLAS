import React from 'react';
import { AlertCircle, XCircle, AlertTriangle, Info, RefreshCw } from 'lucide-react';
import { Button } from './button';

export const ErrorMessage = ({ 
  type = 'error', 
  title, 
  message, 
  onRetry, 
  showIcon = true 
}) => {
  const types = {
    error: {
      bg: 'bg-red-50 border-red-200',
      text: 'text-red-800',
      icon: XCircle,
      iconColor: 'text-red-600'
    },
    warning: {
      bg: 'bg-orange-50 border-orange-200',
      text: 'text-orange-800',
      icon: AlertTriangle,
      iconColor: 'text-orange-600'
    },
    info: {
      bg: 'bg-blue-50 border-blue-200',
      text: 'text-blue-800',
      icon: Info,
      iconColor: 'text-blue-600'
    },
    success: {
      bg: 'bg-green-50 border-green-200',
      text: 'text-green-800',
      icon: AlertCircle,
      iconColor: 'text-green-600'
    }
  };

  const config = types[type];
  const Icon = config.icon;

  return (
    <div className={`p-4 rounded-lg border ${config.bg} ${config.text}`}>
      <div className="flex items-start space-x-3">
        {showIcon && <Icon className={`w-5 h-5 mt-0.5 ${config.iconColor} flex-shrink-0`} />}
        <div className="flex-1">
          {title && <h3 className="font-semibold mb-1">{title}</h3>}
          {message && <p className="text-sm">{message}</p>}
          {onRetry && (
            <Button 
              onClick={onRetry} 
              variant="outline" 
              size="sm" 
              className="mt-3"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Try Again
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

export const EmptyState = ({ 
  icon: Icon, 
  title, 
  message, 
  action, 
  actionLabel 
}) => {
  return (
    <div className="text-center py-12">
      {Icon && <Icon className="w-16 h-16 text-slate-400 mx-auto mb-4" />}
      <h3 className="text-lg font-semibold text-slate-700 mb-2">{title}</h3>
      <p className="text-slate-500 mb-6 max-w-md mx-auto">{message}</p>
      {action && (
        <Button onClick={action}>
          {actionLabel || 'Get Started'}
        </Button>
      )}
    </div>
  );
};
