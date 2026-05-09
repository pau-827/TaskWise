import { useState, useContext } from "react";
import { useNavigate, Link } from "react-router-dom";
import { ThemeContext } from "../context/ThemeContext";
import { THEMES } from "../theme/themes";
import { supabase } from "../services/supabase";

export default function LoginPage() {
  const navigate = useNavigate();
  const { themeName } = useContext(ThemeContext);
  const c = THEMES[themeName]?.custom?.landing ?? THEMES.light.custom.landing;

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPass, setShowPass] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    setLoading(false);

    if (error) return setError(error.message);

    navigate("/tasks");
  };

  const handleGoogleLogin = async () => {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: `${window.location.origin}/tasks`,
      },
    });

    if (error) setError(error.message);
  };

  const inputStyle = {
    width: "100%",
    padding: "11px 14px",
    borderRadius: 10,
    border: `1.5px solid ${c.cardBorder}`,
    background: c.pageBg,
    color: c.headingMain,
    fontSize: 14,
    fontFamily: "inherit",
    outline: "none",
    boxSizing: "border-box",
  };

  const labelStyle = {
    fontSize: 13,
    color: c.bodyText,
    fontWeight: 500,
    display: "block",
    marginBottom: 6,
  };

  return (
    <div style={{
      minHeight: "100vh",
      background: c.pageBg,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      fontFamily: "'DM Sans', sans-serif",
      overflow: "hidden",
      position: "relative",
    }}>
      <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&family=Playfair+Display:wght@500;600&display=swap" rel="stylesheet" />

      <style>{`
        .auth-input:focus { border-color: ${c.accent} !important; }
        .auth-input::placeholder { color: ${c.mutedText}; }
      `}</style>

      <div style={{
        position: "relative",
        zIndex: 1,
        width: "100%",
        maxWidth: 420,
        padding: "40px 36px",
        borderRadius: 24,
        background: c.cardBg,
        border: `1px solid ${c.cardBorder}`,
        boxShadow: "0 8px 40px rgba(0,0,0,0.08)",
      }}>

        {/* Header */}
        <div style={{ textAlign: "center", marginBottom: 28 }}>
          <div style={{
            width: 52,
            height: 52,
            borderRadius: 14,
            background: c.iconBg,
            margin: "0 auto 12px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "#fff",
            fontSize: 24,
          }}>✓</div>

          <h1 style={{
            margin: 0,
            fontSize: 26,
            color: c.headingMain,
            fontWeight: 600,
            fontFamily: "'Playfair Display', serif",
          }}>
            Welcome back
          </h1>

          <p style={{ marginTop: 6, fontSize: 13, color: c.mutedText }}>
            Log in to your TaskWise account
          </p>
        </div>

        {/* Google Login */}
        <button
          onClick={handleGoogleLogin}
          style={{
            width: "100%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 10,
            padding: "11px",
            borderRadius: 10,
            border: `1.5px solid ${c.cardBorder}`,
            background: c.pageBg,
            color: c.bodyText,
            cursor: "pointer",
            fontSize: 14,
            fontWeight: 500,
            marginBottom: 20,
          }}
        >
          <svg width="18" height="18" viewBox="0 0 48 48">
            <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
            <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
            <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
            <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.18 1.48-4.97 2.35-8.16 2.35-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
          </svg>

          Continue with Google
        </button>

        {/* Divider */}
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 20 }}>
          <div style={{ flex: 1, height: 1, background: c.cardBorder }} />
          <span style={{ fontSize: 12, color: c.mutedText }}>or</span>
          <div style={{ flex: 1, height: 1, background: c.cardBorder }} />
        </div>

        {/* Form */}
        <form onSubmit={handleLogin} style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          <div>
            <label style={labelStyle}>Email</label>

            <input
              className="auth-input"
              style={inputStyle}
              type="email"
              placeholder="you@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div>
            <label style={labelStyle}>Password</label>

            <div style={{ position: "relative" }}>
              <input
                className="auth-input"
                style={inputStyle}
                type={showPass ? "text" : "password"}
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />

              <button
                type="button"
                onClick={() => setShowPass(!showPass)}
                style={{
                  position: "absolute",
                  right: 12,
                  top: "50%",
                  transform: "translateY(-50%)",
                  background: "none",
                  border: "none",
                  cursor: "pointer",
                }}
              >
                {showPass ? "🙈" : "👁️"}
              </button>
            </div>
          </div>

          {error && (
            <div style={{
              padding: "10px 14px",
              borderRadius: 8,
              background: "#fff0f0",
              border: "1px solid #ffcccc",
              color: "#cc3333",
              fontSize: 13,
            }}>
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{
              padding: "12px",
              borderRadius: 10,
              border: "none",
              background: loading ? c.progressBg : c.accent,
              color: "#fff",
              cursor: loading ? "not-allowed" : "pointer",
              fontSize: 15,
              fontWeight: 500,
            }}
          >
            {loading ? "Logging in..." : "Log In"}
          </button>
        </form>

        {/* Footer */}
        <p style={{ textAlign: "center", marginTop: 20, fontSize: 13, color: c.mutedText }}>
          Don't have an account?{" "}
          <Link
            to="/signup"
            style={{
              color: c.accent,
              textDecoration: "none",
              fontWeight: 500,
            }}
          >
            Sign up
          </Link>
        </p>

        <p style={{ textAlign: "center", marginTop: 8, fontSize: 12 }}>
          <Link
            to="/"
            style={{
              color: c.mutedText,
              textDecoration: "none",
            }}
          >
            ← Back to homepage
          </Link>
        </p>
      </div>
    </div>
  );
}