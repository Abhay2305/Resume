import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Shield,
  Mail,
  Lock,
  Trash2,
  CheckCircle2,
  AlertTriangle,
  Eye,
  EyeOff,
  ArrowRight,
  Loader2,

  Key,
} from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { api } from "../services/api";

export default function AuthSettings() {
  const { user } = useAuth();
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await api.auth.getSettings();
        if (!cancelled) setSettings(data);
      } catch (err) {
        if (!cancelled) console.error("Failed to load settings:", err);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  async function loadSettings() {
    try {
      const data = await api.auth.getSettings();
      setSettings(data);
    } catch (err) {
      console.error("Failed to load settings:", err);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#1A2B2A] via-[#0F1E1E] to-[#2D3F3E] flex items-center justify-center">
        <Loader2 className="animate-spin text-[#7BC4BE]" size={32} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#1A2B2A] via-[#0F1E1E] to-[#2D3F3E] p-6">
      <div className="max-w-2xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl overflow-hidden"
        >
          {/* Header */}
          <div className="p-6 border-b border-white/10">
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              <Shield className="text-[#7BC4BE]" size={24} />
              Authentication Settings
            </h1>
            <p className="text-gray-400 text-sm mt-1">
              Manage your account security and authentication preferences
            </p>
          </div>

          {/* Tab Navigation */}
          <div className="flex border-b border-white/10">
            {[
              { id: "overview", label: "Overview", icon: Shield },
              { id: "password", label: "Password", icon: Lock },
              { id: "email", label: "Email", icon: Mail },
              { id: "danger", label: "Danger Zone", icon: Trash2 },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 flex items-center justify-center gap-2 py-3 text-sm font-medium transition-colors ${
                  activeTab === tab.id
                    ? "text-[#7BC4BE] border-b-2 border-[#7BC4BE]"
                    : "text-gray-400 hover:text-white"
                }`}
              >
                <tab.icon size={16} />
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="p-6">
            <AnimatePresence mode="wait">
              {activeTab === "overview" && (
                <OverviewTab settings={settings} user={user} />
              )}
              {activeTab === "password" && (
                <PasswordTab settings={settings} refreshSettings={loadSettings} />
              )}
              {activeTab === "email" && (
                <EmailTab settings={settings} refreshSettings={loadSettings} />
              )}
              {activeTab === "danger" && (
                <DangerTab settings={settings} />
              )}
            </AnimatePresence>
          </div>
        </motion.div>
      </div>
    </div>
  );
}

function OverviewTab({ settings }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      className="space-y-4"
    >
      <div className="bg-white/5 rounded-xl p-4">
        <h3 className="text-white font-medium mb-3">Account Information</h3>
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-gray-400 text-sm">Email</span>
            <span className="text-white text-sm">{settings?.email}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-400 text-sm">Login Provider</span>
            <span className="text-white text-sm flex items-center gap-1">
              {settings?.login_provider === "google" ? (
                <>
                  <img src="https://www.google.com/favicon.ico" alt="" className="w-4 h-4" />
                  Google
                </>
              ) : (
                <>
                  <Key size={14} />
                  Email & Password
                </>
              )}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-400 text-sm">Email Verified</span>
            {settings?.is_verified ? (
              <span className="text-emerald-400 text-sm flex items-center gap-1">
                <CheckCircle2 size={14} />
                Verified
              </span>
            ) : (
              <span className="text-amber-400 text-sm flex items-center gap-1">
                <AlertTriangle size={14} />
                Not Verified
              </span>
            )}
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-400 text-sm">Last Login</span>
            <span className="text-white text-sm">
              {settings?.last_login_at
                ? new Date(settings.last_login_at).toLocaleDateString()
                : "N/A"}
            </span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

function PasswordTab({ settings, refreshSettings }) {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showCurrent, setShowCurrent] = useState(false);
  const [showNew, setShowNew] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: "", text: "" });

  const handleChangePassword = async (e) => {
    e.preventDefault();
    setMessage({ type: "", text: "" });

    if (newPassword !== confirmPassword) {
      setMessage({ type: "error", text: "New passwords do not match" });
      return;
    }

    if (currentPassword === newPassword) {
      setMessage({ type: "error", text: "New password must be different from current" });
      return;
    }

    setLoading(true);
    try {
      await api.auth.changePassword(currentPassword, newPassword, confirmPassword);
      setMessage({ type: "success", text: "Password changed successfully" });
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      refreshSettings();
    } catch (err) {
      setMessage({ type: "error", text: err.message || "Failed to change password" });
    } finally {
      setLoading(false);
    }
  };

  if (!settings?.has_password) {
    return (
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: 20 }}
        className="text-center py-8"
      >
        <Key className="mx-auto text-gray-500 mb-3" size={48} />
        <h3 className="text-white font-medium mb-2">No Password Set</h3>
        <p className="text-gray-400 text-sm">
          Your account uses Google sign-in. You can set a password through the settings page.
        </p>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
    >
      <form onSubmit={handleChangePassword} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">
            Current Password
          </label>
          <div className="relative">
            <input
              type={showCurrent ? "text" : "password"}
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              required
              className="w-full bg-white/5 border border-white/10 rounded-xl py-3 px-4 text-white text-sm placeholder-gray-500 focus:outline-none focus:border-[#7BC4BE] focus:ring-1 focus:ring-[#7BC4BE] transition-all pr-10"
            />
            <button
              type="button"
              onClick={() => setShowCurrent(!showCurrent)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
            >
              {showCurrent ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">
            New Password
          </label>
          <div className="relative">
            <input
              type={showNew ? "text" : "password"}
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
              className="w-full bg-white/5 border border-white/10 rounded-xl py-3 px-4 text-white text-sm placeholder-gray-500 focus:outline-none focus:border-[#7BC4BE] focus:ring-1 focus:ring-[#7BC4BE] transition-all pr-10"
            />
            <button
              type="button"
              onClick={() => setShowNew(!showNew)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
            >
              {showNew ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">
            Confirm New Password
          </label>
          <input
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            className="w-full bg-white/5 border border-white/10 rounded-xl py-3 px-4 text-white text-sm placeholder-gray-500 focus:outline-none focus:border-[#7BC4BE] focus:ring-1 focus:ring-[#7BC4BE] transition-all"
          />
        </div>

        {message.text && (
          <div
            className={`p-3 rounded-lg text-sm ${
              message.type === "success"
                ? "bg-emerald-500/10 border border-emerald-500/20 text-emerald-300"
                : "bg-rose-500/10 border border-rose-500/20 text-rose-300"
            }`}
          >
            {message.text}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-gradient-to-r from-[#7BC4BE] to-[#4A9E98] hover:from-[#8AD6CF] hover:to-[#5BB2AC] text-[#1A2B2A] font-semibold rounded-xl py-3 text-sm transition-all flex items-center justify-center gap-2 disabled:opacity-50"
        >
          {loading ? (
            <Loader2 className="animate-spin" size={16} />
          ) : (
            <>
              Change Password <ArrowRight size={16} />
            </>
          )}
        </button>
      </form>
    </motion.div>
  );
}

function EmailTab({ settings }) {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: "", text: "" });

  const handleSendVerification = async () => {
    setLoading(true);
    setMessage({ type: "", text: "" });
    try {
      const result = await api.auth.sendVerification();
      setMessage({ type: "success", text: result.message || "Verification email sent" });
    } catch (err) {
      setMessage({ type: "error", text: err.message || "Failed to send verification email" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      className="space-y-4"
    >
      <div className="bg-white/5 rounded-xl p-4">
        <h3 className="text-white font-medium mb-3">Email Verification</h3>
        <p className="text-gray-400 text-sm mb-4">
          Verify your email address to secure your account and enable all features.
        </p>

        {settings?.is_verified ? (
          <div className="flex items-center gap-2 text-emerald-400">
            <CheckCircle2 size={16} />
            <span className="text-sm">Email verified on {new Date(settings.email_verified_at).toLocaleDateString()}</span>
          </div>
        ) : (
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-amber-400">
              <AlertTriangle size={16} />
              <span className="text-sm">Email not yet verified</span>
            </div>
            <button
              onClick={handleSendVerification}
              disabled={loading}
              className="bg-[#7BC4BE]/10 border border-[#7BC4BE]/30 text-[#7BC4BE] hover:bg-[#7BC4BE]/20 font-medium rounded-xl py-2 px-4 text-sm transition-all flex items-center gap-2 disabled:opacity-50"
            >
              {loading ? (
                <Loader2 className="animate-spin" size={16} />
              ) : (
                <>
                  <Mail size={16} />
                  Send Verification Email
                </>
              )}
            </button>
          </div>
        )}
      </div>

      {message.text && (
        <div
          className={`p-3 rounded-lg text-sm ${
            message.type === "success"
              ? "bg-emerald-500/10 border border-emerald-500/20 text-emerald-300"
              : "bg-rose-500/10 border border-rose-500/20 text-rose-300"
          }`}
        >
          {message.text}
        </div>
      )}
    </motion.div>
  );
}

function DangerTab() {
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: "", text: "" });
  const [confirmStep, setConfirmStep] = useState(false);

  const handleDeleteAccount = async (e) => {
    e.preventDefault();
    setMessage({ type: "", text: "" });

    if (!confirmStep) {
      setConfirmStep(true);
      return;
    }

    setLoading(true);
    try {
      await api.auth.deleteAccount(password);
      setMessage({ type: "success", text: "Account deleted successfully" });
      // Redirect to home after a short delay
      setTimeout(() => {
        window.location.href = "/";
      }, 2000);
    } catch (err) {
      setMessage({ type: "error", text: err.message || "Failed to delete account" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
    >
      <div className="bg-rose-500/5 border border-rose-500/20 rounded-xl p-4">
        <h3 className="text-rose-400 font-medium mb-2 flex items-center gap-2">
          <Trash2 size={18} />
          Delete Account
        </h3>
        <p className="text-gray-400 text-sm mb-4">
          Permanently delete your account and all associated data. This action cannot be undone.
        </p>

        <form onSubmit={handleDeleteAccount} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">
              Enter your password to confirm
            </label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="Your password"
                className="w-full bg-white/5 border border-white/10 rounded-xl py-3 px-4 text-white text-sm placeholder-gray-500 focus:outline-none focus:border-rose-500 focus:ring-1 focus:ring-rose-500 transition-all pr-10"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          {confirmStep && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              className="bg-rose-500/10 border border-rose-500/20 rounded-lg p-3"
            >
              <p className="text-rose-300 text-sm">
                <strong>Warning:</strong> This will permanently delete your account. Type "DELETE" in the confirmation field below.
              </p>
            </motion.div>
          )}

          {message.text && (
            <div
              className={`p-3 rounded-lg text-sm ${
                message.type === "success"
                  ? "bg-emerald-500/10 border border-emerald-500/20 text-emerald-300"
                  : "bg-rose-500/10 border border-rose-500/20 text-rose-300"
              }`}
            >
              {message.text}
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !password}
            className="w-full bg-rose-500/20 border border-rose-500/30 text-rose-400 hover:bg-rose-500/30 font-semibold rounded-xl py-3 text-sm transition-all flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {loading ? (
              <Loader2 className="animate-spin" size={16} />
            ) : confirmStep ? (
              <>
                <Trash2 size={16} />
                Confirm Delete Account
              </>
            ) : (
              <>
                <Trash2 size={16} />
                Delete Account
              </>
            )}
          </button>
        </form>
      </div>
    </motion.div>
  );
}
