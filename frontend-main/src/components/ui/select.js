import React, { useState } from 'react';

export const Select = ({ value, onValueChange, children, defaultValue, ...props }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedValue, setSelectedValue] = useState(value || defaultValue || '');
  
  const handleClose = () => setIsOpen(false);
  const handleToggle = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsOpen(!isOpen);
  };
  
  const handleSelect = (newValue) => {
    setSelectedValue(newValue);
    if (onValueChange) {
      onValueChange(newValue);
    }
    setIsOpen(false);
  };
  
  // Close dropdown when clicking outside
  React.useEffect(() => {
    const handleClickOutside = (event) => {
      if (isOpen && !event.target.closest('[data-select-root]')) {
        setIsOpen(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen]);
  
  return (
    <div className="relative" data-select-root {...props}>
      {React.Children.map(children, child => {
        if (child.type === SelectTrigger) {
          return React.cloneElement(child, {
            onClick: handleToggle,
            isOpen,
            value: selectedValue
          });
        }
        if (child.type === SelectContent && isOpen) {
          return React.cloneElement(child, {
            onSelect: handleSelect,
            onClose: handleClose,
            currentValue: selectedValue
          });
        }
        return null; // Don't render SelectContent when closed
      })}
    </div>
  );
};

export const SelectTrigger = ({ children, className = '', onClick, isOpen, value, ...props }) => (
  <button
    type="button"
    className={`flex h-10 w-full items-center justify-between rounded-md border border-gray-300 bg-white px-3 py-2 text-sm placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
    onClick={onClick}
    {...props}
  >
    <span className="block truncate text-left">
      {value || children}
    </span>
    <svg
      className={`h-4 w-4 opacity-50 transition-transform ${isOpen ? 'rotate-180' : ''}`}
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
    </svg>
  </button>
);

export const SelectValue = ({ placeholder, className = '', children, ...props }) => (
  <span className={`block truncate ${!children ? 'text-gray-500' : ''} ${className}`} {...props}>
    {children || placeholder}
  </span>
);

export const SelectContent = ({ children, className = '', onSelect, onClose, currentValue, ...props }) => {
  return (
    <div
      data-select-content
      className={`absolute top-full left-0 z-50 min-w-full overflow-hidden rounded-md border border-gray-200 bg-white shadow-lg ${className}`}
      {...props}
    >
      <div className="max-h-60 overflow-auto p-1">
        {React.Children.map(children, child =>
          React.cloneElement(child, { onSelect, currentValue })
        )}
      </div>
    </div>
  );
};

export const SelectItem = ({ children, value, className = '', onSelect, currentValue, ...props }) => {
  const handleClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (onSelect) {
      onSelect(value);
    }
  };
  
  return (
    <div
      className={`relative flex cursor-pointer select-none items-center rounded-sm py-1.5 px-2 text-sm outline-none hover:bg-gray-100 focus:bg-gray-100 ${
        currentValue === value ? 'bg-blue-100 text-blue-900' : ''
      } ${className}`}
      onClick={handleClick}
      {...props}
    >
      {children}
    </div>
  );
};