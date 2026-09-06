import { Layers } from "lucide-react";

const CATEGORY_LABELS = {
  programming_languages: "Programming Languages",
  frameworks: "Frameworks",
  libraries: "Libraries",
  databases: "Databases",
  cloud_platforms: "Cloud Platforms",
  devops_tools: "DevOps Tools",
  ai_ml: "AI / ML",
  tools: "Tools",
  other: "Other",
};

export default function SkillCategoryCard({ knowledge, entities }) {
  const skills = knowledge?.skills || [];
  const technologies = knowledge?.technologies || {};

  // Build categories from knowledge.skills (array of skill objects or strings)
  const categories = {};

  if (Array.isArray(skills)) {
    skills.forEach((skill) => {
      if (typeof skill === "string") {
        if (!categories.Other) categories.Other = [];
        categories.Other.push(skill);
      } else {
        const cat = skill.category || skill.type || "Other";
        if (!categories[cat]) categories[cat] = [];
        categories[cat].push(skill.name || skill.value || skill);
      }
    });
  }

  // Merge in technologies (object keyed by category)
  if (technologies && typeof technologies === "object") {
    Object.entries(technologies).forEach(([cat, items]) => {
      const list = Array.isArray(items)
        ? items
        : typeof items === "string"
        ? items.split(",").map((t) => t.trim())
        : [items];
      if (!categories[cat]) categories[cat] = [];
      list.forEach((item) => {
        const val = typeof item === "string" ? item : item.name || item.value || String(item);
        if (!categories[cat].includes(val)) categories[cat].push(val);
      });
    });
  }

  // Merge entities by type into categories
  if (Array.isArray(entities)) {
    const entityCategoryMap = {
      skill: "Other",
      technology: "Other",
      framework: "frameworks",
      library: "libraries",
      database: "databases",
      cloud_platform: "cloud_platforms",
      devops_tool: "devops_tools",
      ai_ml: "ai_ml",
      language: "programming_languages",
    };
    entities.forEach((e) => {
      const cat = entityCategoryMap[e.entity_type] || e.entity_type || "Other";
      if (!categories[cat]) categories[cat] = [];
      if (!categories[cat].includes(e.entity_value)) {
        categories[cat].push(e.entity_value);
      }
    });
  }

  const entries = Object.entries(categories).filter(
    ([, items]) => items.length > 0
  );

  if (entries.length === 0) return null;

  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 rounded-xl bg-[#7BC4BE]/15 flex items-center justify-center">
          <Layers size={20} className="text-[#7BC4BE]" />
        </div>
        <div>
          <h3 className="text-sm font-bold text-white">Skills & Technologies</h3>
          <p className="text-[11px] text-gray-500 mt-0.5">
            {entries.length} categories, {entries.reduce((a, [, s]) => a + s.length, 0)} total skills
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {entries.map(([cat, items]) => (
          <div
            key={cat}
            className="bg-white/5 rounded-xl p-4 border border-white/5"
          >
            <p className="text-[11px] text-gray-400 uppercase font-bold tracking-wider mb-2">
              {CATEGORY_LABELS[cat] || cat}
            </p>
            <div className="flex flex-wrap gap-1.5">
              {items.map((item, i) => (
                <span
                  key={i}
                  className="text-[11px] text-[#7BC4BE] bg-[#7BC4BE]/10 px-2.5 py-1 rounded-full font-medium"
                >
                  {String(item)}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
