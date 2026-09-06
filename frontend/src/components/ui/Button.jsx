import { forwardRef } from 'react';

const variants = {
  primary: 'bg-primary text-white shadow-primary hover:bg-primary-dark hover:shadow-primary hover:-translate-y-0.5 active:translate-y-0',
  secondary: 'bg-white text-neutral-700 border border-border-strong hover:border-primary hover:text-primary-deep',
  ghost: 'bg-transparent text-neutral-600 hover:bg-surface hover:text-neutral-800',
  danger: 'bg-error text-white hover:bg-red-600 hover:-translate-y-0.5',
};

const sizes = {
  sm: 'px-3 py-1.5 text-xs rounded-md',
  md: 'px-4 py-2.5 text-sm rounded-lg',
  lg: 'px-5 py-3 text-base rounded-xl',
  xl: 'px-6 py-4 text-lg rounded-xl',
};

const Button = forwardRef(({
  variant = 'primary',
  size = 'md',
  className = '',
  disabled = false,
  loading = false,
  children,
  ...props
}, ref) => {
  const baseStyles = 'inline-flex items-center justify-center gap-2 font-medium transition-all duration-200 ease-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed font-[\'DM_Sans\',sans-serif]';
  
  return (
    <button
      ref={ref}
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
      )}
      {children}
    </button>
  );
});

Button.displayName = 'Button';

export default Button;
