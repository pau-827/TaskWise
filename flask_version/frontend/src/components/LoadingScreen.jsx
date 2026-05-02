import { useEffect, useState, useContext } from "react";
import { ThemeContext } from "../context/ThemeContext";
import { THEMES } from "../theme/themes";

export default function LoadingScreen({ onFinish }) {
  const { themeName } = useContext(ThemeContext);
  const c = THEMES[themeName]?.custom?.landing ?? THEMES.light.custom.landing;

  const [progress, setProgress] = useState(0);
  const [fadeOut, setFadeOut] = useState(false);

  useEffect(() => {
    const duration = 5000;
    const interval = 40;
    const steps = duration / interval;
    let current = 0;

    const timer = setInterval(() => {
      current += 1;
      const eased = Math.min(100, Math.round((1 - Math.pow(1 - current / steps, 2.5)) * 100));
      setProgress(eased);

      if (current >= steps) {
        clearInterval(timer);
        setFadeOut(true);
        setTimeout(() => onFinish(), 600);
      }
    }, interval);

    return () => clearInterval(timer);
  }, [onFinish]);

  const tips = [
    "Organizing your tasks...",
    "Setting up your calendar...",
    "Loading your journal...",
    "Almost ready...",
  ];
  const tip = tips[Math.min(Math.floor((progress / 100) * tips.length), tips.length - 1)];

  return (
    <div style={{
      position: "fixed", inset: 0, zIndex: 9999,
      background: c.pageBg,
      display: "flex", flexDirection: "column",
      alignItems: "center", justifyContent: "center",
      fontFamily: "'DM Sans', sans-serif",
      opacity: fadeOut ? 0 : 1,
      transition: "opacity 0.6s ease, background 0.4s ease",
    }}>
      <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&family=Playfair+Display:wght@500;600&display=swap" rel="stylesheet" />

      <style>{`
        @keyframes floatLogo {
          0%, 100% { transform: translateY(0px); }
          50%       { transform: translateY(-6px); }
        }
      `}</style>

      {/* Blobs */}
      <div style={{
        position: "absolute", top: -100, right: -80, width: 380, height: 380,
        borderRadius: "50%", background: c.blobColor, pointerEvents: "none",
        transition: "background 0.4s ease",
      }} />
      <div style={{
        position: "absolute", bottom: -80, left: -80, width: 280, height: 280,
        borderRadius: "50%", background: c.blobColor2, pointerEvents: "none",
        transition: "background 0.4s ease",
      }} />

      {/* Logo */}
      <div style={{ marginBottom: 48, textAlign: "center", animation: "floatLogo 3s ease-in-out infinite" }}>
        <div style={{
          width: 72, height: 72, borderRadius: 20,
          background: c.iconBg, margin: "0 auto 18px",
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: 32, color: "#fff",
          transition: "background 0.4s ease",
        }}>✓</div>

        <h1 style={{
          fontFamily: "'Playfair Display', serif",
          fontSize: 36, fontWeight: 600,
          color: c.headingMain, margin: 0, letterSpacing: "-0.5px",
          transition: "color 0.4s ease",
        }}>TaskWise</h1>
        <p style={{ margin: "6px 0 0", fontSize: 14, color: c.mutedText, fontWeight: 300, transition: "color 0.4s ease" }}>
          A calm way to stay on track
        </p>
      </div>

      {/* Progress bar */}
      <div style={{ width: 260, marginBottom: 16 }}>
        <div style={{ height: 4, background: c.progressBg, borderRadius: 100, overflow: "hidden", transition: "background 0.4s ease" }}>
          <div style={{
            height: "100%", width: `${progress}%`,
            background: c.progressBar,
            borderRadius: 100,
            transition: "width 0.04s linear",
          }} />
        </div>
        <div style={{
          display: "flex", justifyContent: "space-between",
          marginTop: 8, fontSize: 12, color: c.mutedText, transition: "color 0.4s ease",
        }}>
          <span>{tip}</span>
          <span>{progress}%</span>
        </div>
      </div>

      {/* Dots */}
      <div style={{ display: "flex", gap: 6, marginTop: 8 }}>
        {[0, 1, 2].map(i => (
          <div key={i} style={{
            width: 6, height: 6, borderRadius: "50%",
            background: progress > (i + 1) * 25 ? c.accent : c.progressBg,
            transition: "background 0.4s",
          }} />
        ))}
      </div>
    </div>
  );
}
