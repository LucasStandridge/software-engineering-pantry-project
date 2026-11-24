
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "../lib/supabase";

export default function AuthCallback() {
  const navigate = useNavigate();
  const [message, setMessage] = useState("Signing you in...");

  useEffect(() => {
    async function finishLogin() {
      const params = new URLSearchParams(window.location.search);
      const hashParams = new URLSearchParams(
        window.location.hash.substring(1)
      );

      const oauthError =
        params.get("error_description") ||
        hashParams.get("error_description") ||
        params.get("error") ||
        hashParams.get("error");

      if (oauthError) {
        setMessage(`Google sign-in failed: ${oauthError}`);
        return;
      }

      const { data, error } = await supabase.auth.getSession();

      if (error) {
        setMessage(`Login failed: ${error.message}`);
        return;
      }

      if (!data.session) {
        setMessage("Login failed: No active session found.");
        return;
      }

      navigate("/", { replace: true });
    }

    finishLogin();
  }, [navigate]);

  return (
    <div style={{ padding: "40px", textAlign: "center" }}>
      <h2>{message}</h2>
    </div>
  );
}
