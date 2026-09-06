import Modal from "./ui/Modal";

export default function ConfirmationDialog({
  isOpen,
  onClose,
  onConfirm,
  title,
  description,
  ruleKey,
  currentState,
  newState,
  confirmLabel = "Confirm",
  confirmColor = "bg-[#7BC4BE] hover:bg-[#8AD6CF]",
  loading = false,
}) {
  const handleConfirm = async () => {
    await onConfirm();
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      size="sm"
      footer={
        <div className="flex justify-end gap-3">
          <button
            onClick={onClose}
            disabled={loading}
            className="px-4 py-2 bg-white/10 hover:bg-white/15 text-white border border-white/10 rounded-xl text-xs font-semibold transition-all disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={handleConfirm}
            disabled={loading}
            className={`px-4 py-2 text-[#1A2B2A] rounded-xl text-xs font-bold transition-all disabled:opacity-50 ${confirmColor}`}
          >
            {loading ? "Processing..." : confirmLabel}
          </button>
        </div>
      }
    >
      <div className="space-y-3">
        {ruleKey && (
          <div className="bg-white/5 rounded-xl p-3 border border-white/10">
            <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Rule</p>
            <p className="text-xs font-mono text-white">{ruleKey}</p>
          </div>
        )}
        {currentState && newState && (
          <div className="flex items-center gap-3">
            <div className="flex-1 bg-white/5 rounded-xl p-3 border border-white/10 text-center">
              <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Current</p>
              <span className="text-xs font-bold text-white">{currentState}</span>
            </div>
            <span className="text-gray-500 text-xs">→</span>
            <div className="flex-1 bg-[#7BC4BE]/10 rounded-xl p-3 border border-[#7BC4BE]/20 text-center">
              <p className="text-[10px] text-[#7BC4BE] uppercase tracking-wider mb-1">New</p>
              <span className="text-xs font-bold text-white">{newState}</span>
            </div>
          </div>
        )}
        {description && (
          <p className="text-xs text-gray-400 leading-relaxed">{description}</p>
        )}
      </div>
    </Modal>
  );
}
