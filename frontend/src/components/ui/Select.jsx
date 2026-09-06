import { forwardRef } from 'react';

const Select = forwardRef(({
  label,
  error,
  helperText,
  options = [],
  placeholder = 'Select an option',
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
      <select
        ref={ref}
        className={`
          w-full px-3.5 py-2.5 text-sm
          bg-white border border-border-strong rounded-lg
          text-neutral-800
          transition-all duration-150
          hover:border-primary
          focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/15
          disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-surface
          appearance-none bg-no-repeat bg-[right_0.75rem_center] bg-[length:1rem]
          ${error ? 'border-error focus:border-error focus:ring-error/15' : ''}
          ${className}
        `}
        style={{
          backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%2394a3b8' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
        }}
        {...props}
      >
        {placeholder && (
          <option value="" disabled>
            {placeholder}
          </option>
        )}
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {(error || helperText) && (
        <p className={`text-xs ${error ? 'text-error' : 'text-neutral-500'}`}>
          {error || helperText}
        </p>
      )}
    </div>
  );
});

Select.displayName = 'Select';

export default Select;
