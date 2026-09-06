import { useState, useEffect } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { CheckCircle2, XCircle, Loader2, ArrowRight } from "lucide-react";
import { api } from "../services/api";

export default function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState("verifying"); // verifying, success, error
  const [message, setMessage] = useState("");

  useEffect(() => {
    (async () => {
      const token = searchParams.get("token");
      if (token) {
        try {
          await api.auth.verifyEmail(token);
          setStatus("success");
          setMessage("Your email has been verified successfully!");
        } catch (err) {
          setStatus("error");
          setMessage(err.message || "Failed to verify email");
        }
      } else {
        setStatus("error");
        setMessage("No verification token provided");
      }
    })();
  }, [searchParams]);

  return (
    <div className="min-h-screen bg-gradient-to-tr from-[#1A2B2A] via-[#0F1E1E] to-[#2D3F3E] flex items-center justify-center p-4">
      <div className="absolute top-1/4 left-1/4 w-80 h-80 bg-[#7BC4BE]/10 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[#FAD07A]/5 rounded-full blur-[120px] pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md bg-white/5 backdrop-blur-xl border border-white/10 p-8 rounded-2xl shadow-2xl relative overflow-hidden"
      >
        <div className="absolute top-0 left-0 w-full h-[3px] bg-gradient-to-r from-[#7BC4BE] via-[#FAD07A] to-[#7BC4BE]" />

        <div className="text-center">
          {status === "verifying" && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="py-8"
            >
              <Loader2 className="animate-spin text-[#7BC4BE] mx-auto mb-4" size={48} />
              <h2 className="text-xl font-medium text-white/90 mb-2">Verifying your email</h2>
              <p className="text-gray-400 text-sm">Please wait while we verify your email address...</p>
            </motion.div>
          )}

          {status === "success" && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="py-8"
            >
              <CheckCircle2 className="text-emerald-400 mx-auto mb-4" size={64} />
              <h2 className="text-xl font-medium text-white/90 mb-2">Email Verified!</h2>
              <p className="text-gray-400 text-sm mb-6">{message}</p>
              <Link
                to="/dashboard"
                className="inline-flex items-center gap-2 bg-gradient-to-r from-[#7BC4BE] to-[#4A9E98] hover:from-[#8AD6CF] hover:to-[#5BB2AC] text-[#1A2B2A] font-semibold rounded-xl py-3 px-6 text-sm transition-all"
              >
                Go to Dashboard <ArrowRight size={16} />
              </Link>
            </motion.div>
          )}

          {status === "error" && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="py-8"
            >
              <XCircle className="text-rose-400 mx-auto mb-4" size={64} />
              <h2 className="text-xl font-medium text-white/90 mb-2">Verification Failed</h2>
              <p className="text-gray-400 text-sm mb-6">{message}</p>
              <div className="space-y-3">
                <Link
                  to="/login"
                  className="inline-flex items-center gap-2 bg-gradient-to-r from-[#7BC4BE] to-[#4A9E98] hover:from-[#8AD6CF] hover:to-[#5BB2AC] text-[#1A2B2A] font-semibold rounded-xl py-3 px-6 text-sm transition-all"
                >
                  Go to Login <ArrowRight size={16} />
                </Link>
                <p className="text-gray-500 text-xs">
                  Need a new verification link?{" "}
                  <Link to="/login" className="text-[#7BC4BE] hover:underline">
                    Log in and resend
                  </Link>
                </p>
              </div>
            </motion.div>
          )}
        </div>
      </motion.div>
    </div>
  );
}
