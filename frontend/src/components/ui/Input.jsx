import { forwardRef } from 'react';

const Input = forwardRef(({
  label,
  error,
  helperText,
  icon: Icon,
  className = '',
  containerClassName = '',
  ...props
}, ref) => {
  return (
    <div className={`flex flex-col gap-1.5 ${containerClassName}`}>
      {label && (
        <label className="text-xs font-semibold uppercase tracking-wider text-neutral-500">
          {label}
        </label>
      )}
      <div className="relative">
        {Icon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400">
            <Icon size={16} />
          </div>
        )}
        <input
          ref={ref}
          className={`
            w-full px-3.5 py-2.5 text-sm
            bg-white border border-border-strong rounded-lg
            text-neutral-800 placeholder-neutral-400
            transition-all duration-150
            hover:border-primary
            focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/15
            disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-surface
            ${Icon ? 'pl-10' : ''}
            ${error ? 'border-error focus:border-error focus:ring-error/15' : ''}
            ${className}
          `}
          {...props}
        />
      </div>
      {(error || helperText) && (
        <p className={`text-xs ${error ? 'text-error' : 'text-neutral-500'}`}>
          {error || helperText}
        </p>
      )}
    </div>
  );
});

Input.displayName = 'Input';

export default Input;
