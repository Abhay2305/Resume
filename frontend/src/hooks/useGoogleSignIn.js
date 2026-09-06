import { useEffect, useRef } from "react";

const GSI_SCRIPT_URL = "https://accounts.google.com/gsi/client";
const SCRIPT_ID = "google-identity-services-script";

let scriptLoaded = false;
let scriptLoading = false;

/**
 * Loads the Google Identity Services script once globally.
 * Prevents duplicate injection across components.
 * Returns { ready, error } state.
 */
export function useGoogleSignIn(buttonId, onCredentialResponse) {
  const readyRef = useRef(false);
  const callbackRef = useRef(onCredentialResponse);

  useEffect(() => {
    callbackRef.current = onCredentialResponse;
    if (!buttonId) return;

    function initGoogle() {
      if (!window.google?.accounts?.id) return;

      window.google.accounts.id.initialize({
        client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
        callback: (response) => callbackRef.current(response),
      });

      const buttonEl = document.getElementById(buttonId);
      if (buttonEl) {
        window.google.accounts.id.renderButton(buttonEl, {
          theme: "outline",
          size: "large",
          width: "100%",
        });
        readyRef.current = true;
        console.log(`[GoogleSignIn] Button rendered into #${buttonId}`);
      }
    }

    // If already loaded, just init
    if (scriptLoaded && window.google?.accounts?.id) {
      initGoogle();
      return;
    }

    // If currently loading, wait
    if (scriptLoading) {
      const interval = setInterval(() => {
        if (scriptLoaded) {
          clearInterval(interval);
          initGoogle();
        }
      }, 50);
      return () => clearInterval(interval);
    }

    // First load — inject script
    scriptLoading = true;
    const script = document.createElement("script");
    script.id = SCRIPT_ID;
    script.src = GSI_SCRIPT_URL;
    script.async = true;
    script.onload = () => {
      scriptLoaded = true;
      scriptLoading = false;
      console.log("[GoogleSignIn] GSI script loaded");
      initGoogle();
    };
    script.onerror = () => {
      scriptLoading = false;
      console.error("[GoogleSignIn] Failed to load GSI script");
    };
    document.head.appendChild(script);

    return () => {
      // Do not remove script tag — it's shared globally
      // But clean up rendered button if component unmounts
      if (window.google?.accounts?.id) {
        try {
          window.google.accounts.id.disableAutoSelect();
        } catch {
          // Silent — not critical
        }
      }
    };
  }, [buttonId, onCredentialResponse]);
}
