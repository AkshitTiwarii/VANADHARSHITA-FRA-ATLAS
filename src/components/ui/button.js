import React from 'react';

export const Button = ({ children, className = '', variant = 'default', size = 'default', disabled = false, ...props }) => {
  const variants = {
    default: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
    secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500',
    outline: 'border border-gray-300 bg-white text-gray-900 hover:bg-gray-50 focus:ring-blue-500',
    destructive: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
    ghost: 'text-gray-900 hover:bg-gray-100 focus:ring-gray-500'
  };
  
  const sizes = {
    default: 'px-4 py-2 text-sm h-10',
    sm: 'px-3 py-1 text-xs h-8',
    lg: 'px-6 py-3 text-base h-12',
    icon: 'h-10 w-10'
  };
  
  return (
    <button
      className={`inline-flex items-center justify-center rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
};