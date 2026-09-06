const Divider = ({
  orientation = 'horizontal',
  className = '',
  ...props
}) => {
  if (orientation === 'vertical') {
    return (
      <div
        className={`w-px h-full bg-border ${className}`}
        {...props}
      />
    );
  }

  return (
    <div
      className={`w-full h-px bg-border ${className}`}
      {...props}
    />
  );
};

export default Divider;
