import { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { ThemeContext } from "../context/ThemeContext";
import { THEMES } from "../theme/themes";
import { supabase } from "../services/supabase";

const CLASSROOM_SCOPES = [
  "https://www.googleapis.com/auth/classroom.courses.readonly",
  "https://www.googleapis.com/auth/classroom.coursework.me.readonly",
  "https://www.googleapis.com/auth/calendar.readonly",
].join(" ");

export default function AdminLogin() {
  const navigate = useNavigate();
  const { themeName } = useContext(ThemeContext);
  const c = THEMES[themeName]?.custom?.landing ?? THEMES.light.custom.landing;
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleYes = async () => {
    setError(""); setLoading(true);
    const { error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: `${window.location.origin}/auth/admin-callback`,
        scopes: CLASSROOM_SCOPES,
        queryParams: { access_type: "offline", prompt: "consent" },
      },
    });
    if (error) { setError(error.message); setLoading(false); }
  };

  return (
    <div style={{
      minHeight: "100vh", background: c.pageBg,
      display: "flex", alignItems: "center", justifyContent: "center",
      fontFamily: "'DM Sans', sans-serif", position: "relative", overflow: "hidden",
    }}>
      <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&family=Playfair+Display:wght@500;600&display=swap" rel="stylesheet" />

      <style>{`
        @keyframes blobTopRight {
          0%   { top: 50%; right: 50%; transform: translate(50%,-50%) scale(0.3); opacity: 0; }
          30%  { opacity: 1; }
          100% { top: -120px; right: -100px; transform: translate(0,0) scale(1); opacity: 1; }
        }
        @keyframes blobBottomLeft {
          0%   { bottom: 50%; left: 50%; transform: translate(-50%,50%) scale(0.3); opacity: 0; }
          30%  { opacity: 1; }
          100% { bottom: -80px; left: -80px; transform: translate(0,0) scale(1); opacity: 1; }
        }
        @keyframes fadeUp {
          from { opacity: 0; transform: translateY(20px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes wiggle {
          0%, 100% { transform: rotate(-2deg); }
          50%      { transform: rotate(2deg); }
        }
      `}</style>

      {/* Blobs */}
      <div style={{ position: "fixed", width: 420, height: 420, borderRadius: "50%", background: c.blobColor, zIndex: 0, pointerEvents: "none", animation: "blobTopRight 1.2s cubic-bezier(0.22,1,0.36,1) forwards" }} />
      <div style={{ position: "fixed", width: 300, height: 300, borderRadius: "50%", background: c.blobColor2, zIndex: 0, pointerEvents: "none", animation: "blobBottomLeft 1.4s cubic-bezier(0.22,1,0.36,1) 0.1s forwards" }} />

      {/* Card */}
      <div style={{
        position: "relative", zIndex: 1,
        width: "100%", maxWidth: 440,
        padding: "48px 40px", borderRadius: 28,
        background: c.cardBg, border: `1px solid ${c.cardBorder}`,
        boxShadow: "0 8px 40px rgba(0,0,0,0.08)",
        animation: "fadeUp 0.6s ease forwards",
        textAlign: "center",
      }}>

        {/* Suspicious icon */}
        <div style={{
          fontSize: 52, marginBottom: 16,
          display: "inline-block",
          animation: "wiggle 2s ease-in-out infinite",
        }}>🔍</div>

        <h1 style={{
          margin: "0 0 10px",
          fontSize: 22,
          color: c.headingMain,
          fontFamily: "'Playfair Display', serif",
          fontWeight: 600,
          lineHeight: 1.3,
        }}>
          Are you sure you're<br />supposed to be here?
        </h1>

        <p style={{ margin: "0 0 32px", fontSize: 13, color: c.mutedText, lineHeight: 1.6 }}>
          This area is restricted. Only authorized personnel may proceed.
        </p>

        {error && (
          <div style={{ padding: "10px 14px", borderRadius: 8, background: "#fff0f0", border: "1px solid #ffcccc", color: "#cc3333", fontSize: 13, marginBottom: 16 }}>
            {error}
          </div>
        )}

        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {/* Yes button */}
          <button
            onClick={handleYes}
            disabled={loading}
            style={{
              padding: "13px", borderRadius: 12, border: "none",
              background: loading ? c.progressBg : c.accent,
              color: "#fff", cursor: loading ? "not-allowed" : "pointer",
              fontSize: 15, fontFamily: "inherit", fontWeight: 600,
              transition: "all 0.2s", display: "flex", alignItems: "center",
              justifyContent: "center", gap: 10,
            }}
            onMouseEnter={e => { if (!loading) e.currentTarget.style.transform = "translateY(-2px)"; }}
            onMouseLeave={e => { e.currentTarget.style.transform = "translateY(0)"; }}
          >
            {loading ? "Verifying..." : (
              <>
                <svg width="18" height="18" viewBox="0 0 48 48">
                  <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
                  <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
                  <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
                  <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.18 1.48-4.97 2.35-8.16 2.35-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
                </svg>
                Yes, I know what I'm doing
              </>
            )}
          </button>

          {/* No button */}
          <button
            onClick={() => navigate("/")}
            style={{
              padding: "13px", borderRadius: 12,
              border: `1.5px solid ${c.cardBorder}`,
              background: "transparent", color: c.mutedText,
              cursor: "pointer", fontSize: 15,
              fontFamily: "inherit", fontWeight: 500,
              transition: "all 0.2s",
            }}
            onMouseEnter={e => { e.currentTarget.style.background = c.accentLight; }}
            onMouseLeave={e => { e.currentTarget.style.background = "transparent"; }}
          >
            🏃 Nope, take me back
          </button>
        </div>

        <p style={{ marginTop: 20, fontSize: 11, color: c.mutedText, fontStyle: "italic" }}>
          Unauthorized access attempts are logged.
        </p>
      </div>
    </div>
  );
}
