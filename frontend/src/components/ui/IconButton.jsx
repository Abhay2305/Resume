const IconButton = ({
  icon: Icon,
  size = 'md',
  variant = 'ghost',
  className = '',
  ...props
}) => {
  const sizes = {
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-12 h-12',
  };

  const variants = {
    ghost: 'text-neutral-500 hover:text-neutral-700 hover:bg-surface',
    primary: 'text-primary bg-primary/10 hover:bg-primary/20',
    danger: 'text-error bg-error/10 hover:bg-error/20',
  };

  return (
    <button
      className={`
        inline-flex items-center justify-center
        rounded-lg transition-all duration-150
        ${sizes[size]}
        ${variants[variant]}
        ${className}
      `}
      {...props}
    >
      <Icon size={size === 'sm' ? 14 : size === 'lg' ? 20 : 16} />
    </button>
  );
};

export default IconButton;
