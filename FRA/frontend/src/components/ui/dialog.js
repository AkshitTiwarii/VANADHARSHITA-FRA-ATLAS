import React, { useEffect } from 'react';

export const Dialog = ({ open, onOpenChange, children, ...props }) => {
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === 'Escape' && open) {
        onOpenChange(false);
      }
    };
    
    if (open) {
      document.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
    }
    
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'unset';
    };
  }, [open, onOpenChange]);

  if (!open) return null;
  
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" {...props}>
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm"
        onClick={() => onOpenChange(false)}
      />
      <div className="relative bg-white rounded-lg shadow-lg max-w-6xl w-full mx-4 max-h-[95vh] overflow-y-auto">
        {children}
      </div>
    </div>
  );
};

export const DialogTrigger = ({ children, asChild, onClick, ...props }) => {
  if (asChild && React.isValidElement(children)) {
    return React.cloneElement(children, {
      ...props,
      onClick: (e) => {
        if (onClick) onClick(e);
        if (children.props.onClick) children.props.onClick(e);
      }
    });
  }
  return (
    <button onClick={onClick} {...props}>
      {children}
    </button>
  );
};

export const DialogContent = ({ children, className = '', ...props }) => (
  <div className={`p-6 ${className}`} {...props}>
    {children}
  </div>
);

export const DialogHeader = ({ children, className = '', ...props }) => (
  <div className={`mb-4 ${className}`} {...props}>
    {children}
  </div>
);

export const DialogTitle = ({ children, className = '', ...props }) => (
  <h2 className={`text-lg font-semibold leading-none tracking-tight ${className}`} {...props}>
    {children}
  </h2>
);

export const DialogDescription = ({ children, className = '', ...props }) => (
  <p className={`text-sm text-gray-600 mt-1 ${className}`} {...props}>
    {children}
  </p>
);

export const DialogFooter = ({ children, className = '', ...props }) => (
  <div className={`flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2 gap-2 mt-6 ${className}`} {...props}>
    {children}
  </div>
);