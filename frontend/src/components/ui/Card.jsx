const Card = ({
  children,
  className = '',
  hover = false,
  interactive = false,
  padding = 'md',
  ...props
}) => {
  const paddings = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  return (
    <div
      className={`
        bg-white border border-border rounded-2xl
        ${hover ? 'transition-all duration-250 hover:border-primary hover:shadow-md hover:-translate-y-0.5' : ''}
        ${interactive ? 'cursor-pointer transition-all duration-250 hover:border-primary hover:shadow-lg' : ''}
        ${paddings[padding]}
        ${className}
      `}
      {...props}
    >
      {children}
    </div>
  );
};

export const CardHeader = ({ children, className = '' }) => (
  <div className={`mb-4 ${className}`}>
    {children}
  </div>
);

export const CardTitle = ({ children, className = '' }) => (
  <h3 className={`text-lg font-semibold text-neutral-800 ${className}`}>
    {children}
  </h3>
);

export const CardDescription = ({ children, className = '' }) => (
  <p className={`text-sm text-neutral-500 mt-1 ${className}`}>
    {children}
  </p>
);

export const CardContent = ({ children, className = '' }) => (
  <div className={className}>
    {children}
  </div>
);

export const CardFooter = ({ children, className = '' }) => (
  <div className={`flex items-center gap-2 mt-4 pt-4 border-t border-border ${className}`}>
    {children}
  </div>
);

export default Card;
