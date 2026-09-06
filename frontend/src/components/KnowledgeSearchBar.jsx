import { useState, useCallback } from "react";
import { Search, X } from "lucide-react";

export default function KnowledgeSearchBar({ onSearch, placeholder = "Search rules..." }) {
  const [value, setValue] = useState("");

  const handleSubmit = useCallback(
    (e) => {
      e.preventDefault();
      onSearch(value.trim());
    },
    [value, onSearch]
  );

  const handleClear = useCallback(() => {
    setValue("");
    onSearch("");
  }, [onSearch]);

  return (
    <form onSubmit={handleSubmit} className="relative">
      <Search
        size={16}
        className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500"
      />
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder={placeholder}
        className="w-full bg-white/5 border border-white/10 rounded-xl py-2.5 pl-10 pr-10 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-[#7BC4BE] transition-colors"
      />
      {value && (
        <button
          type="button"
          onClick={handleClear}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white transition-colors"
        >
          <X size={14} />
        </button>
      )}
    </form>
  );
}
