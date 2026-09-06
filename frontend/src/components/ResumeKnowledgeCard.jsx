import { Brain, Star, TrendingUp, Calendar } from "lucide-react";

export default function ResumeKnowledgeCard({ knowledge }) {
  if (!knowledge) return null;

  const achievements = knowledge.achievements || [];
  const totalExp = knowledge.total_experience_years;

  return (
    <div className="bg-gradient-to-r from-[#7BC4BE]/10 to-[#7BC4BE]/5 border border-[#7BC4BE]/20 rounded-2xl p-6">
      <div className="flex items-center gap-3 mb-5">
        <div className="w-10 h-10 rounded-xl bg-[#7BC4BE]/20 flex items-center justify-center">
          <Brain size={20} className="text-[#7BC4BE]" />
        </div>
        <div>
          <h3 className="text-sm font-bold text-white">
            Resume Knowledge
          </h3>
          <p className="text-[11px] text-gray-400 mt-0.5">
            Canonical intelligence extracted from your resume
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-5">
        {totalExp != null && (
          <div className="bg-white/5 rounded-xl p-4 border border-white/5 text-center">
            <Calendar size={18} className="text-[#7BC4BE] mx-auto mb-2" />
            <p className="text-lg font-bold text-white">{totalExp}</p>
            <p className="text-[10px] text-gray-500 uppercase font-bold tracking-wider">
              Years Experience
            </p>
          </div>
        )}

        {knowledge.skills && (
          <div className="bg-white/5 rounded-xl p-4 border border-white/5 text-center">
            <TrendingUp size={18} className="text-[#7BC4BE] mx-auto mb-2" />
            <p className="text-lg font-bold text-white">
              {Array.isArray(knowledge.skills) ? knowledge.skills.length : "—"}
            </p>
            <p className="text-[10px] text-gray-500 uppercase font-bold tracking-wider">
              Skills Listed
            </p>
          </div>
        )}

        {achievements.length > 0 && (
          <div className="bg-white/5 rounded-xl p-4 border border-white/5 text-center">
            <Star size={18} className="text-amber-400 mx-auto mb-2" />
            <p className="text-lg font-bold text-white">
              {achievements.length}
            </p>
            <p className="text-[10px] text-gray-500 uppercase font-bold tracking-wider">
              Achievements
            </p>
          </div>
        )}
      </div>

      {achievements.length > 0 && (
        <div>
          <p className="text-[10px] text-gray-500 uppercase font-bold tracking-wider mb-2">
            Key Achievements
          </p>
          <ul className="space-y-1.5">
            {achievements.map((item, i) => (
              <li
                key={i}
                className="flex items-start gap-2 text-xs text-gray-300"
              >
                <span className="text-amber-400 mt-1 shrink-0">★</span>
                <span className="leading-relaxed">{String(item)}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
