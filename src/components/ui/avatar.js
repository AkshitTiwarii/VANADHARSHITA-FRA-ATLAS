import React from 'react';

export const Avatar = ({ children, className = '', ...props }) => {
  return (
    <div
      className={`
        relative flex h-10 w-10 shrink-0 overflow-hidden rounded-full
        ${className}
      `}
      {...props}
    >
      {children}
    </div>
  );
};

export const AvatarImage = ({ 
  src, 
  alt, 
  className = '',
  onLoad,
  onError,
  ...props 
}) => {
  const [loaded, setLoaded] = React.useState(false);
  const [error, setError] = React.useState(false);

  const handleLoad = (e) => {
    setLoaded(true);
    if (onLoad) onLoad(e);
  };

  const handleError = (e) => {
    setError(true);
    if (onError) onError(e);
  };

  if (error) return null;

  return (
    <img
      src={src}
      alt={alt}
      onLoad={handleLoad}
      onError={handleError}
      className={`
        aspect-square h-full w-full object-cover
        ${loaded ? 'opacity-100' : 'opacity-0'}
        ${className}
      `}
      {...props}
    />
  );
};

export const AvatarFallback = ({ 
  children, 
  className = '', 
  delayMs = 600,
  ...props 
}) => {
  const [canRender, setCanRender] = React.useState(delayMs === 0);

  React.useEffect(() => {
    if (delayMs > 0) {
      const timer = setTimeout(() => {
        setCanRender(true);
      }, delayMs);

      return () => clearTimeout(timer);
    }
  }, [delayMs]);

  if (!canRender) return null;

  return (
    <div
      className={`
        flex h-full w-full items-center justify-center rounded-full
        bg-slate-100 text-slate-600 font-medium text-sm
        ${className}
      `}
      {...props}
    >
      {children}
    </div>
  );
};