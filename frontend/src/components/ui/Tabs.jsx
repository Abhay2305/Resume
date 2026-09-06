const Tabs = ({
  tabs,
  activeTab,
  onChange,
  className = '',
}) => {
  return (
    <div className={`flex gap-1 p-1 bg-surface rounded-xl ${className}`}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          className={`
            flex items-center gap-2 px-4 py-2 text-sm font-medium
            rounded-lg transition-all duration-200
            ${activeTab === tab.id
              ? 'bg-white text-primary-deep shadow-sm'
              : 'text-neutral-500 hover:text-neutral-700 hover:bg-white/50'
            }
          `}
        >
          {tab.icon && <tab.icon size={16} />}
          {tab.label}
        </button>
      ))}
    </div>
  );
};

export default Tabs;
