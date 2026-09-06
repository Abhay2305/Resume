import { GraduationCap } from "lucide-react";

export default function EducationCard({ knowledge, parsedData }) {
  const entries =
    knowledge?.education_summary || parsedData?.education_entries || [];

  if (!entries || entries.length === 0) return null;

  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 rounded-xl bg-[#7BC4BE]/15 flex items-center justify-center">
          <GraduationCap size={20} className="text-[#7BC4BE]" />
        </div>
        <div>
          <h3 className="text-sm font-bold text-white">Education</h3>
          <p className="text-[11px] text-gray-500 mt-0.5">
            {entries.length} entries
          </p>
        </div>
      </div>

      <div className="space-y-3">
        {entries.map((entry, i) => {
          const degree =
            entry.degree || entry.degree_name || entry.title || "Degree";
          const institution =
            entry.institution || entry.school || entry.university || "";
          const field =
            entry.field || entry.field_of_study || entry.major || "";
          const graduation =
            entry.graduation || entry.graduation_date || entry.date || entry.year || "";

          return (
            <div
              key={entry.id || i}
              className="bg-white/5 rounded-xl p-4 border border-white/5"
            >
              <p className="text-sm font-bold text-white">{degree}</p>
              {institution && (
                <p className="text-xs text-[#7BC4BE] font-medium mt-0.5">
                  {institution}
                </p>
              )}
              <div className="flex items-center gap-3 mt-2">
                {field && (
                  <span className="text-[11px] text-gray-400 bg-white/5 px-2 py-0.5 rounded-full">
                    {field}
                  </span>
                )}
                {graduation && (
                  <span className="text-[11px] text-gray-500">
                    {graduation}
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
