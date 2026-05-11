import { useState, useEffect, useContext, useCallback } from "react";
import { Link } from "react-router-dom";
import { ThemeContext } from "../context/ThemeContext";
import { THEMES } from "../theme/themes";
import {
  Box, Paper, Typography, Button, IconButton, TextField,
  InputAdornment, Chip, CircularProgress, Tooltip, LinearProgress,
  Menu, MenuItem, Dialog, DialogTitle, DialogContent, DialogActions,
  FormControl, InputLabel, Select, Snackbar, Alert, Grid, RadioGroup,
  FormControlLabel, Radio,
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import AddIcon from "@mui/icons-material/Add";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import PictureAsPdfIcon from "@mui/icons-material/PictureAsPdf";
import SyncIcon from "@mui/icons-material/Sync";
import RadioButtonUncheckedIcon from "@mui/icons-material/RadioButtonUnchecked";
import SortIcon from "@mui/icons-material/Sort";
import CalendarTodayIcon from "@mui/icons-material/CalendarToday";
import { PieChart, Pie, Cell, Tooltip as ReTooltip, ResponsiveContainer, Legend } from "recharts";
import { supabase } from "../services/supabase";
import { AppContext } from "../context/AppContext";
import dayjs from "dayjs";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { DateTimePicker } from "@mui/x-date-pickers/DateTimePicker";


const CATEGORIES = ["All Tasks", "Personal", "Work", "Study", "Bills", "Others"];
const PRIORITIES = ["low", "medium", "high"];

const PRIORITY_COLOR = {
  low: "#4a9b82",
  medium: "#f4a261",
  high: "#e53935",
};

function toDateTimeLocalValue(value) {
  if (!value) return "";
  const date = new Date(value);
  const offset = date.getTimezoneOffset();
  const localDate = new Date(date.getTime() - offset * 60000);
  return localDate.toISOString().slice(0, 16);
}

function localInputToISO(value) {
  if (!value) return null;
  return new Date(value).toISOString();
}

function formatTaskDate(value) {
  if (!value) return "";
  return new Date(value).toLocaleString([], {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function isOverdue(task) {
  if (!task.due_date || task.status === "completed") return false;
  return new Date(task.due_date) < new Date();
}

function TaskModal({ open, onClose, onSave, editTask }) {
  const emptyForm = {
    title: "",
    description: "",
    category: "Personal",
    priority: "medium",
    due_date: "",
    reminder_at: "",
  };

  const [form, setForm] = useState(emptyForm);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!open) return;

    if (editTask) {
      setForm({
        title: editTask.title || "",
        description: editTask.description || "",
        category: editTask.category || "Personal",
        priority: editTask.priority || "medium",
        due_date: toDateTimeLocalValue(editTask.due_date),
        reminder_at: toDateTimeLocalValue(editTask.reminder_at),
      });
    } else {
      setForm(emptyForm);
    }

    setError("");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  const handleSave = async () => {
    if (!form.title.trim()) {
      setError("Title is required.");
      return;
    }

    setLoading(true);
    await onSave(form);
    setLoading(false);
    onClose();
  };

  const inputStyle = {
    "& .MuiOutlinedInput-root": {
      borderRadius: 2,
    },
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{ sx: { borderRadius: 3 } }}
    >
      <DialogTitle sx={{ fontWeight: 600, fontFamily: "'Playfair Display', serif" }}>
        {editTask ? "Edit Task" : "New Task"}
      </DialogTitle>

      <DialogContent sx={{ display: "flex", flexDirection: "column", gap: 2, pt: "12px !important" }}>
        {error && <Alert severity="error" sx={{ borderRadius: 2 }}>{error}</Alert>}

        <TextField
          label="Title"
          fullWidth
          required
          value={form.title}
          onChange={(e) => setForm({ ...form, title: e.target.value })}
          sx={inputStyle}
        />

        <TextField
          label="Description"
          fullWidth
          multiline
          rows={3}
          value={form.description}
          onChange={(e) => setForm({ ...form, description: e.target.value })}
          sx={inputStyle}
        />

        <Grid container spacing={2}>
          <Grid item xs={6}>
            <FormControl fullWidth>
              <InputLabel>Category</InputLabel>
              <Select
                value={form.category}
                label="Category"
                onChange={(e) => setForm({ ...form, category: e.target.value })}
                sx={{ borderRadius: 2 }}
              >
                {CATEGORIES.filter((c) => c !== "All Tasks").map((c) => (
                  <MenuItem key={c} value={c}>{c}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={6}>
            <FormControl fullWidth>
              <InputLabel>Priority</InputLabel>
              <Select
                value={form.priority}
                label="Priority"
                onChange={(e) => setForm({ ...form, priority: e.target.value })}
                sx={{ borderRadius: 2 }}
              >
                {PRIORITIES.map((p) => (
                  <MenuItem key={p} value={p}>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                      <Box sx={{ width: 8, height: 8, borderRadius: "50%", bgcolor: PRIORITY_COLOR[p] }} />
                      {p.charAt(0).toUpperCase() + p.slice(1)}
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>

<LocalizationProvider dateAdapter={AdapterDayjs}>
  <Grid container spacing={2}>
    <Grid item xs={12} md={6}>
      <DateTimePicker
        label="Due Date & Time"
        value={form.due_date ? dayjs(form.due_date) : null}
        onChange={(newValue) =>
          setForm({
            ...form,
            due_date: newValue
              ? newValue.format("YYYY-MM-DDTHH:mm")
              : "",
          })
        }
        slotProps={{
          textField: {
            fullWidth: true,
            helperText: "Select the task deadline",
            sx: {
              "& .MuiOutlinedInput-root": {
                borderRadius: 3,
              },
            },
          },
        }}
      />
    </Grid>

    <Grid item xs={12} md={6}>
      <DateTimePicker
        label="Reminder Time"
        value={form.reminder_at ? dayjs(form.reminder_at) : null}
        onChange={(newValue) =>
          setForm({
            ...form,
            reminder_at: newValue
              ? newValue.format("YYYY-MM-DDTHH:mm")
              : "",
          })
        }
        slotProps={{
          textField: {
            fullWidth: true,
            helperText: "Optional reminder before the deadline",
            sx: {
              "& .MuiOutlinedInput-root": {
                borderRadius: 3,
              },
            },
          },
        }}
      />
    </Grid>
  </Grid>
</LocalizationProvider>
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 3, gap: 1 }}>
        <Button onClick={onClose} sx={{ borderRadius: 50 }}>
          Cancel
        </Button>

        <Button
          onClick={handleSave}
          variant="contained"
          disabled={loading}
          sx={{ borderRadius: 50, px: 3 }}
        >
          {loading ? "Saving..." : editTask ? "Save Changes" : "Add Task"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default function Tasks() {
  const { user } = useContext(AppContext);
  const { themeName } = useContext(ThemeContext);

  const CHART_COLORS =
    THEMES[themeName]?.custom?.chartColors ??
    ["#4a9b82", "#f4a261", "#2a9d8f", "#e76f51", "#a855f7"];

  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeCategory, setActiveCategory] = useState("All Tasks");
  const [search, setSearch] = useState("");
  const [sortAnchor, setSortAnchor] = useState(null);
  const [sortBy, setSortBy] = useState("created_at");
  const [modalOpen, setModalOpen] = useState(false);
  const [editTask, setEditTask] = useState(null);
  const [snack, setSnack] = useState({ open: false, msg: "", severity: "success" });
  const [printOpen, setPrintOpen] = useState(false);
  const [printScope, setPrintScope] = useState("current");
  const [syncing, setSyncing] = useState(false);

  const showSnack = (msg, severity = "success") => {
    setSnack({ open: true, msg, severity });
  };

  const fetchTasks = useCallback(async () => {
    if (!user?.id) return;

    setLoading(true);

    const { data, error } = await supabase
      .from("tasks")
      .select("*")
      .eq("user_id", user.id)
      .order(sortBy, { ascending: sortBy === "title" });

    if (!error) {
      setTasks(data || []);
    } else {
      showSnack(error.message, "error");
    }

    setLoading(false);
  }, [user, sortBy]);

  useEffect(() => {
    if (user) fetchTasks();
  }, [fetchTasks, user]);

  const handleClassroomSync = async () => {
    setSyncing(true);

    try {
      const { data: { session } } = await supabase.auth.getSession();
      const access_token = session?.provider_token;
      const user_jwt = session?.access_token;

      if (!access_token) {
        showSnack("No Google access token found. Please log in with Google first.", "error");
        setSyncing(false);
        return;
      }

      const res = await fetch("http://localhost:5000/api/classroom/sync", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ access_token, user_id: user.id, user_jwt }),
      });

      const data = await res.json();

      if (!res.ok) throw new Error(data.error || "Sync failed");

      showSnack(data.message, "success");
      fetchTasks();
    } catch (err) {
      showSnack(err.message, "error");
    }

    setSyncing(false);
  };

  const handleClassroomUnsync = async () => {
    if (!window.confirm("This will remove all tasks synced from Google Classroom. Continue?")) return;

    setSyncing(true);

    try {
      const { data: { session } } = await supabase.auth.getSession();
      const user_jwt = session?.access_token;

      const res = await fetch("http://localhost:5000/api/classroom/unsync", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: user.id, user_jwt }),
      });

      const data = await res.json();

      if (!res.ok) throw new Error(data.error || "Unsync failed");

      showSnack(data.message, "success");
      fetchTasks();
    } catch (err) {
      showSnack(err.message, "error");
    }

    setSyncing(false);
  };

  const handleSave = async (form) => {
    const payload = {
      ...form,
      user_id: user.id,
      due_date: localInputToISO(form.due_date),
      reminder_at: localInputToISO(form.reminder_at),
      status: editTask?.status || "pending",
    };

    if (editTask) {
      const { error } = await supabase
        .from("tasks")
        .update(payload)
        .eq("id", editTask.id);

      if (!error) {
        showSnack("Task updated!");
        fetchTasks();
      } else {
        showSnack(error.message, "error");
      }
    } else {
      const { error } = await supabase
        .from("tasks")
        .insert(payload);

      if (!error) {
        showSnack("Task added!");
        fetchTasks();
      } else {
        showSnack(error.message, "error");
      }
    }
  };

  const toggleComplete = async (task) => {
    const newStatus = task.status === "completed" ? "pending" : "completed";

    const { error } = await supabase
      .from("tasks")
      .update({ status: newStatus })
      .eq("id", task.id);

    if (!error) {
      setTasks((prev) =>
        prev.map((t) => (t.id === task.id ? { ...t, status: newStatus } : t))
      );

      showSnack(newStatus === "completed" ? "Task completed!" : "Marked as pending.");
    } else {
      showSnack(error.message, "error");
    }
  };

  const deleteTask = async (id) => {
    const { error } = await supabase
      .from("tasks")
      .delete()
      .eq("id", id);

    if (!error) {
      setTasks((prev) => prev.filter((t) => t.id !== id));
      showSnack("Task deleted.");
    } else {
      showSnack(error.message, "error");
    }
  };

  const filtered = tasks.filter((t) => {
    const matchCat = activeCategory === "All Tasks" || t.category === activeCategory;
    const matchSearch =
      t.title.toLowerCase().includes(search.toLowerCase()) ||
      (t.description || "").toLowerCase().includes(search.toLowerCase());

    return matchCat && matchSearch;
  });

  const total = tasks.length;
  const completed = tasks.filter((t) => t.status === "completed").length;
  const pending = tasks.filter((t) => t.status === "pending").length;
  const overdue = tasks.filter(isOverdue).length;
  const progress = total ? Math.round((completed / total) * 100) : 0;

  const categoryData = CATEGORIES
    .filter((c) => c !== "All Tasks")
    .map((cat) => ({
      name: cat,
      value: tasks.filter((t) => t.category === cat).length,
    }))
    .filter((d) => d.value > 0);

  const handlePrint = () => {
    const tasksToPrint = printScope === "all" ? tasks : filtered;
    const displayName = user?.user_metadata?.display_name || user?.email?.split("@")[0] || "User";
    const now = new Date().toLocaleString();

    const totalP = tasksToPrint.length;
    const completedP = tasksToPrint.filter((t) => t.status === "completed").length;
    const pendingP = tasksToPrint.filter((t) => t.status === "pending").length;
    const overdueP = tasksToPrint.filter(isOverdue).length;
    const progressP = totalP ? Math.round((completedP / totalP) * 100) : 0;

    const rows = tasksToPrint.map((t) => `
      <tr>
        <td>${t.status === "completed" ? "✅" : isOverdue(t) ? "⚠️" : "🔲"}</td>
        <td>
          <strong>${t.title}</strong>
          ${t.description ? `<br/><span style="color:#666;font-size:12px">${t.description}</span>` : ""}
        </td>
        <td>${t.category}</td>
        <td style="color:${t.priority === "high" ? "#e53935" : t.priority === "medium" ? "#f4a261" : "#4a9b82"}">
          ${t.priority}
        </td>
        <td>${t.due_date ? formatTaskDate(t.due_date) : "—"}</td>
        <td>${t.status}</td>
      </tr>
    `).join("");

    const html = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>TaskWise Task Report</title>
        <style>
          * { box-sizing: border-box; margin: 0; padding: 0; }
          body { font-family: 'Segoe UI', sans-serif; color: #1a1a2e; padding: 40px; }
          .header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 28px; border-bottom: 2px solid #4a9b82; padding-bottom: 16px; }
          .logo { font-size: 28px; font-weight: 700; color: #4a9b82; }
          .meta { font-size: 12px; color: #888; text-align: right; }
          .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 28px; }
          .stat { background: #f0f7f5; border-radius: 10px; padding: 14px; text-align: center; }
          .stat-value { font-size: 28px; font-weight: 700; color: #4a9b82; }
          .stat-label { font-size: 11px; color: #888; margin-top: 2px; text-transform: uppercase; letter-spacing: 1px; }
          .progress-bar { background: #e0e0e0; border-radius: 50px; height: 8px; margin-bottom: 28px; }
          .progress-fill { background: linear-gradient(90deg, #7bbfaa, #4a9b82); height: 100%; border-radius: 50px; width: ${progressP}%; }
          .progress-label { font-size: 12px; color: #888; margin-bottom: 6px; }
          table { width: 100%; border-collapse: collapse; font-size: 13px; }
          thead tr { background: #4a9b82; color: white; }
          thead th { padding: 10px 12px; text-align: left; font-weight: 600; }
          tbody tr { border-bottom: 1px solid #eee; }
          tbody tr:nth-child(even) { background: #f9f9f9; }
          tbody td { padding: 10px 12px; vertical-align: top; }
          .footer { margin-top: 32px; font-size: 11px; color: #aaa; text-align: center; }
          @media print { body { padding: 20px; } }
        </style>
      </head>
      <body>
        <div class="header">
          <div>
            <div class="logo">TaskWise</div>
            <div style="font-size:13px;color:#666;margin-top:4px">
              Task Report - ${printScope === "all" ? "All Tasks" : `Filtered: ${activeCategory}`}
            </div>
          </div>
          <div class="meta">
            <div>${displayName}</div>
            <div>Generated: ${now}</div>
          </div>
        </div>

        <div class="stats">
          <div class="stat"><div class="stat-value">${totalP}</div><div class="stat-label">Total</div></div>
          <div class="stat"><div class="stat-value" style="color:#f4a261">${pendingP}</div><div class="stat-label">Pending</div></div>
          <div class="stat"><div class="stat-value" style="color:#4CAF50">${completedP}</div><div class="stat-label">Completed</div></div>
          <div class="stat"><div class="stat-value" style="color:#e53935">${overdueP}</div><div class="stat-label">Overdue</div></div>
        </div>

        <div class="progress-label">Overall Progress - ${progressP}%</div>
        <div class="progress-bar"><div class="progress-fill"></div></div>

        <table>
          <thead>
            <tr>
              <th style="width:32px"></th>
              <th>Task</th>
              <th>Category</th>
              <th>Priority</th>
              <th>Due Date</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>

        <div class="footer">TaskWise • Exported on ${now}</div>
      </body>
      </html>
    `;

    const win = window.open("", "_blank");
    win.document.write(html);
    win.document.close();
    win.focus();

    setTimeout(() => {
      win.print();
    }, 500);

    setPrintOpen(false);
  };

  return (
<Box
  sx={{
    width: "100%",
    display: "flex",
    flexDirection: { xs: "column", lg: "row" },
    gap: { xs: 2, md: 3 },
    alignItems: "stretch",
  }}
>      <Box sx={{ flex: "1 1 0", minWidth: 0, width: "100%" }}>
        <Paper sx={{ p: 3, borderRadius: 3, height: "calc(100vh - 140px)", position: "relative", display: "flex", flexDirection: "column", overflow: "hidden" }}>
          <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
            <Typography variant="h5" sx={{ fontWeight: 600, fontFamily: "'Playfair Display', serif" }}>
              Tasks
            </Typography>

            <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap", justifyContent: "flex-end" }}>
              <Tooltip title="Sync Google Classroom">
                <IconButton
                  onClick={handleClassroomSync}
                  disabled={syncing}
                  sx={{ border: "1px solid", borderColor: "divider", borderRadius: 2 }}
                >
                  <SyncIcon
                    fontSize="small"
                    sx={{
                      animation: syncing ? "spin 1s linear infinite" : "none",
                      "@keyframes spin": { "100%": { transform: "rotate(360deg)" } },
                    }}
                  />
                </IconButton>
              </Tooltip>

              <Tooltip title="Unsync Classroom tasks">
                <IconButton
                  onClick={handleClassroomUnsync}
                  disabled={syncing}
                  sx={{
                    border: "1px solid",
                    borderColor: "error.light",
                    borderRadius: 2,
                    color: "error.main",
                    "&:hover": { bgcolor: "error.light", color: "#fff" },
                  }}
                >
                  <SyncIcon fontSize="small" sx={{ transform: "scaleX(-1)" }} />
                </IconButton>
              </Tooltip>

              <Tooltip title="Export as PDF">
                <IconButton
                  onClick={() => setPrintOpen(true)}
                  sx={{ border: "1px solid", borderColor: "divider", borderRadius: 2 }}
                >
                  <PictureAsPdfIcon fontSize="small" />
                </IconButton>
              </Tooltip>

              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => {
                  setEditTask(null);
                  setModalOpen(true);
                }}
                sx={{ borderRadius: 50, px: 2.5 }}
              >
                Add Task
              </Button>
            </Box>
          </Box>

          <Box sx={{ display: "flex", gap: 1.5, mb: 2 }}>
            <TextField
              fullWidth
              size="small"
              placeholder="Search tasks..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon fontSize="small" />
                  </InputAdornment>
                ),
                sx: { borderRadius: 50 },
              }}
            />

            <Tooltip title="Sort">
              <IconButton
                onClick={(e) => setSortAnchor(e.currentTarget)}
                sx={{ border: "1px solid", borderColor: "divider", borderRadius: 2 }}
              >
                <SortIcon fontSize="small" />
              </IconButton>
            </Tooltip>

            <Menu
              anchorEl={sortAnchor}
              open={Boolean(sortAnchor)}
              onClose={() => setSortAnchor(null)}
            >
              {[
                { label: "Date Created", value: "created_at" },
                { label: "Due Date", value: "due_date" },
                { label: "Priority", value: "priority" },
                { label: "Title (A-Z)", value: "title" },
              ].map((s) => (
                <MenuItem
                  key={s.value}
                  selected={sortBy === s.value}
                  onClick={() => {
                    setSortBy(s.value);
                    setSortAnchor(null);
                  }}
                >
                  {s.label}
                </MenuItem>
              ))}
            </Menu>
          </Box>

          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1, mb: 3 }}>
            {CATEGORIES.map((cat) => (
              <Chip
                key={cat}
                label={cat}
                onClick={() => setActiveCategory(cat)}
                variant={activeCategory === cat ? "filled" : "outlined"}
                color={activeCategory === cat ? "primary" : "default"}
                sx={{ borderRadius: 50, fontWeight: activeCategory === cat ? 600 : 400 }}
              />
            ))}
          </Box>

          {loading ? (
            <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
              <CircularProgress size={32} />
            </Box>
          ) : filtered.length === 0 ? (
            <Box sx={{ textAlign: "center", py: 8, color: "text.secondary" }}>
              <Typography fontSize={40} mb={1}>📋</Typography>
              <Typography fontWeight={500}>No tasks found in this category.</Typography>
              <Typography variant="body2" mt={0.5}>Add one using the button above.</Typography>
            </Box>
          ) : (
            <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5, overflowY: "auto", pr: 1, pb: 8, maxHeight: "100%", "&::-webkit-scrollbar": { width: 8 }, "&::-webkit-scrollbar-track": { background: "rgba(0,0,0,0.04)", borderRadius: 10 }, "&::-webkit-scrollbar-thumb": { background: "rgba(255,79,139,0.45)", borderRadius: 10 }, "&::-webkit-scrollbar-thumb:hover": { background: "rgba(255,79,139,0.7)" } }}>
              {filtered.map((task) => {
                const done = task.status === "completed";
                const over = isOverdue(task);

                return (
                  <Paper
                    key={task.id}
                    variant="outlined"
                    sx={{
                      p: 2,
                      borderRadius: 2.5,
                      borderColor: over ? "error.main" : done ? "success.light" : "divider",
                      opacity: done ? 0.7 : 1,
                      transition: "all 0.2s",
                      "&:hover": { boxShadow: 2 },
                    }}
                  >
                    <Box sx={{ display: "flex", alignItems: "flex-start", gap: 1.5 }}>
                      <IconButton size="small" onClick={() => toggleComplete(task)} sx={{ mt: 0.3 }}>
                        {done ? (
                          <CheckCircleIcon fontSize="small" color="success" />
                        ) : (
                          <RadioButtonUncheckedIcon fontSize="small" sx={{ color: "text.disabled" }} />
                        )}
                      </IconButton>

                      <Box sx={{ flex: 1, minWidth: 0 }}>
                        <Box sx={{ display: "flex", alignItems: "center", gap: 1, flexWrap: "wrap" }}>
                          <Typography
                            fontWeight={500}
                            sx={{
                              textDecoration: done ? "line-through" : "none",
                              color: done ? "text.disabled" : "text.primary",
                            }}
                          >
                            {task.title}
                          </Typography>

                          <Chip
                            label={task.category}
                            size="small"
                            sx={{ borderRadius: 50, fontSize: 11, height: 20 }}
                          />

                          {task.synced_from === "classroom" && (
                            <Chip
                              label="📚 Classroom"
                              size="small"
                              sx={{
                                borderRadius: 50,
                                fontSize: 11,
                                height: 20,
                                bgcolor: "#4285F422",
                                color: "#4285F4",
                                fontWeight: 600,
                              }}
                            />
                          )}

                          <Box
                            sx={{
                              width: 8,
                              height: 8,
                              borderRadius: "50%",
                              bgcolor: PRIORITY_COLOR[task.priority] || "#999",
                              flexShrink: 0,
                            }}
                          />

                          {over && (
                            <Chip
                              label="Overdue"
                              size="small"
                              color="error"
                              sx={{ borderRadius: 50, fontSize: 11, height: 20 }}
                            />
                          )}
                        </Box>

                        {task.description && (
                          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.3, fontSize: 13 }} noWrap>
                            {task.description}
                          </Typography>
                        )}

                        {task.due_date && (
                          <Box sx={{ display: "flex", alignItems: "center", gap: 0.5, mt: 0.5 }}>
                            <CalendarTodayIcon sx={{ fontSize: 12, color: over ? "error.main" : "text.disabled" }} />
                            <Typography variant="caption" color={over ? "error.main" : "text.disabled"}>
                              {formatTaskDate(task.due_date)}
                            </Typography>
                          </Box>
                        )}
                      </Box>

                      <Box sx={{ display: "flex", gap: 0.5, flexShrink: 0 }}>
                        <Tooltip title="Edit">
                          <IconButton
                            size="small"
                            onClick={() => {
                              setEditTask(task);
                              setModalOpen(true);
                            }}
                          >
                            <EditIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>

                        <Tooltip title="Delete">
                          <IconButton size="small" color="error" onClick={() => deleteTask(task.id)}>
                            <DeleteIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </Box>
                  </Paper>
                );
              })}
            </Box>
          )}

          <Box
            sx={{
              position: "absolute",
              bottom: 24,
              left: "50%",
              transform: "translateX(-50%)",
            }}
          >
            <Tooltip title="Add Task">
              <IconButton
                onClick={() => {
                  setEditTask(null);
                  setModalOpen(true);
                }}
                sx={{
                  width: 48,
                  height: 48,
                  border: "2px solid",
                  borderColor: "primary.main",
                  borderRadius: 2,
                  color: "primary.main",
                  bgcolor: "background.paper",
                  boxShadow: 3,
                  transition: "all 0.2s",
                  "&:hover": {
                    bgcolor: "primary.main",
                    color: "#fff",
                    transform: "translateY(-3px)",
                    boxShadow: 6,
                  },
                }}
              >
                <AddIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Paper>
      </Box>

<Box
  sx={{
    width: { xs: "100%", lg: 420 },
    flex: { xs: "1 1 auto", lg: "0 0 420px" },
    minWidth: 0,
    display: "flex",
    flexDirection: { xs: "column", md: "row", lg: "column" },
    gap: { xs: 2, md: 3 },
  }}
>        <Paper sx={{ p: 3, borderRadius: 3, minHeight: 280 }}>
          <Typography variant="h6" fontWeight={600} mb={2} sx={{ fontFamily: "'Playfair Display', serif" }}>
            Category Mix
          </Typography>

          {categoryData.length === 0 ? (
            <Box sx={{ textAlign: "center", py: 4, color: "text.secondary" }}>
              <CircularProgress variant="determinate" value={0} size={48} sx={{ mb: 1.5, opacity: 0.3 }} />
              <Typography variant="body2">No tasks yet.</Typography>
              <Typography variant="caption">Add a task to see the category mix.</Typography>
            </Box>
          ) : (
            <ResponsiveContainer width="100%" height={180}>
              <PieChart>
                <Pie data={categoryData} cx="50%" cy="50%" innerRadius={45} outerRadius={70} dataKey="value" paddingAngle={3}>
                  {categoryData.map((_, i) => (
                    <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                  ))}
                </Pie>
                <ReTooltip />
                <Legend iconType="circle" iconSize={8} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </Paper>

        <Paper
          sx={{
            p: 3,
            borderRadius: 4,
            flexGrow: 1,
            background:
              "linear-gradient(180deg, rgba(255,255,255,0.95) 0%, rgba(255,248,250,0.98) 100%)",
            boxShadow: "0 8px 24px rgba(0,0,0,0.06)",
            border: "1px solid rgba(255,255,255,0.5)",
            backdropFilter: "blur(10px)",
          }}
        >
          <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 1.5 }}>
            <Typography variant="h6" fontWeight={600} sx={{ fontFamily: "'Playfair Display', serif" }}>
              Progress
            </Typography>

            <Typography variant="body2" color="text.secondary" fontWeight={500}>
              {progress}%
            </Typography>
          </Box>

          <LinearProgress
              variant="determinate"
              value={progress}
              sx={{
                borderRadius: 999,
                height: 10,
                mb: 3,
                bgcolor: "rgba(0,0,0,0.06)",
                "& .MuiLinearProgress-bar": {
                  borderRadius: 999,
                  background: "linear-gradient(90deg, #ff4f8b, #ff7eb3)",
                },
              }}
            />

          <Grid container spacing={2}>
            {[
              { label: "Total", value: total, icon: "📋", color: "primary.main" },
              { label: "Pending", value: pending, icon: "🕐", color: "text.secondary" },
              { label: "Completed", value: completed, icon: "✅", color: "success.main" },
              { label: "Overdue", value: overdue, icon: "⚠️", color: "error.main" },
            ].map((stat) => (
              <Grid item xs={6} key={stat.label}>
                <Paper variant="outlined" sx={{
                    p: 2,
                    borderRadius: 3,
                    textAlign: "center",
                    transition: "all 0.2s ease",
                    cursor: "default",
                    bgcolor: "background.paper",
                    "&:hover": {
                      transform: "translateY(-4px)",
                      boxShadow: 4,
                    },
                  }}
                >
                  <Typography fontSize={20}>{stat.icon}</Typography>
                  <Typography variant="h6" fontWeight={600} color={stat.color}>
                    {stat.value}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {stat.label}
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>

          <Box sx={{ display: "flex", gap: 1, mt: 2 }}>
            <Button fullWidth variant="outlined" size="small" sx={{ borderRadius: 50 }} component={Link} to="/calendar">
              Open Calendar
            </Button>

            <Button fullWidth variant="outlined" size="small" sx={{ borderRadius: 50 }} component={Link} to="/settings">
              Settings
            </Button>
          </Box>
        </Paper>
      </Box>

      <Dialog
        open={printOpen}
        onClose={() => setPrintOpen(false)}
        maxWidth="xs"
        fullWidth
        PaperProps={{ sx: { borderRadius: 3 } }}
      >
        <DialogTitle sx={{ fontWeight: 600, fontFamily: "'Playfair Display', serif" }}>
          Export as PDF
        </DialogTitle>

        <DialogContent>
          <Typography variant="body2" color="text.secondary" mb={2}>
            Choose which tasks to include in the report:
          </Typography>

          <RadioGroup value={printScope} onChange={(e) => setPrintScope(e.target.value)}>
            <FormControlLabel
              value="current"
              control={<Radio />}
              label={`Current view - "${activeCategory}"${search ? ` + search "${search}"` : ""} (${filtered.length} tasks)`}
            />

            <FormControlLabel
              value="all"
              control={<Radio />}
              label={`All tasks (${tasks.length} tasks)`}
            />
          </RadioGroup>
        </DialogContent>

        <DialogActions sx={{ px: 3, pb: 3, gap: 1 }}>
          <Button onClick={() => setPrintOpen(false)} sx={{ borderRadius: 50 }}>
            Cancel
          </Button>

          <Button
            onClick={handlePrint}
            variant="contained"
            startIcon={<PictureAsPdfIcon />}
            sx={{ borderRadius: 50, px: 3 }}
          >
            Export
          </Button>
        </DialogActions>
      </Dialog>

      <TaskModal
        open={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setEditTask(null);
        }}
        onSave={handleSave}
        editTask={editTask}
      />

      <Snackbar
        open={snack.open}
        autoHideDuration={3000}
        onClose={() => setSnack((s) => ({ ...s, open: false }))}
        anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
      >
        <Alert
          severity={snack.severity}
          sx={{ borderRadius: 2 }}
          onClose={() => setSnack((s) => ({ ...s, open: false }))}
        >
          {snack.msg}
        </Alert>
      </Snackbar>
    </Box>
  );
}