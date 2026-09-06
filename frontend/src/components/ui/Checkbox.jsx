import { forwardRef } from 'react';

const Checkbox = forwardRef(({
  label,
  checked,
  onChange,
  className = '',
  ...props
}, ref) => {
  return (
    <label className={`flex items-center gap-2 cursor-pointer ${className}`}>
      <input
        ref={ref}
        type="checkbox"
        checked={checked}
        onChange={onChange}
        className="sr-only peer"
        {...props}
      />
      <div className="
        w-5 h-5 rounded-md border-2 border-border-strong
        bg-white transition-all duration-150
        peer-checked:bg-primary peer-checked:border-primary
        peer-hover:border-primary
        peer-focus-visible:ring-2 peer-focus-visible:ring-primary/20
        peer-disabled:opacity-50 peer-disabled:cursor-not-allowed
        flex items-center justify-center
      ">
        {checked && (
          <svg className="w-3 h-3 text-white" viewBox="0 0 12 12" fill="none">
            <path
              d="M2 6L5 9L10 3"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        )}
      </div>
      {label && (
        <span className="text-sm text-neutral-700">{label}</span>
      )}
    </label>
  );
});

Checkbox.displayName = 'Checkbox';

export default Checkbox;
