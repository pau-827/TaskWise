import { useEffect, useState, useContext } from "react";
import { Box, Paper, Typography, Avatar, Button, Chip } from "@mui/material";
import EmailIcon from "@mui/icons-material/Email";
import { useNavigate } from "react-router-dom";
import { ThemeContext } from "../context/ThemeContext";
import { THEMES } from "../theme/themes";

const SQUAD_EMAIL = "dueitsquad.taskwise@gmail.com";

const admins = [
  {
    name: "Ayelyn Panliboton",
    role: "Developer",
    email: "aypanliboton@my.cspc.edu.ph",
    image: "/admin-ayelyn.jpg",
  },
  {
    name: "Ivy Pauline Muit",
    role: "Developer",
    email: "ivmuit@my.cspc.edu.ph",
    image: "/admin-ivy.jpg",
  },
  {
    name: "Rhea Lizza Sangurl",
    role: "Developer",
    email: "rhsanglay@my.cspc.edu.ph",
    image: "/admin-rhea.jpg",
  },
];

export default function ContactAdmin() {
  const navigate = useNavigate();
  const { themeName } = useContext(ThemeContext);
  const c = THEMES[themeName]?.custom?.landing ?? THEMES.light.custom.landing;

  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const t = setTimeout(() => setVisible(true), 100);
    return () => clearTimeout(t);
  }, []);

  return (
    <Box sx={{
      minHeight: "100vh",
      background: c.pageBg,
      px: { xs: 2, md: 6 },
      py: 4,
      position: "relative",
      overflowX: "hidden",
      transition: "background 0.4s ease",
      fontFamily: "'DM Sans', sans-serif",
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

      {/* Blobs — same as LandingPage */}
      <Box sx={{
        position: "fixed", width: 420, height: 420, borderRadius: "50%",
        background: c.blobColor, zIndex: 0, pointerEvents: "none",
        animation: "blobTopRight 1.2s cubic-bezier(0.22,1,0.36,1) forwards",
        transition: "background 0.4s ease",
      }} />
      <Box sx={{
        position: "fixed", width: 300, height: 300, borderRadius: "50%",
        background: c.blobColor2, zIndex: 0, pointerEvents: "none",
        animation: "blobBottomLeft 1.4s cubic-bezier(0.22,1,0.36,1) 0.1s forwards",
        transition: "background 0.4s ease",
      }} />
      <Box sx={{
        position: "fixed", width: 200, height: 200, borderRadius: "50%",
        background: c.blobColor3, zIndex: 0, pointerEvents: "none",
        animation: "blobTopLeft 1.6s cubic-bezier(0.22,1,0.36,1) 0.2s forwards",
        transition: "background 0.4s ease",
      }} />

      {/* Content */}
      <Box sx={{ position: "relative", zIndex: 1 }}>

        {/* Header */}
        <Box sx={{
          textAlign: "center", mb: 5,
          opacity: visible ? 1 : 0, transform: visible ? "translateY(0)" : "translateY(24px)",
          transition: "opacity 0.7s ease, transform 0.7s ease",
        }}>
          <Typography variant="h3" fontWeight={800} sx={{
            fontFamily: "'Playfair Display', serif",
            color: c.headingMain,
          }}>
            Due-It Squad
          </Typography>
          <Typography mt={1} sx={{ color: c.bodyText, fontSize: 15 }}>
            Reach out to the TaskWise team for account, task, or system support.
          </Typography>
        </Box>

        {/* Squad email banner */}
        <Box sx={{
          maxWidth: 520, mx: "auto", mb: 5,
          opacity: visible ? 1 : 0, transform: visible ? "translateY(0)" : "translateY(24px)",
          transition: "opacity 0.8s ease 0.1s, transform 0.8s ease 0.1s",
        }}>
          <Paper sx={{
            p: 3, borderRadius: 5, textAlign: "center",
            bgcolor: c.cardBg, border: `1px solid ${c.cardBorder}`,
            boxShadow: "0 10px 30px rgba(0,0,0,0.08)",
            transition: "background 0.4s ease",
          }}>
            <Typography fontSize={13} fontWeight={500} letterSpacing={1}
              sx={{ textTransform: "uppercase", mb: 0.5, color: c.mutedText }}>
              General Inquiries
            </Typography>
            <Typography variant="h6" fontWeight={800} mb={0.5} sx={{ color: c.headingMain }}>
              📬 TaskWise Official
            </Typography>
            <Typography fontSize={13} mb={2} sx={{ color: c.bodyText }}>
              For general support, feedback, or anything that doesn't need a specific developer.
            </Typography>
            <Button
              component="a"
              href={`https://mail.google.com/mail/?view=cm&fs=1&to=${SQUAD_EMAIL}`}
              target="_blank" rel="noopener noreferrer"
              variant="contained" startIcon={<EmailIcon />}
              sx={{ borderRadius: 50, px: 3, bgcolor: c.accent,
                "&:hover": { bgcolor: c.accentHover } }}
            >
              Email the Squad
            </Button>
          </Paper>
        </Box>

        {/* Admin cards */}
        <Box sx={{
          display: "grid",
          gridTemplateColumns: { xs: "1fr", md: "repeat(3, 1fr)" },
          gap: 3, maxWidth: 1100, mx: "auto", mb: 6,
          opacity: visible ? 1 : 0, transform: visible ? "translateY(0)" : "translateY(24px)",
          transition: "opacity 0.9s ease 0.2s, transform 0.9s ease 0.2s",
        }}>
          {admins.map((admin) => (
            <Paper key={admin.name} sx={{
              p: 4, borderRadius: 5, textAlign: "center",
              bgcolor: c.cardBg, border: `1px solid ${c.cardBorder}`,
              boxShadow: "0 10px 30px rgba(0,0,0,0.08)", transition: "all 0.2s",
              "&:hover": { transform: "translateY(-6px)", boxShadow: "0 14px 35px rgba(0,0,0,0.12)" },
            }}>
              <Avatar src={admin.image} alt={admin.name} sx={{
                width: 110, height: 110, mx: "auto", mb: 2,
                border: `4px solid ${c.accent}`,
              }} />
              <Typography variant="h5" fontWeight={800} sx={{ color: c.headingMain }}>
                {admin.name}
              </Typography>
              <Chip label={admin.role} size="small" sx={{
                mt: 1, mb: 2, borderRadius: 50,
                bgcolor: c.accent, color: "#fff", fontWeight: 700,
              }} />
              <Typography fontSize={14} mb={3} sx={{ color: c.bodyText }}>
                Need help? Send a message directly to this developer.
              </Typography>
              <Button
                fullWidth component="a"
                href={`https://mail.google.com/mail/?view=cm&fs=1&to=${admin.email}`}
                target="_blank" rel="noopener noreferrer"
                variant="outlined" startIcon={<EmailIcon />}
                sx={{ borderRadius: 50, borderColor: c.accent, color: c.accent,
                  "&:hover": { borderColor: c.accentHover, bgcolor: c.accentLight } }}
              >
                Email {admin.name.split(" ")[0]}
              </Button>
            </Paper>
          ))}
        </Box>

        {/* Back button */}
        <Box sx={{ display: "flex", justifyContent: "center", mb: 5 }}>
          <Button
            onClick={() => navigate(-1)}
            sx={{
              borderRadius: 50, px: 4, py: 1.2, fontSize: 14,
              color: c.bodyText, border: `1px solid ${c.cardBorder}`,
              "&:hover": { bgcolor: c.accentLight, borderColor: c.accent },
            }}
          >
            ← Back
          </Button>
        </Box>

        {/* Footer */}
        <Box sx={{
          textAlign: "center", pb: 2,
          borderTop: `1px solid ${c.cardBorder}`, pt: 3,
          transition: "border-color 0.4s ease",
        }}>
          <Typography fontSize={12} sx={{ color: c.mutedText }}>
            © {new Date().getFullYear()} TaskWise · Due-It Squad · All rights reserved.
          </Typography>
        </Box>

      </Box>
    </Box>
  );
}