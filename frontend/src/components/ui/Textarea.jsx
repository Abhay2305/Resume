import { forwardRef } from 'react';

const Textarea = forwardRef(({
  label,
  error,
  helperText,
  rows = 4,
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
      <textarea
        ref={ref}
        rows={rows}
        className={`
          w-full px-3.5 py-2.5 text-sm
          bg-white border border-border-strong rounded-lg
          text-neutral-800 placeholder-neutral-400
          transition-all duration-150
          hover:border-primary
          focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/15
          disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-surface
          resize-vertical min-h-[100px]
          ${error ? 'border-error focus:border-error focus:ring-error/15' : ''}
          ${className}
        `}
        {...props}
      />
      {(error || helperText) && (
        <p className={`text-xs ${error ? 'text-error' : 'text-neutral-500'}`}>
          {error || helperText}
        </p>
      )}
    </div>
  );
});

Textarea.displayName = 'Textarea';

export default Textarea;
