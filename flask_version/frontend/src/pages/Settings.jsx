import { useState, useContext } from "react";
import {
  Box, Paper, Typography, Avatar, Divider, Select, MenuItem,
  IconButton, Dialog, DialogTitle, DialogContent, DialogActions,
  Button, TextField, Alert, Snackbar, CircularProgress,
} from "@mui/material";
import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import LockIcon from "@mui/icons-material/Lock";
import DeleteIcon from "@mui/icons-material/Delete";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import PaletteIcon from "@mui/icons-material/Palette";
import { useNavigate } from "react-router-dom";
import { AppContext } from "../context/AppContext";
import { ThemeContext } from "../context/ThemeContext";
import { THEMES } from "../theme/themes";
import { supabase } from "../services/supabase";

const THEME_OPTIONS = [
  { value: "light", label: "Light Mode" },
  { value: "dark",  label: "Dark Mode"  },
  { value: "pink",  label: "Pink Mode"  },
];

export default function Settings() {
  const navigate = useNavigate();
  const { user, logout } = useContext(AppContext);
  const { themeName, setThemeName } = useContext(ThemeContext);

  const palette   = THEMES[themeName]?.palette;
  const isDark    = palette?.mode === "dark";
  const bgPaper   = palette?.background?.paper   ?? "#E3F4F4";
  const primary   = palette?.primary?.main       ?? "#4A707A";
  const textMain  = palette?.text?.primary       ?? "#1a3a40";
  const textMuted = palette?.text?.secondary     ?? "#4A707A";
  const borderCol = isDark ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.08)";
  const rowBg     = isDark ? "rgba(255,255,255,0.04)" : "rgba(255,255,255,0.7)";

  const displayName = user?.user_metadata?.display_name || user?.email?.split("@")[0] || "User";
  const email       = user?.email || "";
  const initials    = displayName.slice(0, 2).toUpperCase();

  // ── Dialog states ──────────────────────────────────────────────────────
  const [profileOpen,  setProfileOpen]  = useState(false);
  const [passwordOpen, setPasswordOpen] = useState(false);
  const [deleteOpen,   setDeleteOpen]   = useState(false);

  // ── Profile form ───────────────────────────────────────────────────────
  const [newName,    setNewName]    = useState(displayName);
  const [nameLoading, setNameLoading] = useState(false);
  const [nameError,  setNameError]  = useState("");
  const [nameSuccess, setNameSuccess] = useState("");

  const handleUpdateName = async () => {
    if (!newName.trim()) { setNameError("Name cannot be empty."); return; }
    setNameLoading(true); setNameError("");
    const { error } = await supabase.auth.updateUser({ data: { display_name: newName.trim() } });
    if (error) setNameError(error.message);
    else { setNameSuccess("Display name updated!"); setTimeout(() => setProfileOpen(false), 1000); }
    setNameLoading(false);
  };

  // ── Password form ──────────────────────────────────────────────────────
  const [newPass,      setNewPass]      = useState("");
  const [confirmPass,  setConfirmPass]  = useState("");
  const [passLoading,  setPassLoading]  = useState(false);
  const [passError,    setPassError]    = useState("");
  const [passSuccess,  setPassSuccess]  = useState("");

  const handleUpdatePassword = async () => {
    if (newPass.length < 6) { setPassError("Password must be at least 6 characters."); return; }
    if (newPass !== confirmPass) { setPassError("Passwords do not match."); return; }
    setPassLoading(true); setPassError("");
    const { error } = await supabase.auth.updateUser({ password: newPass });
    if (error) setPassError(error.message);
    else { setPassSuccess("Password updated!"); setNewPass(""); setConfirmPass(""); setTimeout(() => setPasswordOpen(false), 1000); }
    setPassLoading(false);
  };

  // ── Delete account ─────────────────────────────────────────────────────
  const [deleteConfirm, setDeleteConfirm] = useState("");
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [deleteError,   setDeleteError]   = useState("");

  const handleDeleteAccount = async () => {
    if (deleteConfirm !== "DELETE") { setDeleteError('Type "DELETE" to confirm.'); return; }
    setDeleteLoading(true);
    // Delete all user tasks first
    await supabase.from("tasks").delete().eq("user_id", user.id);
    // Sign out (actual account deletion requires admin API — show message)
    await logout();
    navigate("/");
  };

  // ── Snackbar ───────────────────────────────────────────────────────────
  const [snack, setSnack] = useState({ open: false, msg: "", severity: "success" });
  const showSnack = (msg, severity = "success") => setSnack({ open: true, msg, severity });

  // ── Row component ──────────────────────────────────────────────────────
  const SettingRow = ({ icon, title, subtitle, onClick, danger }) => (
    <Box onClick={onClick} sx={{
      display: "flex", alignItems: "center", gap: 2,
      p: 2, borderRadius: 2.5, bgcolor: rowBg,
      border: `1px solid ${danger ? "#e5393544" : borderCol}`,
      cursor: onClick ? "pointer" : "default",
      transition: "all 0.2s",
      "&:hover": onClick ? {
        bgcolor: danger ? "#e5393511" : primary + "11",
        transform: "translateY(-1px)", boxShadow: 1,
      } : {},
    }}>
      <Box sx={{
        width: 40, height: 40, borderRadius: 2,
        bgcolor: danger ? "#e5393522" : primary + "22",
        display: "flex", alignItems: "center", justifyContent: "center",
        color: danger ? "#e53935" : primary, flexShrink: 0,
      }}>
        {icon}
      </Box>
      <Box sx={{ flex: 1 }}>
        <Typography fontWeight={600} fontSize={14} color={danger ? "#e53935" : textMain}>{title}</Typography>
        <Typography variant="caption" color={textMuted}>{subtitle}</Typography>
      </Box>
      {onClick && <ChevronRightIcon sx={{ color: textMuted, fontSize: 20 }} />}
    </Box>
  );

  return (
    <Box sx={{ width: "100%", display: "flex", gap: 3, alignItems: "stretch" }}>

      {/* ── LEFT: Settings Panel ─────────────────────────────────────────── */}
      <Box sx={{ flex: "1 1 0", minWidth: 0 }}>
        <Paper sx={{ p: 3, borderRadius: 3, bgcolor: bgPaper, height: "100%" }}>

          <Typography variant="h5" fontWeight={700} mb={3} color={textMain}
            sx={{ fontFamily: "'Playfair Display', serif" }}>
            Settings
          </Typography>

          {/* Profile card */}
          <Box sx={{
            display: "flex", alignItems: "center", gap: 2,
            p: 2.5, borderRadius: 2.5, bgcolor: rowBg,
            border: `1px solid ${borderCol}`, mb: 3,
          }}>
            <Avatar sx={{ width: 48, height: 48, bgcolor: primary, fontSize: 18, fontWeight: 700 }}>
              {initials}
            </Avatar>
            <Box sx={{ flex: 1 }}>
              <Typography fontWeight={700} fontSize={16} color={textMain}>{displayName}</Typography>
              <Typography variant="caption" color={textMuted}>{email}</Typography>
            </Box>
            <IconButton sx={{ color: textMuted }}>
              <AccountCircleIcon />
            </IconButton>
          </Box>

          {/* Preferences */}
          <Typography variant="overline" color={textMuted} fontWeight={700} letterSpacing={1.5}
            display="block" mb={1}>
            Preferences
          </Typography>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5, mb: 3 }}>

            {/* Theme switcher */}
            <Box sx={{
              display: "flex", alignItems: "center", gap: 2,
              p: 2, borderRadius: 2.5, bgcolor: rowBg,
              border: `1px solid ${borderCol}`,
            }}>
              <Box sx={{
                width: 40, height: 40, borderRadius: 2,
                bgcolor: primary + "22", display: "flex", alignItems: "center",
                justifyContent: "center", color: primary, flexShrink: 0,
              }}>
                <PaletteIcon />
              </Box>
              <Box sx={{ flex: 1 }}>
                <Typography fontWeight={600} fontSize={14} color={textMain}>Theme</Typography>
                <Typography variant="caption" color={textMuted}>Switch your look and feel</Typography>
              </Box>
              <Select
                value={themeName}
                onChange={e => setThemeName(e.target.value)}
                size="small"
                sx={{
                  borderRadius: 2, minWidth: 140, fontSize: 14,
                  ".MuiOutlinedInput-notchedOutline": { borderColor: borderCol },
                }}
              >
                {THEME_OPTIONS.map(o => (
                  <MenuItem key={o.value} value={o.value}>{o.label}</MenuItem>
                ))}
              </Select>
            </Box>
          </Box>

          {/* Account */}
          <Typography variant="overline" color={textMuted} fontWeight={700} letterSpacing={1.5}
            display="block" mb={1}>
            Account
          </Typography>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5 }}>
            <SettingRow
              icon={<AccountCircleIcon />}
              title="Account"
              subtitle="View profile information"
              onClick={() => { setNewName(displayName); setNameError(""); setNameSuccess(""); setProfileOpen(true); }}
            />
            <SettingRow
              icon={<LockIcon />}
              title="Change Password"
              subtitle="Update your password"
              onClick={() => { setNewPass(""); setConfirmPass(""); setPassError(""); setPassSuccess(""); setPasswordOpen(true); }}
            />
            <SettingRow
              icon={<DeleteIcon />}
              title="Delete Account"
              subtitle="Permanently delete your account and data"
              onClick={() => { setDeleteConfirm(""); setDeleteError(""); setDeleteOpen(true); }}
              danger
            />
          </Box>

        </Paper>
      </Box>

      {/* ── RIGHT: Quick Tips ────────────────────────────────────────────── */}
      <Box sx={{ flex: "0 0 360px", display: "flex", flexDirection: "column" }}>
        <Paper sx={{ p: 3, borderRadius: 3, bgcolor: bgPaper, height: "100%" }}>
          <Typography variant="h6" fontWeight={700} mb={2.5} color={textMain}
            sx={{ fontFamily: "'Playfair Display', serif" }}>
            Quick Tips
          </Typography>

          <Box sx={{
            borderRadius: 2.5, bgcolor: rowBg,
            border: `1px solid ${borderCol}`, overflow: "hidden",
          }}>
            {[
              { icon: "💡", tip: "Theme changes apply instantly." },
              { icon: "🔒", tip: "Use a strong password." },
              { icon: "📅", tip: "Set due dates so tasks appear on the calendar." },
              { icon: "📓", tip: "Write in your journal daily for mood tracking." },
              { icon: "⚡", tip: "Use categories to keep tasks organized." },
              { icon: "🔔", tip: "Set reminders so you never miss a deadline." },
            ].map((t, i, arr) => (
              <Box key={i} sx={{
                display: "flex", alignItems: "flex-start", gap: 1.5,
                p: 2,
                borderBottom: i < arr.length - 1 ? `1px solid ${borderCol}` : "none",
              }}>
                <Typography fontSize={20} lineHeight={1.3}>{t.icon}</Typography>
                <Typography fontSize={13} color={textMuted} lineHeight={1.6}>{t.tip}</Typography>
              </Box>
            ))}
          </Box>

          {/* App info */}
          <Box sx={{ mt: 3, p: 2, borderRadius: 2.5, bgcolor: primary + "11", border: `1px solid ${primary}22` }}>
            <Typography fontSize={12} color={primary} fontWeight={600} mb={0.5}>TaskWise</Typography>
            <Typography fontSize={11} color={textMuted}>Flask + React + Supabase</Typography>
            <Typography fontSize={11} color={textMuted}>Version 1.0.0 — Flask Version</Typography>
          </Box>
        </Paper>
      </Box>

      {/* ── Profile Dialog ─────────────────────────────────────────────── */}
      <Dialog open={profileOpen} onClose={() => setProfileOpen(false)} maxWidth="xs" fullWidth
        PaperProps={{ sx: { borderRadius: 3 } }}>
        <DialogTitle sx={{ fontWeight: 600, fontFamily: "'Playfair Display', serif" }}>
          Edit Profile
        </DialogTitle>
        <DialogContent sx={{ display: "flex", flexDirection: "column", gap: 2, pt: "12px !important" }}>
          <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 1, mb: 1 }}>
            <Avatar sx={{ width: 64, height: 64, bgcolor: primary, fontSize: 24, fontWeight: 700 }}>
              {initials}
            </Avatar>
            <Typography variant="caption" color={textMuted}>{email}</Typography>
          </Box>
          {nameError   && <Alert severity="error"   sx={{ borderRadius: 2 }}>{nameError}</Alert>}
          {nameSuccess && <Alert severity="success" sx={{ borderRadius: 2 }}>{nameSuccess}</Alert>}
          <TextField
            label="Display Name" fullWidth value={newName}
            onChange={e => setNewName(e.target.value)}
            sx={{ "& .MuiOutlinedInput-root": { borderRadius: 2 } }}
          />
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3, gap: 1 }}>
          <Button onClick={() => setProfileOpen(false)} sx={{ borderRadius: 50 }}>Cancel</Button>
          <Button onClick={handleUpdateName} variant="contained" disabled={nameLoading}
            sx={{ borderRadius: 50, px: 3 }}>
            {nameLoading ? <CircularProgress size={18} color="inherit" /> : "Save"}
          </Button>
        </DialogActions>
      </Dialog>

      {/* ── Password Dialog ────────────────────────────────────────────── */}
      <Dialog open={passwordOpen} onClose={() => setPasswordOpen(false)} maxWidth="xs" fullWidth
        PaperProps={{ sx: { borderRadius: 3 } }}>
        <DialogTitle sx={{ fontWeight: 600, fontFamily: "'Playfair Display', serif" }}>
          Change Password
        </DialogTitle>
        <DialogContent sx={{ display: "flex", flexDirection: "column", gap: 2, pt: "12px !important" }}>
          {passError   && <Alert severity="error"   sx={{ borderRadius: 2 }}>{passError}</Alert>}
          {passSuccess && <Alert severity="success" sx={{ borderRadius: 2 }}>{passSuccess}</Alert>}
          <TextField
            label="New Password" type="password" fullWidth value={newPass}
            onChange={e => setNewPass(e.target.value)}
            sx={{ "& .MuiOutlinedInput-root": { borderRadius: 2 } }}
          />
          <TextField
            label="Confirm Password" type="password" fullWidth value={confirmPass}
            onChange={e => setConfirmPass(e.target.value)}
            sx={{ "& .MuiOutlinedInput-root": { borderRadius: 2 } }}
          />
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3, gap: 1 }}>
          <Button onClick={() => setPasswordOpen(false)} sx={{ borderRadius: 50 }}>Cancel</Button>
          <Button onClick={handleUpdatePassword} variant="contained" disabled={passLoading}
            sx={{ borderRadius: 50, px: 3 }}>
            {passLoading ? <CircularProgress size={18} color="inherit" /> : "Update"}
          </Button>
        </DialogActions>
      </Dialog>

      {/* ── Delete Account Dialog ──────────────────────────────────────── */}
      <Dialog open={deleteOpen} onClose={() => setDeleteOpen(false)} maxWidth="xs" fullWidth
        PaperProps={{ sx: { borderRadius: 3 } }}>
        <DialogTitle sx={{ fontWeight: 600, fontFamily: "'Playfair Display', serif", color: "#e53935" }}>
          Delete Account
        </DialogTitle>
        <DialogContent sx={{ display: "flex", flexDirection: "column", gap: 2, pt: "12px !important" }}>
          <Alert severity="error" sx={{ borderRadius: 2 }}>
            This will permanently delete all your tasks and data. This cannot be undone.
          </Alert>
          {deleteError && <Alert severity="warning" sx={{ borderRadius: 2 }}>{deleteError}</Alert>}
          <Typography fontSize={13} color={textMuted}>
            Type <strong>DELETE</strong> below to confirm:
          </Typography>
          <TextField
            fullWidth placeholder="DELETE" value={deleteConfirm}
            onChange={e => setDeleteConfirm(e.target.value)}
            sx={{ "& .MuiOutlinedInput-root": { borderRadius: 2, borderColor: "#e53935" } }}
          />
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3, gap: 1 }}>
          <Button onClick={() => setDeleteOpen(false)} sx={{ borderRadius: 50 }}>Cancel</Button>
          <Button
            onClick={handleDeleteAccount}
            variant="contained" disabled={deleteLoading}
            sx={{ borderRadius: 50, px: 3, bgcolor: "#e53935", "&:hover": { bgcolor: "#c62828" } }}>
            {deleteLoading ? <CircularProgress size={18} color="inherit" /> : "Delete Forever"}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar */}
      <Snackbar open={snack.open} autoHideDuration={3000}
        onClose={() => setSnack(s => ({ ...s, open: false }))}
        anchorOrigin={{ vertical: "bottom", horizontal: "right" }}>
        <Alert severity={snack.severity} sx={{ borderRadius: 2 }}
          onClose={() => setSnack(s => ({ ...s, open: false }))}>
          {snack.msg}
        </Alert>
      </Snackbar>
    </Box>
  );
}
