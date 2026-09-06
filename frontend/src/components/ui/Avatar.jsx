const Avatar = ({
  src,
  alt,
  name,
  size = 'md',
  className = '',
  ...props
}) => {
  const sizes = {
    sm: 'w-8 h-8 text-xs',
    md: 'w-10 h-10 text-sm',
    lg: 'w-12 h-12 text-base',
    xl: 'w-16 h-16 text-lg',
  };

  const getInitials = (name) => {
    if (!name) return '?';
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  if (src) {
    return (
      <img
        src={src}
        alt={alt || name}
        className={`rounded-full object-cover ${sizes[size]} ${className}`}
        {...props}
      />
    );
  }

  return (
    <div
      className={`
        rounded-full bg-primary flex items-center justify-center
        text-white font-semibold
        ${sizes[size]}
        ${className}
      `}
      {...props}
    >
      {getInitials(name)}
    </div>
  );
};

export default Avatar;
