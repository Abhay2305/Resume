import { X } from 'lucide-react';

const Alert = ({
  variant = 'info',
  title,
  children,
  onClose,
  className = '',
}) => {
  const variants = {
    info: 'bg-secondary-light border-secondary text-neutral-700',
    success: 'bg-success-light border-success text-green-700',
    warning: 'bg-warning-light border-warning text-amber-700',
    error: 'bg-error-light border-error text-red-700',
  };

  return (
    <div
      className={`
        flex items-start gap-3 p-4 rounded-xl border
        ${variants[variant]}
        ${className}
      `}
    >
      <div className="flex-1">
        {title && (
          <h4 className="font-semibold text-sm mb-1">{title}</h4>
        )}
        <p className="text-sm">{children}</p>
      </div>
      {onClose && (
        <button
          onClick={onClose}
          className="shrink-0 p-1 rounded-lg hover:bg-black/5 transition-colors"
        >
          <X size={16} />
        </button>
      )}
    </div>
  );
};

export default Alert;
