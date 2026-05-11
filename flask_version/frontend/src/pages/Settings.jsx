import { useState, useContext } from "react";
import {
  Box, Paper, Typography, Avatar, Select, MenuItem,
  IconButton, Dialog, DialogTitle, DialogContent, DialogActions,
  Button, TextField, Alert, Snackbar, CircularProgress, Chip,
} from "@mui/material";
import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import LockIcon from "@mui/icons-material/Lock";
import DeleteIcon from "@mui/icons-material/Delete";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import PaletteIcon from "@mui/icons-material/Palette";
import BugReportIcon from "@mui/icons-material/BugReport";
import SupportAgentIcon from "@mui/icons-material/SupportAgent";
import InfoIcon from "@mui/icons-material/Info";
import { useNavigate } from "react-router-dom";
import { AppContext } from "../context/AppContext";
import { ThemeContext } from "../context/ThemeContext";
import { THEMES } from "../theme/themes";
import { supabase } from "../services/supabase";

const THEME_OPTIONS = [
  { value: "light", label: "Light Mode", color: "#E3F4F4" },
  { value: "dark", label: "Dark Mode", color: "#1f2937" },
  { value: "pink", label: "Pink Mode", color: "#ffd1dc" },
];

export default function Settings() {
  const navigate = useNavigate();
  const { user, logout } = useContext(AppContext);
  const { themeName, setThemeName } = useContext(ThemeContext);

  const palette = THEMES[themeName]?.palette;
  const isDark = palette?.mode === "dark";
  const bgPaper = palette?.background?.paper ?? "#E3F4F4";
  const primary = palette?.primary?.main ?? "#4A707A";
  const textMain = palette?.text?.primary ?? "#1a3a40";
  const textMuted = palette?.text?.secondary ?? "#4A707A";
  const borderCol = isDark ? "rgba(255,255,255,0.12)" : "rgba(0,0,0,0.08)";
  const rowBg = isDark ? "rgba(255,255,255,0.06)" : "rgba(255,255,255,0.7)";

  const displayName = user?.user_metadata?.display_name || user?.email?.split("@")[0] || "User";
  const email = user?.email || "";
  const initials = displayName.slice(0, 2).toUpperCase();

  const [profileOpen, setProfileOpen] = useState(false);
  const [passwordOpen, setPasswordOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [reportOpen, setReportOpen] = useState(false);

  const [newName, setNewName] = useState(displayName);
  const [nameLoading, setNameLoading] = useState(false);
  const [nameError, setNameError] = useState("");
  const [nameSuccess, setNameSuccess] = useState("");

  const [newPass, setNewPass] = useState("");
  const [confirmPass, setConfirmPass] = useState("");
  const [passLoading, setPassLoading] = useState(false);
  const [passError, setPassError] = useState("");
  const [passSuccess, setPassSuccess] = useState("");

  const [deleteConfirm, setDeleteConfirm] = useState("");
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [deleteError, setDeleteError] = useState("");

  const [issueTitle, setIssueTitle] = useState("");
  const [issueType, setIssueType] = useState("UI Issue");
  const [issueDescription, setIssueDescription] = useState("");
  const [issueLoading, setIssueLoading] = useState(false);

  const [snack, setSnack] = useState({ open: false, msg: "", severity: "success" });
  const showSnack = (msg, severity = "success") => setSnack({ open: true, msg, severity });

  const mainShadow = isDark ? "0 10px 30px rgba(0,0,0,0.35)" : "0 10px 30px rgba(0,0,0,0.08)";

  const handleUpdateName = async () => {
    if (!newName.trim()) {
      setNameError("Name cannot be empty.");
      return;
    }

    setNameLoading(true);
    setNameError("");

    const { error } = await supabase.auth.updateUser({
      data: { display_name: newName.trim() },
    });

    if (error) {
      setNameError(error.message);
    } else {
      setNameSuccess("Display name updated!");
      showSnack("Profile updated.");
      setTimeout(() => setProfileOpen(false), 1000);
    }

    setNameLoading(false);
  };

  const handleUpdatePassword = async () => {
    if (newPass.length < 6) {
      setPassError("Password must be at least 6 characters.");
      return;
    }

    if (newPass !== confirmPass) {
      setPassError("Passwords do not match.");
      return;
    }

    setPassLoading(true);
    setPassError("");

    const { error } = await supabase.auth.updateUser({ password: newPass });

    if (error) {
      setPassError(error.message);
    } else {
      setPassSuccess("Password updated!");
      setNewPass("");
      setConfirmPass("");
      showSnack("Password updated.");
      setTimeout(() => setPasswordOpen(false), 1000);
    }

    setPassLoading(false);
  };

  const handleDeleteAccount = async () => {
    if (deleteConfirm !== "DELETE") {
      setDeleteError('Type "DELETE" to confirm.');
      return;
    }

    setDeleteLoading(true);

    await supabase.from("tasks").delete().eq("user_id", user.id);
    await supabase.from("journal_entries").delete().eq("user_id", user.id);
    await supabase.from("recipes").delete().eq("user_id", user.id);

    await logout();
    navigate("/");
  };

  const handleReportIssue = async () => {
    if (!issueTitle.trim() || !issueDescription.trim()) {
      showSnack("Please complete the issue title and description.", "warning");
      return;
    }

    setIssueLoading(true);

    const payload = {
      user_id: user?.id,
      email,
      issue_type: issueType,
      title: issueTitle.trim(),
      description: issueDescription.trim(),
      status: "open",
      created_at: new Date().toISOString(),
    };

    const { error } = await supabase.from("issue_reports").insert(payload);

    if (error) {
      showSnack("Issue report saved locally only. Check if issue_reports table exists.", "warning");
    } else {
      showSnack("Issue report submitted.");
    }

    setIssueTitle("");
    setIssueDescription("");
    setIssueType("UI Issue");
    setReportOpen(false);
    setIssueLoading(false);
  };

  const SettingRow = ({ icon, title, subtitle, onClick, danger }) => (
    <Box
      onClick={onClick}
      sx={{
        display: "flex",
        alignItems: "center",
        gap: 2,
        p: 2,
        borderRadius: 3,
        bgcolor: rowBg,
        border: `1px solid ${danger ? "#e5393544" : borderCol}`,
        cursor: onClick ? "pointer" : "default",
        transition: "all 0.25s ease",
        "&:hover": onClick
          ? {
              bgcolor: danger ? "#e5393511" : primary + "11",
              transform: "translateY(-3px) scale(1.01)",
              boxShadow: 2,
            }
          : {},
      }}
    >
      <Box
        sx={{
          width: 44,
          height: 44,
          borderRadius: 3,
          bgcolor: danger ? "#e5393522" : primary + "22",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: danger ? "#e53935" : primary,
          flexShrink: 0,
        }}
      >
        {icon}
      </Box>

      <Box sx={{ flex: 1 }}>
        <Typography fontWeight={700} fontSize={14} color={danger ? "#e53935" : textMain}>
          {title}
        </Typography>
        <Typography variant="caption" color={textMuted}>
          {subtitle}
        </Typography>
      </Box>

      {onClick && <ChevronRightIcon sx={{ color: textMuted, fontSize: 20 }} />}
    </Box>
  );

  return (
    <Box sx={{ width: "100%", display: "flex", flexDirection: { xs: "column", lg: "row" }, gap: 3, alignItems: "stretch" }}>
      <Box sx={{ flex: "1 1 0", minWidth: 0 }}>
        <Paper sx={{ p: 3, borderRadius: 5, bgcolor: bgPaper, minHeight: "calc(100vh - 140px)", boxShadow: mainShadow }}>
          <Typography variant="h5" fontWeight={800} mb={3} color={textMain} sx={{ fontFamily: "'Playfair Display', serif" }}>
            Settings
          </Typography>

          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              gap: 2,
              p: 3,
              borderRadius: 4,
              bgcolor: isDark ? "linear-gradient(135deg,#1f2937,#111827)" : primary + "12",
              border: `1px solid ${borderCol}`,
              mb: 3,
              position: "relative",
              overflow: "hidden",
            }}
          >
            <Box sx={{ position: "absolute", right: -35, top: -35, width: 120, height: 120, borderRadius: "50%", bgcolor: primary + "22" }} />

            <Avatar sx={{ width: 64, height: 64, bgcolor: primary, fontSize: 22, fontWeight: 800, boxShadow: `0 0 20px ${primary}55` }}>
              {initials}
            </Avatar>

            <Box sx={{ flex: 1, position: "relative", zIndex: 1 }}>
              <Typography fontWeight={800} fontSize={18} color={textMain}>
                {displayName}
              </Typography>
              <Typography variant="caption" color={textMuted}>
                {email}
              </Typography>
            </Box>

            <Chip label="Active" size="small" sx={{ bgcolor: primary + "22", color: primary, fontWeight: 700 }} />
          </Box>

          <Typography variant="overline" color={textMuted} fontWeight={800} letterSpacing={1.5} display="block" mb={1}>
            Preferences
          </Typography>

          <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5, mb: 3 }}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 2, p: 2, borderRadius: 3, bgcolor: rowBg, border: `1px solid ${borderCol}` }}>
              <Box sx={{ width: 44, height: 44, borderRadius: 3, bgcolor: primary + "22", display: "flex", alignItems: "center", justifyContent: "center", color: primary, flexShrink: 0 }}>
                <PaletteIcon />
              </Box>

              <Box sx={{ flex: 1 }}>
                <Typography fontWeight={700} fontSize={14} color={textMain}>
                  Theme
                </Typography>
                <Typography variant="caption" color={textMuted}>
                  Switch your look and feel
                </Typography>
              </Box>

              <Select value={themeName} onChange={(e) => setThemeName(e.target.value)} size="small" sx={{ borderRadius: 3, minWidth: 170, fontSize: 14, fontWeight: 700, bgcolor: rowBg, boxShadow: "0 4px 12px rgba(0,0,0,0.08)", ".MuiOutlinedInput-notchedOutline": { borderColor: borderCol } }}>
                {THEME_OPTIONS.map((o) => (
                  <MenuItem key={o.value} value={o.value}>
                    {o.label}
                  </MenuItem>
                ))}
              </Select>
            </Box>

            <Box sx={{ display: "flex", gap: 2 }}>
              {THEME_OPTIONS.map((t) => (
                <Box
                  key={t.value}
                  onClick={() => setThemeName(t.value)}
                  sx={{
                    flex: 1,
                    height: 74,
                    borderRadius: 3,
                    bgcolor: t.color,
                    border: `3px solid ${themeName === t.value ? primary : borderCol}`,
                    cursor: "pointer",
                    transition: "all 0.2s ease",
                    display: "flex",
                    alignItems: "end",
                    p: 1,
                    "&:hover": { transform: "scale(1.04)", boxShadow: 3 },
                  }}
                >
                  <Typography fontSize={11} fontWeight={800} sx={{ color: t.value === "dark" ? "#fff" : "#1f2937" }}>
                    {t.label}
                  </Typography>
                </Box>
              ))}
            </Box>
          </Box>

          <Typography variant="overline" color={textMuted} fontWeight={800} letterSpacing={1.5} display="block" mb={1}>
            Account
          </Typography>

          <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5, mb: 3 }}>
            <SettingRow icon={<AccountCircleIcon />} title="Account" subtitle="View and edit profile information" onClick={() => { setNewName(displayName); setNameError(""); setNameSuccess(""); setProfileOpen(true); }} />
            <SettingRow icon={<LockIcon />} title="Change Password" subtitle="Update your account password" onClick={() => { setNewPass(""); setConfirmPass(""); setPassError(""); setPassSuccess(""); setPasswordOpen(true); }} />
            <SettingRow icon={<DeleteIcon />} title="Delete Account" subtitle="Permanently delete your account and data" onClick={() => { setDeleteConfirm(""); setDeleteError(""); setDeleteOpen(true); }} danger />
          </Box>

          <Typography variant="overline" color={textMuted} fontWeight={800} letterSpacing={1.5} display="block" mb={1}>
            Support
          </Typography>

          <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5 }}>
            <SettingRow icon={<BugReportIcon />} title="Report Issue" subtitle="Send a bug report or UI problem" onClick={() => setReportOpen(true)} />
            <SettingRow icon={<SupportAgentIcon />} title="Contact Support" subtitle="Ask for help with TaskWise features" onClick={() => showSnack("Support feature coming soon.", "info")} />
          </Box>
        </Paper>
      </Box>

      <Box sx={{ flex: { xs: "1 1 auto", lg: "0 0 360px" }, display: "flex", flexDirection: "column" }}>
        <Paper sx={{ p: 3, borderRadius: 5, bgcolor: bgPaper, minHeight: "calc(100vh - 95px)", boxShadow: mainShadow }}>
          <Typography variant="h6" fontWeight={800} mb={2.5} color={textMain} sx={{ fontFamily: "'Playfair Display', serif" }}>
            Quick Tips
          </Typography>

          <Box sx={{ borderRadius: 3, bgcolor: rowBg, border: `1px solid ${borderCol}`, overflow: "hidden", backdropFilter: "blur(12px)" }}>
            {[
              { icon: "💡", tip: "Theme changes apply instantly." },
              { icon: "🔒", tip: "Use a strong password." },
              { icon: "📅", tip: "Set due dates so tasks appear on the calendar." },
              { icon: "📓", tip: "Write in your journal daily for mood tracking." },
              { icon: "⚡", tip: "Use categories to keep tasks organized." },
              { icon: "🔔", tip: "Set reminders so you never miss a deadline." },
            ].map((t, i, arr) => (
              <Box key={i} sx={{ display: "flex", alignItems: "flex-start", gap: 1.5, p: 2, borderBottom: i < arr.length - 1 ? `1px solid ${borderCol}` : "none", transition: "all 0.2s ease", "&:hover": { bgcolor: primary + "10", transform: "translateX(4px)" } }}>
                <Typography fontSize={20} lineHeight={1.3}>
                  {t.icon}
                </Typography>
                <Typography fontSize={13} color={textMuted} lineHeight={1.6}>
                  {t.tip}
                </Typography>
              </Box>
            ))}
          </Box>

          <Box sx={{ mt: 3, p: 2.5, borderRadius: 3, bgcolor: isDark ? "rgba(255,255,255,0.05)" : primary + "10", border: `1px solid ${primary}22`, backdropFilter: "blur(10px)", boxShadow: "0 6px 20px rgba(0,0,0,0.08)" }}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}>
              <InfoIcon sx={{ color: primary, fontSize: 18 }} />
              <Typography fontSize={13} color={primary} fontWeight={800}>
                TaskWise
              </Typography>
            </Box>
            <Typography fontSize={12} color={textMuted}>
              Flask + React + Supabase
            </Typography>
            <Typography fontSize={12} color={textMuted}>
              Version 1.0.0 — Flask Version
            </Typography>
          </Box>
        </Paper>
      </Box>

      <Dialog open={profileOpen} onClose={() => setProfileOpen(false)} maxWidth="xs" fullWidth PaperProps={{ sx: { borderRadius: 4 } }}>
        <DialogTitle sx={{ fontWeight: 800, fontFamily: "'Playfair Display', serif" }}>Edit Profile</DialogTitle>
        <DialogContent sx={{ display: "flex", flexDirection: "column", gap: 2, pt: "12px !important" }}>
          <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 1, mb: 1 }}>
            <Avatar sx={{ width: 70, height: 70, bgcolor: primary, fontSize: 24, fontWeight: 800 }}>{initials}</Avatar>
            <Typography variant="caption" color={textMuted}>{email}</Typography>
          </Box>
          {nameError && <Alert severity="error" sx={{ borderRadius: 2 }}>{nameError}</Alert>}
          {nameSuccess && <Alert severity="success" sx={{ borderRadius: 2 }}>{nameSuccess}</Alert>}
          <TextField label="Display Name" fullWidth value={newName} onChange={(e) => setNewName(e.target.value)} sx={{ "& .MuiOutlinedInput-root": { borderRadius: 3 } }} />
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3, gap: 1 }}>
          <Button onClick={() => setProfileOpen(false)} sx={{ borderRadius: 50 }}>Cancel</Button>
          <Button onClick={handleUpdateName} variant="contained" disabled={nameLoading} sx={{ borderRadius: 50, px: 3 }}>
            {nameLoading ? <CircularProgress size={18} color="inherit" /> : "Save"}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={passwordOpen} onClose={() => setPasswordOpen(false)} maxWidth="xs" fullWidth PaperProps={{ sx: { borderRadius: 4 } }}>
        <DialogTitle sx={{ fontWeight: 800, fontFamily: "'Playfair Display', serif" }}>Change Password</DialogTitle>
        <DialogContent sx={{ display: "flex", flexDirection: "column", gap: 2, pt: "12px !important" }}>
          {passError && <Alert severity="error" sx={{ borderRadius: 2 }}>{passError}</Alert>}
          {passSuccess && <Alert severity="success" sx={{ borderRadius: 2 }}>{passSuccess}</Alert>}
          <TextField label="New Password" type="password" fullWidth value={newPass} onChange={(e) => setNewPass(e.target.value)} sx={{ "& .MuiOutlinedInput-root": { borderRadius: 3 } }} />
          <TextField label="Confirm Password" type="password" fullWidth value={confirmPass} onChange={(e) => setConfirmPass(e.target.value)} sx={{ "& .MuiOutlinedInput-root": { borderRadius: 3 } }} />
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3, gap: 1 }}>
          <Button onClick={() => setPasswordOpen(false)} sx={{ borderRadius: 50 }}>Cancel</Button>
          <Button onClick={handleUpdatePassword} variant="contained" disabled={passLoading} sx={{ borderRadius: 50, px: 3 }}>
            {passLoading ? <CircularProgress size={18} color="inherit" /> : "Update"}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={reportOpen} onClose={() => setReportOpen(false)} maxWidth="sm" fullWidth PaperProps={{ sx: { borderRadius: 4 } }}>
        <DialogTitle sx={{ fontWeight: 800, fontFamily: "'Playfair Display', serif" }}>Report Issue</DialogTitle>
        <DialogContent sx={{ display: "flex", flexDirection: "column", gap: 2, pt: "12px !important" }}>
          <Select value={issueType} onChange={(e) => setIssueType(e.target.value)} fullWidth sx={{ borderRadius: 3 }}>
            <MenuItem value="UI Issue">UI Issue</MenuItem>
            <MenuItem value="Bug">Bug</MenuItem>
            <MenuItem value="Performance">Performance</MenuItem>
            <MenuItem value="Feature Request">Feature Request</MenuItem>
            <MenuItem value="Other">Other</MenuItem>
          </Select>
          <TextField label="Issue Title" fullWidth value={issueTitle} onChange={(e) => setIssueTitle(e.target.value)} sx={{ "& .MuiOutlinedInput-root": { borderRadius: 3 } }} />
          <TextField label="Describe the issue" fullWidth multiline rows={5} value={issueDescription} onChange={(e) => setIssueDescription(e.target.value)} sx={{ "& .MuiOutlinedInput-root": { borderRadius: 3 } }} />
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3, gap: 1 }}>
          <Button onClick={() => setReportOpen(false)} sx={{ borderRadius: 50 }}>Cancel</Button>
          <Button onClick={handleReportIssue} variant="contained" disabled={issueLoading} startIcon={<BugReportIcon />} sx={{ borderRadius: 50, px: 3 }}>
            {issueLoading ? "Sending..." : "Submit"}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={deleteOpen} onClose={() => setDeleteOpen(false)} maxWidth="xs" fullWidth PaperProps={{ sx: { borderRadius: 4 } }}>
        <DialogTitle sx={{ fontWeight: 800, fontFamily: "'Playfair Display', serif", color: "#e53935" }}>Delete Account</DialogTitle>
        <DialogContent sx={{ display: "flex", flexDirection: "column", gap: 2, pt: "12px !important" }}>
          <Alert severity="error" sx={{ borderRadius: 2 }}>This will delete your local app data. Account deletion requires admin access.</Alert>
          {deleteError && <Alert severity="warning" sx={{ borderRadius: 2 }}>{deleteError}</Alert>}
          <Typography fontSize={13} color={textMuted}>Type <strong>DELETE</strong> below to confirm:</Typography>
          <TextField fullWidth placeholder="DELETE" value={deleteConfirm} onChange={(e) => setDeleteConfirm(e.target.value)} sx={{ "& .MuiOutlinedInput-root": { borderRadius: 3 } }} />
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3, gap: 1 }}>
          <Button onClick={() => setDeleteOpen(false)} sx={{ borderRadius: 50 }}>Cancel</Button>
          <Button onClick={handleDeleteAccount} variant="contained" disabled={deleteLoading} sx={{ borderRadius: 50, px: 3, bgcolor: "#e53935", "&:hover": { bgcolor: "#c62828" } }}>
            {deleteLoading ? <CircularProgress size={18} color="inherit" /> : "Delete Forever"}
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar open={snack.open} autoHideDuration={3000} onClose={() => setSnack((s) => ({ ...s, open: false }))} anchorOrigin={{ vertical: "bottom", horizontal: "right" }}>
        <Alert severity={snack.severity} sx={{ borderRadius: 2 }} onClose={() => setSnack((s) => ({ ...s, open: false }))}>
          {snack.msg}
        </Alert>
      </Snackbar>
    </Box>
  );
}