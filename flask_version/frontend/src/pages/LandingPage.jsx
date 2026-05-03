import { useEffect, useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { ThemeContext } from "../context/ThemeContext";
import { THEMES } from "../theme/themes";

export default function LandingPage() {
  const navigate = useNavigate();
  const { themeName } = useContext(ThemeContext);
  const c = THEMES[themeName]?.custom?.landing ?? THEMES.light.custom.landing;

  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setVisible(true), 100);
    return () => clearTimeout(t);
  }, []);

  return (
    <div style={{
      minHeight: "100vh",
      background: c.pageBg,
      fontFamily: "'DM Sans', sans-serif",
      overflowX: "hidden",
      transition: "background 0.4s ease",
    }}>
      <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&family=Playfair+Display:wght@500;600&display=swap" rel="stylesheet" />

      <style>{`
        @keyframes blobTopRight {
          0%   { top: 50%; right: 50%; transform: translate(50%, -50%) scale(0.3); opacity: 0; }
          30%  { opacity: 1; }
          100% { top: -120px; right: -100px; transform: translate(0, 0) scale(1); opacity: 1; }
        }
        @keyframes blobBottomLeft {
          0%   { bottom: 50%; left: 50%; transform: translate(-50%, 50%) scale(0.3); opacity: 0; }
          30%  { opacity: 1; }
          100% { bottom: -80px; left: -80px; transform: translate(0, 0) scale(1); opacity: 1; }
        }
        @keyframes blobTopLeft {
          0%   { top: 50%; left: 50%; transform: translate(-50%, -50%) scale(0.2); opacity: 0; }
          30%  { opacity: 1; }
          100% { top: 60px; left: -60px; transform: translate(0, 0) scale(1); opacity: 1; }
        }
      `}</style>

      {/* Blobs */}
      <div style={{
        position: "fixed", width: 420, height: 420,
        borderRadius: "50%", background: c.blobColor, zIndex: 0, pointerEvents: "none",
        animation: "blobTopRight 1.2s cubic-bezier(0.22, 1, 0.36, 1) forwards",
        transition: "background 0.4s ease",
      }} />
      <div style={{
        position: "fixed", width: 300, height: 300,
        borderRadius: "50%", background: c.blobColor2, zIndex: 0, pointerEvents: "none",
        animation: "blobBottomLeft 1.4s cubic-bezier(0.22, 1, 0.36, 1) 0.1s forwards",
        transition: "background 0.4s ease",
      }} />
      <div style={{
        position: "fixed", width: 200, height: 200,
        borderRadius: "50%", background: c.blobColor3, zIndex: 0, pointerEvents: "none",
        animation: "blobTopLeft 1.6s cubic-bezier(0.22, 1, 0.36, 1) 0.2s forwards",
        transition: "background 0.4s ease",
      }} />

      {/* Nav */}
      <nav style={{
        position: "sticky", top: 0, zIndex: 100,
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "0 2.5rem", height: 64,
        background: c.navBg, backdropFilter: "blur(12px)",
        borderBottom: `1px solid ${c.navBorder}`,
        transition: "background 0.4s ease, border-color 0.4s ease",
      }}>
        <span style={{
          fontFamily: "'Playfair Display', serif", fontSize: 22,
          color: c.logoText, letterSpacing: "-0.3px", transition: "color 0.4s ease",
        }}>
          TaskWise
        </span>
        <div style={{ display: "flex", gap: 12 }}>
          <button
            onClick={() => navigate("/login")}
            style={{
              padding: "8px 22px", borderRadius: 50, border: `1.5px solid ${c.accent}`,
              background: "transparent", color: c.logoText, cursor: "pointer",
              fontSize: 14, fontFamily: "inherit", fontWeight: 500,
              transition: "all 0.2s",
            }}
            onMouseEnter={e => { e.currentTarget.style.background = c.accentLight; }}
            onMouseLeave={e => { e.currentTarget.style.background = "transparent"; }}
          >
            Log In
          </button>
          <button
            onClick={() => navigate("/signup")}
            style={{
              padding: "8px 22px", borderRadius: 50, border: "none",
              background: c.accent, color: "#fff", cursor: "pointer",
              fontSize: 14, fontFamily: "inherit", fontWeight: 500,
              transition: "all 0.2s",
            }}
            onMouseEnter={e => { e.currentTarget.style.background = c.accentHover; }}
            onMouseLeave={e => { e.currentTarget.style.background = c.accent; }}
          >
            Sign Up
          </button>
        </div>
      </nav>

      {/* Hero */}
      <section style={{
        position: "relative", zIndex: 1,
        maxWidth: 1100, margin: "0 auto",
        padding: "80px 2.5rem 60px",
        display: "grid", gridTemplateColumns: "1fr 1fr", gap: 60, alignItems: "center",
        opacity: visible ? 1 : 0, transform: visible ? "translateY(0)" : "translateY(24px)",
        transition: "opacity 0.7s ease, transform 0.7s ease",
      }}>
        {/* Left */}
        <div>
          <div style={{
            display: "inline-flex", alignItems: "center", gap: 6,
            background: c.pillBg, borderRadius: 50, padding: "5px 14px",
            fontSize: 13, color: c.pillText, marginBottom: 28, fontWeight: 500,
            transition: "background 0.4s ease, color 0.4s ease",
          }}>
            <span style={{ fontSize: 14 }}>✦</span> A calm way to stay on track
          </div>

          <h1 style={{
            fontFamily: "'Playfair Display', serif",
            fontSize: "clamp(36px, 5vw, 56px)", fontWeight: 600,
            color: c.headingMain, lineHeight: 1.15, margin: "0 0 20px",
            letterSpacing: "-0.5px", transition: "color 0.4s ease",
          }}>
            Plan Your Day<br />
            <span style={{ color: c.headingAccent, transition: "color 0.4s ease" }}>with TaskWise</span>
          </h1>

          <p style={{
            fontSize: 16, color: c.bodyText, lineHeight: 1.75,
            margin: "0 0 36px", maxWidth: 420, fontWeight: 300,
            transition: "color 0.4s ease",
          }}>
            Create tasks, set deadlines, and keep your week organized with a clean calendar, journal, and gentle reminders.
          </p>

          {/* Feature pills */}
          <div style={{ display: "flex", flexWrap: "wrap", gap: 10, marginBottom: 40 }}>
            {[
              { icon: "⚡", label: "Fast Setup" },
              { icon: "📅", label: "Calendar View" },
              { icon: "🔔", label: "Smart Reminders" },
            ].map(f => (
              <div key={f.label} style={{
                display: "flex", alignItems: "center", gap: 7,
                background: c.cardBg, border: `1px solid ${c.cardBorder}`,
                borderRadius: 50, padding: "7px 16px",
                fontSize: 13, color: c.pillText, fontWeight: 400,
                transition: "all 0.4s ease",
              }}>
                <span style={{ fontSize: 14 }}>{f.icon}</span> {f.label}
              </div>
            ))}
          </div>

          <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
            <button
              onClick={() => navigate("/signup")}
              style={{
                padding: "12px 30px", borderRadius: 50, border: "none",
                background: c.accent, color: "#fff", cursor: "pointer",
                fontSize: 15, fontFamily: "inherit", fontWeight: 500,
                transition: "all 0.2s",
              }}
              onMouseEnter={e => { e.currentTarget.style.background = c.accentHover; e.currentTarget.style.transform = "translateY(-1px)"; }}
              onMouseLeave={e => { e.currentTarget.style.background = c.accent; e.currentTarget.style.transform = "translateY(0)"; }}
            >
              Create Account
            </button>
            <button
              style={{
                padding: "12px 30px", borderRadius: 50,
                border: `1.5px solid ${c.accent}`, background: "transparent",
                color: c.logoText, cursor: "pointer",
                fontSize: 15, fontFamily: "inherit", fontWeight: 400,
                transition: "all 0.2s",
              }}
              onMouseEnter={e => { e.currentTarget.style.background = c.accentLight; }}
              onMouseLeave={e => { e.currentTarget.style.background = "transparent"; }}
            >
              Contact Admin
            </button>
          </div>
          <p style={{ marginTop: 14, fontSize: 12, color: c.mutedText, transition: "color 0.4s ease" }}>
            Sign up takes under a minute.
          </p>
        </div>

        {/* Right — Quick Glance Card */}
        <div style={{
          background: c.cardBg, borderRadius: 20, padding: "28px",
          border: `1px solid ${c.cardBorder}`,
          opacity: visible ? 1 : 0, transform: visible ? "translateY(0)" : "translateY(32px)",
          transition: "opacity 0.9s ease 0.2s, transform 0.9s ease 0.2s, background 0.4s ease, border-color 0.4s ease",
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <div style={{
                width: 38, height: 38, borderRadius: 10,
                background: c.tagBg, display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 18, transition: "background 0.4s ease",
              }}>📋</div>
              <div>
                <p style={{ margin: 0, fontWeight: 500, fontSize: 15, color: c.headingMain, transition: "color 0.4s ease" }}>Today</p>
                <p style={{ margin: 0, fontSize: 12, color: c.mutedText, transition: "color 0.4s ease" }}>Quick glance</p>
              </div>
            </div>
            <span style={{
              background: c.tagBg, color: c.tagText, fontSize: 12,
              padding: "4px 12px", borderRadius: 50, fontWeight: 500,
              transition: "all 0.4s ease",
            }}>3 Tasks</span>
          </div>

          {[
            { icon: "✅", text: "Finish activity plan" },
            { icon: "🕐", text: "Review upcoming deadlines" },
            { icon: "🔔", text: "Set reminder for tomorrow" },
          ].map((item, i) => (
            <div key={i} style={{
              display: "flex", alignItems: "center", gap: 12,
              padding: "11px 0",
              borderBottom: i < 2 ? `1px solid ${c.cardBorder}` : "none",
              opacity: visible ? 1 : 0,
              transition: `opacity 0.6s ease ${0.3 + i * 0.12}s, border-color 0.4s ease`,
            }}>
              <span style={{ fontSize: 16 }}>{item.icon}</span>
              <span style={{ fontSize: 14, color: c.bodyText, fontWeight: 400, transition: "color 0.4s ease" }}>
                {item.text}
              </span>
            </div>
          ))}

          <div style={{
            marginTop: 18, paddingTop: 16, borderTop: `1px solid ${c.cardBorder}`,
            display: "flex", justifyContent: "space-between", alignItems: "center",
            transition: "border-color 0.4s ease",
          }}>
            <span style={{ fontSize: 13, color: c.mutedText, transition: "color 0.4s ease" }}>Next reminder</span>
            <span style={{ fontSize: 14, fontWeight: 500, color: c.logoText, transition: "color 0.4s ease" }}>9:00 AM</span>
          </div>
        </div>
      </section>

      {/* Features */}
      <section style={{
        position: "relative", zIndex: 1,
        maxWidth: 1100, margin: "0 auto", padding: "40px 2.5rem 80px",
        opacity: visible ? 1 : 0,
        transition: "opacity 1s ease 0.4s",
      }}>
        <p style={{
          fontSize: 12, letterSpacing: "2px", color: c.mutedText,
          textTransform: "uppercase", marginBottom: 24, fontWeight: 500,
          transition: "color 0.4s ease",
        }}>What You Get</p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16 }}>
          {[
            { icon: "✓",  title: "Task Management", desc: "Keep your plans simple and easy to follow." },
            { icon: "📅", title: "Calendar View",    desc: "See deadlines without digging through pages." },
            { icon: "🔔", title: "Smart Reminders",  desc: "Stay notified so you do not miss tasks." },
            { icon: "📓", title: "Daily Journal",    desc: "Reflect on your day with mood tracking." },
          ].map((f, i) => (
            <div key={i}
              style={{
                background: c.cardBg, borderRadius: 16, padding: "22px",
                border: `1px solid ${c.cardBorder}`,
                transition: "transform 0.2s, background 0.4s ease, border-color 0.4s ease",
              }}
              onMouseEnter={e => { e.currentTarget.style.transform = "translateY(-3px)"; }}
              onMouseLeave={e => { e.currentTarget.style.transform = "translateY(0)"; }}
            >
              <div style={{
                width: 40, height: 40, borderRadius: 10,
                background: c.tagBg, display: "flex", alignItems: "center",
                justifyContent: "center", fontSize: 18, marginBottom: 14,
                transition: "background 0.4s ease",
              }}>{f.icon}</div>
              <p style={{ margin: "0 0 6px", fontWeight: 500, fontSize: 15, color: c.headingMain, transition: "color 0.4s ease" }}>
                {f.title}
              </p>
              <p style={{ margin: 0, fontSize: 13, color: c.mutedText, lineHeight: 1.6, fontWeight: 300, transition: "color 0.4s ease" }}>
                {f.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer style={{
        borderTop: `1px solid ${c.cardBorder}`, padding: "20px 2.5rem",
        textAlign: "center", fontSize: 12, color: c.mutedText,
        transition: "border-color 0.4s ease, color 0.4s ease",
      }}>
        TaskWise keeps your day clear and organized.
      </footer>
    </div>
  );
}
