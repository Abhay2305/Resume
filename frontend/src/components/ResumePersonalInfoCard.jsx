import {
  User,
  Mail,
  Phone,
  Link,
  Code,
  Globe,
  MapPin,
} from "lucide-react";

const CONTACT_FIELDS = [
  { key: "name", icon: User, label: "Name" },
  { key: "email", icon: Mail, label: "Email" },
  { key: "phone", icon: Phone, label: "Phone" },
  { key: "linkedin", icon: Link, label: "LinkedIn" },
  { key: "github", icon: Code, label: "GitHub" },
  { key: "website", icon: Globe, label: "Website" },
  { key: "location", icon: MapPin, label: "Location" },
];

export default function ResumePersonalInfoCard({ knowledge }) {
  const personal = knowledge?.personal_info || {};
  const contact = knowledge?.contact_info || {};

  const hasData = CONTACT_FIELDS.some(
    (f) => contact[f.key] || personal[f.key]
  );

  if (!hasData) return null;

  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 rounded-xl bg-[#7BC4BE]/15 flex items-center justify-center">
          <User size={20} className="text-[#7BC4BE]" />
        </div>
        <div>
          <h3 className="text-sm font-bold text-white">
            {personal.name || contact.name || "Personal Information"}
          </h3>
          <p className="text-[11px] text-gray-500 mt-0.5">
            Extracted contact details
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {CONTACT_FIELDS.map((field) => {
          const Icon = field.icon;
          const value = contact[field.key] || personal[field.key];
          if (!value) return null;
          return (
            <div
              key={field.key}
              className="flex items-center gap-3 bg-white/5 rounded-xl p-3 border border-white/5"
            >
              <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center shrink-0">
                <Icon size={14} className="text-gray-500" />
              </div>
              <div className="min-w-0">
                <p className="text-[10px] text-gray-500 uppercase font-bold tracking-wider">
                  {field.label}
                </p>
                <p className="text-xs text-white font-medium truncate">
                  {value}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
