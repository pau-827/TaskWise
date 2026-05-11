import { useState, useEffect, useContext, useCallback } from "react";
import {
  Box, Paper, Typography, IconButton, Avatar, Chip, CircularProgress,
  Tooltip, Snackbar, Alert, Button, TextField, InputAdornment,
  Dialog, DialogTitle, DialogContent, DialogActions, Divider,
} from "@mui/material";
import RefreshIcon      from "@mui/icons-material/Refresh";
import LogoutIcon       from "@mui/icons-material/Logout";
import DeleteIcon       from "@mui/icons-material/Delete";
import BlockIcon        from "@mui/icons-material/Block";
import SearchIcon       from "@mui/icons-material/Search";
import PeopleIcon       from "@mui/icons-material/People";
import TaskIcon         from "@mui/icons-material/Task";
import MenuBookIcon     from "@mui/icons-material/MenuBook";
import HistoryIcon      from "@mui/icons-material/History";
import { useNavigate }  from "react-router-dom";
import { AppContext }   from "../context/AppContext";
import { supabase }     from "../services/supabase";

const LOG_COLORS = {
  Login:   "#4CAF50",
  Logout:  "#f4a261",
  Signup:  "#4285F4",
  Delete:  "#e53935",
  Ban:     "#9c27b0",
};

