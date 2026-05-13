import { useState, useEffect, useContext } from "react";
import {
  Box, Paper, Typography, IconButton, Avatar,
  CircularProgress, Tooltip, Snackbar, Alert,
} from "@mui/material";
import RefreshIcon   from "@mui/icons-material/Refresh";
import LogoutIcon    from "@mui/icons-material/Logout";
import TaskIcon      from "@mui/icons-material/Task";
import MenuBookIcon  from "@mui/icons-material/MenuBook";
import HistoryIcon   from "@mui/icons-material/History";
import { useNavigate } from "react-router-dom";
import { AppContext }  from "../context/AppContext";
import { supabase }    from "../services/supabase";

const LOG_COLORS = {
  Login:  "#4CAF50",
  Logout: "#f4a261",
  Signup: "#4285F4",
  Delete: "#e53935",
  Ban:    "#9c27b0",
};

export default function AdminPanel() {
  const navigate       = useNavigate();
  const { logout }     = useContext(AppContext);

  const [logs,    setLogs]    = useState([]);
  const [stats,   setStats]   = useState({ tasks: 0, journals: 0 });
  const [loading, setLoading] = useState(true);
  const [snack,   setSnack]   = useState({ open: false, msg: "", severity: "success" });

  const showSnack = (msg, severity = "success") => setSnack({ open: true, msg, severity });

  const fetchAll = async () => {
    const [logsRes, tasksRes, journalsRes] = await Promise.all([
      supabase.from("admin_logs").select("*").order("created_at", { ascending: false }).limit(100),
      supabase.from("tasks").select("id", { count: "exact" }),
      supabase.from("journal_entries").select("id", { count: "exact" }),
    ]);
    setLogs(logsRes.data || []);
    setStats({
      tasks:    tasksRes.count    ?? 0,
      journals: journalsRes.count ?? 0,
    });
    setLoading(false);
  };

  useEffect(() => {
    const load = async () => { await fetchAll(); };
    load();
  }, []);

  const handleLogout = async () => {
    await supabase.from("admin_logs").insert({
      action: "Logout", details: "Admin logged out",
      created_at: new Date().toISOString(),
    });
    await logout();
    navigate("/");
  };

  const handleRefresh = () => { fetchAll(); showSnack("Refreshed!"); };

  const fmt = (iso) => iso
    ? new Date(iso).toLocaleString([], { dateStyle: "medium", timeStyle: "short" })
    : "";

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

        {/* Stats */}
        <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap" }}>
          {[
            { icon: <TaskIcon />,     label: "Total Tasks",     value: stats.tasks,    color: "#4285F4" },
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
                {loading
                  ? <CircularProgress size={20} />
                  : <Typography fontWeight={700} fontSize={24} color="#1a4a3a">{s.value}</Typography>
                }
              </Box>
            </Paper>
          ))}
        </Box>

        {/* Log History */}
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