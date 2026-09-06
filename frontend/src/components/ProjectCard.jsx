import { FolderGit2 } from "lucide-react";

export default function ProjectCard({ knowledge, parsedData }) {
  const entries =
    knowledge?.projects || parsedData?.projects || [];

  if (!entries || entries.length === 0) return null;

  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 rounded-xl bg-[#7BC4BE]/15 flex items-center justify-center">
          <FolderGit2 size={20} className="text-[#7BC4BE]" />
        </div>
        <div>
          <h3 className="text-sm font-bold text-white">Projects</h3>
          <p className="text-[11px] text-gray-500 mt-0.5">
            {entries.length} project{entries.length !== 1 ? "s" : ""}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {entries.map((project, i) => {
          const name = project.name || project.title || "Project";
          const description = project.description || "";
          const technologies = project.technologies || project.tech || project.stack || [];
          const achievements = project.achievements || project.results || [];

          const techList = Array.isArray(technologies)
            ? technologies
            : typeof technologies === "string"
            ? technologies.split(",").map((t) => t.trim())
            : [];

          const achievementList = Array.isArray(achievements)
            ? achievements
            : typeof achievements === "string"
            ? achievements.split(",").map((a) => a.trim())
            : [];

          return (
            <div
              key={project.id || i}
              className="bg-white/5 rounded-xl p-4 border border-white/5 space-y-2"
            >
              <p className="text-sm font-bold text-white">{name}</p>
              {description && (
                <p className="text-[11px] text-gray-400 leading-relaxed line-clamp-3">
                  {description}
                </p>
              )}
              {techList.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mt-2">
                  {techList.map((tech, j) => (
                    <span
                      key={j}
                      className="text-[10px] text-[#7BC4BE] bg-[#7BC4BE]/10 px-2 py-0.5 rounded-full font-medium"
                    >
                      {tech}
                    </span>
                  ))}
                </div>
              )}
              {achievementList.length > 0 && (
                <ul className="space-y-1 mt-2">
                  {achievementList.map((item, j) => (
                    <li
                      key={j}
                      className="text-[11px] text-gray-400 flex items-start gap-1.5"
                    >
                      <span className="text-amber-400 mt-0.5 shrink-0">★</span>
                      <span>{String(item)}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
