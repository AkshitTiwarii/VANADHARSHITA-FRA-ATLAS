import React, { useState, useRef, useEffect } from 'react';

export const DropdownMenu = ({ children }) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    const handleEscape = (event) => {
      if (event.key === 'Escape') {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('keydown', handleEscape);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen]);

  return (
    <div className="relative" ref={dropdownRef}>
      {React.Children.map(children, (child) => {
        if (child.type === DropdownMenuTrigger) {
          return React.cloneElement(child, { 
            onClick: () => setIsOpen(!isOpen),
            isOpen 
          });
        }
        if (child.type === DropdownMenuContent) {
          return React.cloneElement(child, { 
            isOpen,
            onClose: () => setIsOpen(false)
          });
        }
        return child;
      })}
    </div>
  );
};

export const DropdownMenuTrigger = ({ children, asChild, onClick, className = '', ...props }) => {
  const handleClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (onClick) onClick(e);
  };

  if (asChild && React.isValidElement(children)) {
    return React.cloneElement(children, {
      ...props,
      className: `${children.props.className || ''} ${className}`,
      onClick: handleClick
    });
  }

  return (
    <button 
      onClick={handleClick} 
      className={`inline-flex items-center justify-center ${className}`}
      {...props}
    >
      {children}
    </button>
  );
};

export const DropdownMenuContent = ({ 
  children, 
  isOpen, 
  onClose, 
  align = 'center', 
  sideOffset = 4, 
  className = '',
  ...props 
}) => {
  if (!isOpen) return null;

  const alignmentClasses = {
    start: 'left-0',
    center: 'left-1/2 transform -translate-x-1/2',
    end: 'right-0'
  };

  return (
    <div 
      className={`
        absolute z-50 min-w-[8rem] overflow-hidden rounded-md border border-slate-200 
        bg-white p-1 text-slate-950 shadow-md animate-in fade-in-0 zoom-in-95
        ${alignmentClasses[align]}
        ${className}
      `}
      style={{ 
        top: `calc(100% + ${sideOffset}px)`,
        minWidth: '200px'
      }}
      {...props}
    >
      {React.Children.map(children, (child) => {
        if (React.isValidElement(child)) {
          return React.cloneElement(child, { onClose });
        }
        return child;
      })}
    </div>
  );
};

export const DropdownMenuItem = ({ 
  children, 
  onClick, 
  onClose,
  className = '', 
  disabled = false,
  ...props 
}) => {
  const handleClick = (e) => {
    if (disabled) return;
    
    if (onClick) {
      onClick(e);
    }
    if (onClose) {
      onClose();
    }
  };

  return (
    <div
      onClick={handleClick}
      className={`
        relative flex cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm 
        outline-none transition-colors
        ${disabled 
          ? 'pointer-events-none opacity-50' 
          : 'hover:bg-slate-100 hover:text-slate-900 focus:bg-slate-100 focus:text-slate-900'
        }
        ${className}
      `}
      {...props}
    >
      {children}
    </div>
  );
};

export const DropdownMenuSeparator = ({ className = '', ...props }) => (
  <div 
    className={`-mx-1 my-1 h-px bg-slate-200 ${className}`} 
    {...props} 
  />
);

export const DropdownMenuLabel = ({ 
  children, 
  inset = false, 
  className = '', 
  ...props 
}) => (
  <div 
    className={`
      px-2 py-1.5 text-sm font-semibold text-slate-900
      ${inset ? 'pl-8' : ''}
      ${className}
    `}
    {...props}
  >
    {children}
  </div>
);