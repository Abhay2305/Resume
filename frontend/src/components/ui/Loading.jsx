const LoadingSpinner = ({ size = 'md', className = '' }) => {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12',
  };

  return (
    <div className={`loading-spinner ${sizes[size]} ${className}`} />
  );
};

export const LoadingDots = ({ className = '' }) => (
  <div className={`loading-dots ${className}`}>
    <div className="loading-dot" />
    <div className="loading-dot" />
    <div className="loading-dot" />
  </div>
);

export const LoadingPage = ({ message = 'Loading...' }) => (
  <div className="min-h-screen bg-white flex flex-col items-center justify-center gap-4">
    <LoadingSpinner size="lg" />
    <p className="text-neutral-500 text-sm">{message}</p>
  </div>
);

export const Skeleton = ({ className = '', ...props }) => (
  <div className={`skeleton ${className}`} {...props} />
);

export default LoadingSpinner;
