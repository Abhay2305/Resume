import { Award } from "lucide-react";

export default function CertificationCard({ knowledge }) {
  const certs = knowledge?.certifications || [];

  if (!certs || certs.length === 0) return null;

  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 rounded-xl bg-amber-400/15 flex items-center justify-center">
          <Award size={20} className="text-amber-400" />
        </div>
        <div>
          <h3 className="text-sm font-bold text-white">Certifications</h3>
          <p className="text-[11px] text-gray-500 mt-0.5">
            {certs.length} certification{certs.length !== 1 ? "s" : ""}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {certs.map((cert, i) => {
          const name = cert.name || cert.title || cert;
          const issuer = cert.issuer || cert.organization || cert.provider || "";
          const date = cert.date || cert.issued_date || cert.year || "";

          return (
            <div
              key={i}
              className="bg-white/5 rounded-xl p-4 border border-white/5 flex items-start gap-3"
            >
              <div className="w-8 h-8 rounded-lg bg-amber-400/10 flex items-center justify-center shrink-0">
                <Award size={14} className="text-amber-400" />
              </div>
              <div>
                <p className="text-xs font-bold text-white">
                  {String(name)}
                </p>
                {issuer && (
                  <p className="text-[11px] text-gray-400 mt-0.5">
                    {String(issuer)}
                  </p>
                )}
                {date && (
                  <p className="text-[10px] text-gray-500 mt-0.5">
                    {String(date)}
                  </p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