export default function AdminPanel() {
  const navigate          = useNavigate();
  const { logout }        = useContext(AppContext);

  const [users,       setUsers]       = useState([]);
  const [logs,        setLogs]        = useState([]);
  const [stats,       setStats]       = useState({ users: 0, tasks: 0, journals: 0 });
  const [loading,     setLoading]     = useState(true);
  const [search,      setSearch]      = useState("");
  const [deleteOpen,  setDeleteOpen]  = useState(false);
  const [banOpen,     setBanOpen]     = useState(false);
  const [targetUser,  setTargetUser]  = useState(null);
  const [snack,       setSnack]       = useState({ open: false, msg: "", severity: "success" });

  const showSnack = (msg, severity = "success") => setSnack({ open: true, msg, severity });

  // ── Fetch all users from profiles ─────────────────────────────────────
  const fetchUsers = useCallback(async () => {
    setLoading(true);
    const { data, error } = await supabase
      .from("profiles")
      .select("*")
      .order("created_at", { ascending: false });
    if (!error) setUsers(data || []);
    setLoading(false);
  }, []);

  // ── Fetch logs ─────────────────────────────────────────────────────────
  const fetchLogs = useCallback(async () => {
    const { data } = await supabase
      .from("admin_logs")
      .select("*")
      .order("created_at", { ascending: false })
      .limit(100);
    setLogs(data || []);
  }, []);

  // ── Fetch stats ────────────────────────────────────────────────────────
  const fetchStats = useCallback(async () => {
    const [usersRes, tasksRes, journalsRes] = await Promise.all([
      supabase.from("profiles").select("id", { count: "exact" }),
      supabase.from("tasks").select("id", { count: "exact" }),
      supabase.from("journal_entries").select("id", { count: "exact" }),
    ]);
    setStats({
      users:    usersRes.count    ?? 0,
      tasks:    tasksRes.count    ?? 0,
      journals: journalsRes.count ?? 0,
    });
  }, []);

  const addLog = async (action, details, targetEmail = null) => {
    await supabase.from("admin_logs").insert({
      action,
      details,
      target_email: targetEmail,
      created_at:   new Date().toISOString(),
    });
    await fetchLogs();
  };

  useEffect(() => {
    fetchUsers();
    fetchLogs();
    fetchStats();
  }, [fetchUsers, fetchLogs, fetchStats]);

  // ── Ban / Unban user ───────────────────────────────────────────────────
  const handleBan = async () => {
    if (!targetUser) return;
    const newStatus = targetUser.status === "banned" ? "active" : "banned";
    const { error } = await supabase
      .from("profiles")
      .update({ status: newStatus })
      .eq("id", targetUser.id);
    if (!error) {
      showSnack(`User ${newStatus === "banned" ? "banned" : "unbanned"} successfully.`);
      await addLog(newStatus === "banned" ? "Ban" : "Unban", `${newStatus === "banned" ? "Banned" : "Unbanned"} user: ${targetUser.display_name}`, targetUser.email);
      fetchUsers(); fetchStats();
    } else showSnack(error.message, "error");
    setBanOpen(false); setTargetUser(null);
  };

  // ── Delete user ────────────────────────────────────────────────────────
  const handleDelete = async () => {
    if (!targetUser) return;
    // Delete all user data first
    await supabase.from("tasks").delete().eq("user_id", targetUser.id);
    await supabase.from("journal_entries").delete().eq("user_id", targetUser.id);
    await supabase.from("profiles").delete().eq("id", targetUser.id);
    showSnack("User and all data deleted.");
    await addLog("Delete", `Deleted user: ${targetUser.display_name}`, targetUser.email);
    fetchUsers(); fetchStats();
    setDeleteOpen(false); setTargetUser(null);
  };

  const handleLogout = async () => {
    await addLog("Logout", "Admin logged out");
    await logout();
    navigate("/");
  };

  const handleRefresh = () => { fetchUsers(); fetchLogs(); fetchStats(); showSnack("Refreshed!"); };

  const filteredUsers = users.filter(u =>
    u.display_name?.toLowerCase().includes(search.toLowerCase()) ||
    u.email?.toLowerCase().includes(search.toLowerCase())
  );

  const fmt = (iso) => iso ? new Date(iso).toLocaleString([], { dateStyle: "medium", timeStyle: "short" }) : "";

  return (
    <Box sx={{ minHeight: "100vh", bgcolor: "#f0f7f5", fontFamily: "'DM Sans', sans-serif" }}>
      <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&family=Playfair+Display:wght@500;600&display=swap" rel="stylesheet" />

      {/* Header */}
      <Box sx={{ bgcolor: "#fff", borderBottom: "1px solid #c5e0d8", px: 4, py: 2,
        display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
          <Avatar sx={{ bgcolor: "#4a9b82", width: 34, height: 34, fontSize: 16 }}>A</Avatar>
          <Box>
            <Typography fontWeight={700} fontSize={18} color="#1a4a3a"
              sx={{ fontFamily: "'Playfair Display', serif" }}>
              TaskWise Admin
            </Typography>
            <Typography variant="caption" color="#7aaa97">Admin Panel</Typography>
          </Box>
        </Box>
        <Box sx={{ display: "flex", gap: 1 }}>
          <Tooltip title="Refresh">
            <IconButton onClick={handleRefresh} sx={{ color: "#4a9b82" }}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Logout">
            <IconButton onClick={handleLogout} sx={{ color: "#e53935" }}>
              <LogoutIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      <Box sx={{ p: 3, display: "flex", flexDirection: "column", gap: 3 }}>

        {/* Stats row */}
        <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap" }}>
          {[
            { icon: <PeopleIcon />,   label: "Total Users",   value: stats.users,    color: "#4a9b82" },
            { icon: <TaskIcon />,     label: "Total Tasks",   value: stats.tasks,    color: "#4285F4" },
            { icon: <MenuBookIcon />, label: "Journal Entries", value: stats.journals, color: "#f4a261" },
          ].map(s => (
            <Paper key={s.label} sx={{ p: 2.5, borderRadius: 3, flex: "1 1 180px",
              display: "flex", alignItems: "center", gap: 2,
              border: "1px solid #c5e0d8", boxShadow: "0 4px 16px rgba(74,155,130,0.08)" }}>
              <Box sx={{ width: 44, height: 44, borderRadius: 2, bgcolor: s.color + "22",
                display: "flex", alignItems: "center", justifyContent: "center", color: s.color }}>
                {s.icon}
              </Box>
              <Box>
                <Typography variant="caption" color="#7aaa97" fontWeight={500}>{s.label}</Typography>
                <Typography fontWeight={700} fontSize={24} color="#1a4a3a">{s.value}</Typography>
              </Box>
            </Paper>
          ))}
        </Box>

        {/* Main content */}
        <Box sx={{ display: "flex", gap: 3, alignItems: "flex-start", flexWrap: "wrap" }}>

          {/* Users panel */}
          <Box sx={{ flex: "1 1 400px", minWidth: 0 }}>
            <Paper sx={{ p: 3, borderRadius: 3, border: "1px solid #c5e0d8" }}>
              <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
                <Typography fontWeight={700} fontSize={18} color="#1a4a3a"
                  sx={{ fontFamily: "'Playfair Display', serif" }}>
                  Users
                </Typography>
                <Typography variant="caption" color="#7aaa97">{filteredUsers.length} total</Typography>
              </Box>

              <TextField fullWidth size="small" placeholder="Search users..."
                value={search} onChange={e => setSearch(e.target.value)}
                InputProps={{
                  startAdornment: <InputAdornment position="start"><SearchIcon fontSize="small" /></InputAdornment>,
                  sx: { borderRadius: 50, mb: 0 },
                }}
                sx={{ mb: 2 }}
              />

              {loading ? (
                <Box sx={{ display: "flex", justifyContent: "center", py: 4 }}><CircularProgress size={28} /></Box>
              ) : filteredUsers.length === 0 ? (
                <Box sx={{ textAlign: "center", py: 4, color: "#7aaa97" }}>
                  <Typography>No users found.</Typography>
                </Box>
              ) : (
                <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5, maxHeight: 480, overflowY: "auto",
                  "&::-webkit-scrollbar": { width: 4 },
                  "&::-webkit-scrollbar-thumb": { borderRadius: 4, bgcolor: "#4a9b8244" },
                }}>
                  {filteredUsers.map(u => (
                    <Paper key={u.id} variant="outlined" sx={{ p: 2, borderRadius: 2.5,
                      borderColor: u.status === "banned" ? "#e5393544" : "#c5e0d8",
                      bgcolor: u.status === "banned" ? "#e5393508" : "#fff",
                      transition: "all 0.2s", "&:hover": { boxShadow: 2 },
                    }}>
                      <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                        <Avatar sx={{ width: 38, height: 38, bgcolor: u.role === "admin" ? "#4a9b82" : "#7aaa97", fontSize: 14, fontWeight: 700 }}>
                          {(u.display_name || u.email || "U").slice(0, 2).toUpperCase()}
                        </Avatar>
                        <Box sx={{ flex: 1, minWidth: 0 }}>
                          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                            <Typography fontWeight={600} fontSize={14} color="#1a4a3a" noWrap>
                              {u.display_name || "—"}
                            </Typography>
                            <Chip label={u.role || "user"} size="small"
                              sx={{ borderRadius: 50, height: 18, fontSize: 10, fontWeight: 700,
                                bgcolor: u.role === "admin" ? "#4a9b8222" : "#7aaa9722",
                                color: u.role === "admin" ? "#4a9b82" : "#7aaa97" }} />
                            {u.status === "banned" && (
                              <Chip label="Banned" size="small" color="error"
                                sx={{ borderRadius: 50, height: 18, fontSize: 10, fontWeight: 700 }} />
                            )}
                          </Box>
                          <Typography variant="caption" color="#7aaa97" noWrap>{u.email}</Typography>
                        </Box>
                        {u.role !== "admin" && (
                          <Box sx={{ display: "flex", gap: 0.5 }}>
                            <Tooltip title={u.status === "banned" ? "Unban user" : "Ban user"}>
                              <IconButton size="small"
                                sx={{ color: u.status === "banned" ? "#4a9b82" : "#9c27b0" }}
                                onClick={() => { setTargetUser(u); setBanOpen(true); }}>
                                <BlockIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Delete user">
                              <IconButton size="small" color="error"
                                onClick={() => { setTargetUser(u); setDeleteOpen(true); }}>
                                <DeleteIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          </Box>
                        )}
                      </Box>
                      <Typography variant="caption" color="#7aaa97" display="block" mt={0.5} fontSize={10}>
                        Joined {fmt(u.created_at)}
                      </Typography>
                    </Paper>
                  ))}
                </Box>
              )}
            </Paper>
          </Box>

          {/* Log History panel */}
          <Box sx={{ flex: "1 1 400px", minWidth: 0 }}>
            <Paper sx={{ p: 3, borderRadius: 3, border: "1px solid #c5e0d8" }}>
              <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}>
                <HistoryIcon sx={{ color: "#4a9b82" }} />
                <Typography fontWeight={700} fontSize={18} color="#1a4a3a"
                  sx={{ fontFamily: "'Playfair Display', serif" }}>
                  Log History
                </Typography>
              </Box>

              {logs.length === 0 ? (
                <Box sx={{ textAlign: "center", py: 4, color: "#7aaa97" }}>
                  <Typography variant="body2">No logs yet.</Typography>
                </Box>
              ) : (
                <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5, maxHeight: 520, overflowY: "auto",
                  "&::-webkit-scrollbar": { width: 4 },
                  "&::-webkit-scrollbar-thumb": { borderRadius: 4, bgcolor: "#4a9b8244" },
                }}>
                  {logs.map((log, i) => (
                    <Box key={log.id || i} sx={{ p: 1.5, borderRadius: 2,
                      bgcolor: "#f8fdfb", border: "1px solid #e0f0eb" }}>
                      <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 0.3 }}>
                        <Box sx={{ width: 8, height: 8, borderRadius: "50%", flexShrink: 0,
                          bgcolor: LOG_COLORS[log.action] || "#7aaa97" }} />
                        <Typography fontWeight={600} fontSize={13} color="#1a4a3a">{log.action}</Typography>
                        <Typography variant="caption" color="#7aaa97" ml="auto" fontSize={10}>
                          {fmt(log.created_at)}
                        </Typography>
                      </Box>
                      {log.target_email && (
                        <Typography variant="caption" color="#7aaa97" display="block" fontSize={11}>
                          👤 {log.target_email}
                        </Typography>
                      )}
                      {log.details && (
                        <Typography variant="caption" color="#4a7a68" display="block" fontSize={11}>
                          {log.details}
                        </Typography>
                      )}
                    </Box>
                  ))}
                </Box>
              )}
            </Paper>
          </Box>
        </Box>
      </Box>

      {/* Ban dialog */}
      <Dialog open={banOpen} onClose={() => setBanOpen(false)} maxWidth="xs" fullWidth
        PaperProps={{ sx: { borderRadius: 3 } }}>
        <DialogTitle sx={{ fontWeight: 600 }}>
          {targetUser?.status === "banned" ? "Unban User?" : "Ban User?"}
        </DialogTitle>
        <DialogContent>
          <Typography fontSize={14} color="#4a7a68">
            {targetUser?.status === "banned"
              ? `Restore access for ${targetUser?.display_name}?`
              : `Ban ${targetUser?.display_name} from TaskWise? They will not be able to log in.`}
          </Typography>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3, gap: 1 }}>
          <Button onClick={() => setBanOpen(false)} sx={{ borderRadius: 50 }}>Cancel</Button>
          <Button onClick={handleBan} variant="contained"
            sx={{ borderRadius: 50, bgcolor: targetUser?.status === "banned" ? "#4a9b82" : "#9c27b0",
              "&:hover": { bgcolor: targetUser?.status === "banned" ? "#3a8270" : "#7b1fa2" } }}>
            {targetUser?.status === "banned" ? "Unban" : "Ban"}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete dialog */}
      <Dialog open={deleteOpen} onClose={() => setDeleteOpen(false)} maxWidth="xs" fullWidth
        PaperProps={{ sx: { borderRadius: 3 } }}>
        <DialogTitle sx={{ fontWeight: 600, color: "#e53935" }}>Delete User?</DialogTitle>
        <DialogContent>
          <Alert severity="error" sx={{ borderRadius: 2, mb: 2 }}>
            This permanently deletes the user and ALL their data including tasks and journal entries.
          </Alert>
          <Typography fontSize={14} color="#4a7a68">
            Are you sure you want to delete <strong>{targetUser?.display_name}</strong>?
          </Typography>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3, gap: 1 }}>
          <Button onClick={() => setDeleteOpen(false)} sx={{ borderRadius: 50 }}>Cancel</Button>
          <Button onClick={handleDelete} variant="contained" color="error" sx={{ borderRadius: 50, px: 3 }}>
            Delete Forever
          </Button>
        </DialogActions>
      </Dialog>

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
