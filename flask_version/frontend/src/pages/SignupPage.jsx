import { useState, useContext } from "react";
import { useNavigate, Link } from "react-router-dom";
import { ThemeContext } from "../context/ThemeContext";
import { THEMES } from "../theme/themes";
import { supabase } from "../services/supabase";

export default function SignupPage() {
  const navigate = useNavigate();
  const { themeName } = useContext(ThemeContext);
  const c = THEMES[themeName]?.custom?.landing ?? THEMES.light.custom.landing;

  // Steps: "form" | "otp"
  const [step, setStep]           = useState("form");
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail]         = useState("");
  const [password, setPassword]   = useState("");
  const [confirmPass, setConfirmPass] = useState("");
  const [otp, setOtp]             = useState("");
  const [error, setError]         = useState("");
  const [loading, setLoading]     = useState(false);
  const [showPass, setShowPass]   = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  const handleSignup = async (e) => {
    e.preventDefault();
    setError("");

    if (password !== confirmPass) {
      setError("Passwords do not match.");
      return;
    }
    if (password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }

    setLoading(true);

    const { error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: { display_name: displayName },
      },
    });

    if (error) {
      setError(error.message);
      setLoading(false);
    } else {
      setStep("otp");
      setLoading(false);
    }
  };

  const handleVerifyOtp = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    const { error } = await supabase.auth.verifyOtp({
      email,
      token: otp,
      type: "signup",
    });

    if (error) {
      setError(error.message);
      setLoading(false);
    } else {
      navigate("/tasks");
    }
  };

  const inputStyle = {
    width: "100%", padding: "11px 14px", borderRadius: 10,
    border: `1.5px solid ${c.cardBorder}`,
    background: c.pageBg, color: c.headingMain,
    fontSize: 14, fontFamily: "inherit", outline: "none",
    transition: "border-color 0.2s",
    boxSizing: "border-box",
  };

  return (
    <div style={{
      minHeight: "100vh", background: c.pageBg,
      fontFamily: "'DM Sans', sans-serif",
      display: "flex", alignItems: "center", justifyContent: "center",
      position: "relative", overflow: "hidden",
      transition: "background 0.4s ease",
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
        @keyframes blobTopLeft {
          0%   { top: 50%; left: 50%; transform: translate(-50%,-50%) scale(0.2); opacity: 0; }
          30%  { opacity: 1; }
          100% { top: 60px; left: -60px; transform: translate(0,0) scale(1); opacity: 1; }
        }
        @keyframes fadeUp {
          from { opacity: 0; transform: translateY(20px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        .auth-input:focus { border-color: ${c.accent} !important; }
        .auth-input::placeholder { color: ${c.mutedText}; }
        .otp-input {
          width: 48px !important; text-align: center; font-size: 22px !important;
          font-weight: 500 !important; padding: 12px 0 !important;
          letter-spacing: 2px;
        }
      `}</style>

      {/* Blobs */}
      <div style={{
        position: "fixed", width: 420, height: 420, borderRadius: "50%",
        background: c.blobColor, zIndex: 0, pointerEvents: "none",
        animation: "blobTopRight 1.2s cubic-bezier(0.22,1,0.36,1) forwards",
      }} />
      <div style={{
        position: "fixed", width: 300, height: 300, borderRadius: "50%",
        background: c.blobColor2, zIndex: 0, pointerEvents: "none",
        animation: "blobBottomLeft 1.4s cubic-bezier(0.22,1,0.36,1) 0.1s forwards",
      }} />
      <div style={{
        position: "fixed", width: 200, height: 200, borderRadius: "50%",
        background: c.blobColor3, zIndex: 0, pointerEvents: "none",
        animation: "blobTopLeft 1.6s cubic-bezier(0.22,1,0.36,1) 0.2s forwards",
      }} />

      {/* Card */}
      <div style={{
        position: "relative", zIndex: 1,
        background: c.cardBg, borderRadius: 24, padding: "40px 36px",
        border: `1px solid ${c.cardBorder}`,
        width: "100%", maxWidth: 420,
        boxShadow: "0 8px 40px rgba(0,0,0,0.08)",
        animation: "fadeUp 0.6s ease forwards",
      }}>

        {/* ── STEP 1: Signup Form ── */}
        {step === "form" && (
          <>
            <div style={{ textAlign: "center", marginBottom: 28 }}>
              <div style={{
                width: 52, height: 52, borderRadius: 14,
                background: c.iconBg, margin: "0 auto 12px",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 24, color: "#fff",
              }}>✓</div>
              <h1 style={{
                fontFamily: "'Playfair Display', serif",
                fontSize: 26, fontWeight: 600, color: c.headingMain,
                margin: 0, letterSpacing: "-0.3px",
              }}>Create account</h1>
              <p style={{ margin: "6px 0 0", fontSize: 13, color: c.mutedText }}>
                Join TaskWise and stay on track
              </p>
            </div>

            {/* Google (disabled) */}
            <div title="Coming soon!" style={{
              display: "flex", alignItems: "center", justifyContent: "center", gap: 10,
              padding: "10px", borderRadius: 10, border: `1.5px solid ${c.cardBorder}`,
              background: c.pageBg, color: c.mutedText,
              fontSize: 14, fontWeight: 500, cursor: "not-allowed",
              marginBottom: 20, opacity: 0.6, userSelect: "none",
            }}>
              <svg width="18" height="18" viewBox="0 0 48 48">
                <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
                <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
                <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
                <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.18 1.48-4.97 2.35-8.16 2.35-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
              </svg>
              Continue with Google — Coming soon
            </div>

            {/* Divider */}
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 20 }}>
              <div style={{ flex: 1, height: 1, background: c.cardBorder }} />
              <span style={{ fontSize: 12, color: c.mutedText }}>or</span>
              <div style={{ flex: 1, height: 1, background: c.cardBorder }} />
            </div>

            <form onSubmit={handleSignup} style={{ display: "flex", flexDirection: "column", gap: 14 }}>
              <div>
                <label style={{ fontSize: 13, color: c.bodyText, fontWeight: 500, display: "block", marginBottom: 6 }}>
                  Display Name
                </label>
                <input
                  className="auth-input" style={inputStyle}
                  type="text" placeholder="e.g. ivyyy"
                  value={displayName} onChange={e => setDisplayName(e.target.value)}
                  required
                />
              </div>

              <div>
                <label style={{ fontSize: 13, color: c.bodyText, fontWeight: 500, display: "block", marginBottom: 6 }}>
                  Email
                </label>
                <input
                  className="auth-input" style={inputStyle}
                  type="email" placeholder="you@email.com"
                  value={email} onChange={e => setEmail(e.target.value)}
                  required
                />
              </div>

              <div>
                <label style={{ fontSize: 13, color: c.bodyText, fontWeight: 500, display: "block", marginBottom: 6 }}>
                  Password
                </label>
                <div style={{ position: "relative" }}>
                  <input
                    className="auth-input" style={inputStyle}
                    type={showPass ? "text" : "password"} placeholder="Min. 6 characters"
                    value={password} onChange={e => setPassword(e.target.value)}
                    required
                  />
                  <button type="button" onClick={() => setShowPass(!showPass)} style={{
                    position: "absolute", right: 12, top: "50%", transform: "translateY(-50%)",
                    background: "none", border: "none", cursor: "pointer", fontSize: 16, color: c.mutedText, padding: 0,
                  }}>{showPass ? "🙈" : "👁️"}</button>
                </div>
              </div>

              <div>
                <label style={{ fontSize: 13, color: c.bodyText, fontWeight: 500, display: "block", marginBottom: 6 }}>
                  Confirm Password
                </label>
                <div style={{ position: "relative" }}>
                  <input
                    className="auth-input" style={inputStyle}
                    type={showConfirm ? "text" : "password"} placeholder="Repeat password"
                    value={confirmPass} onChange={e => setConfirmPass(e.target.value)}
                    required
                  />
                  <button type="button" onClick={() => setShowConfirm(!showConfirm)} style={{
                    position: "absolute", right: 12, top: "50%", transform: "translateY(-50%)",
                    background: "none", border: "none", cursor: "pointer", fontSize: 16, color: c.mutedText, padding: 0,
                  }}>{showConfirm ? "🙈" : "👁️"}</button>
                </div>
              </div>

              {error && (
                <div style={{
                  background: "#fff0f0", border: "1px solid #ffcccc",
                  borderRadius: 8, padding: "10px 14px", fontSize: 13, color: "#cc3333",
                }}>{error}</div>
              )}

              <button type="submit" disabled={loading} style={{
                padding: "12px", borderRadius: 10, border: "none",
                background: loading ? c.progressBg : c.accent,
                color: "#fff", cursor: loading ? "not-allowed" : "pointer",
                fontSize: 15, fontFamily: "inherit", fontWeight: 500,
                marginTop: 4, transition: "background 0.2s",
              }}>
                {loading ? "Creating account..." : "Create Account"}
              </button>
            </form>

            <p style={{ textAlign: "center", marginTop: 20, fontSize: 13, color: c.mutedText }}>
              Already have an account?{" "}
              <Link to="/login" style={{ color: c.accent, fontWeight: 500, textDecoration: "none" }}>
                Log in
              </Link>
            </p>
            <p style={{ textAlign: "center", marginTop: 8, fontSize: 12 }}>
              <Link to="/" style={{ color: c.mutedText, textDecoration: "none" }}>
                ← Back to homepage
              </Link>
            </p>
          </>
        )}

        {/* ── STEP 2: OTP Verification ── */}
        {step === "otp" && (
          <>
            <div style={{ textAlign: "center", marginBottom: 28 }}>
              <div style={{
                width: 52, height: 52, borderRadius: 14,
                background: c.iconBg, margin: "0 auto 12px",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 24, color: "#fff",
              }}>📬</div>
              <h1 style={{
                fontFamily: "'Playfair Display', serif",
                fontSize: 24, fontWeight: 600, color: c.headingMain,
                margin: 0, letterSpacing: "-0.3px",
              }}>Check your email</h1>
              <p style={{ margin: "8px 0 0", fontSize: 13, color: c.mutedText, lineHeight: 1.6 }}>
                We sent a 6-digit code to<br />
                <strong style={{ color: c.bodyText }}>{email}</strong>
              </p>
            </div>

            <form onSubmit={handleVerifyOtp} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              <div>
                <label style={{ fontSize: 13, color: c.bodyText, fontWeight: 500, display: "block", marginBottom: 10, textAlign: "center" }}>
                  Enter verification code
                </label>
                <input
                  className="auth-input"
                  style={{
                    ...inputStyle,
                    textAlign: "center",
                    fontSize: 32,
                    letterSpacing: 12,
                    fontWeight: 600,
                    width: "100%",
                    padding: "16px 14px",
                  }}
                  type="text" placeholder="······"
                  maxLength={6}
                  value={otp} onChange={e => setOtp(e.target.value.replace(/\D/g, ""))}
                  required
                />
              </div>

              {error && (
                <div style={{
                  background: "#fff0f0", border: "1px solid #ffcccc",
                  borderRadius: 8, padding: "10px 14px", fontSize: 13, color: "#cc3333",
                }}>{error}</div>
              )}

              <button type="submit" disabled={loading || otp.length < 6} style={{
                padding: "12px", borderRadius: 10, border: "none",
                background: (loading || otp.length < 6) ? c.progressBg : c.accent,
                color: "#fff", cursor: (loading || otp.length < 6) ? "not-allowed" : "pointer",
                fontSize: 15, fontFamily: "inherit", fontWeight: 500,
                transition: "background 0.2s",
              }}>
                {loading ? "Verifying..." : "Verify & Continue"}
              </button>

              <button
                type="button"
                onClick={() => setStep("form")}
                style={{
                  background: "none", border: "none", color: c.mutedText,
                  fontSize: 13, cursor: "pointer", fontFamily: "inherit",
                  textDecoration: "underline", padding: 0,
                }}
              >
                ← Back to signup
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  );
}
