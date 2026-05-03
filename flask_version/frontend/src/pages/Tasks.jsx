import { useState, useEffect, useContext } from "react";
import { Link } from "react-router-dom";
import { ThemeContext } from "../context/ThemeContext";
import { THEMES } from "../theme/themes";
import {
  Box, Grid, Paper, Typography, Button, IconButton, TextField,
  InputAdornment, Chip, CircularProgress, Tooltip, LinearProgress,
  Menu, MenuItem, Dialog, DialogTitle, DialogContent, DialogActions,
  FormControl, InputLabel, Select, Snackbar, Alert,
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import AddIcon from "@mui/icons-material/Add";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import RadioButtonUncheckedIcon from "@mui/icons-material/RadioButtonUnchecked";
import SortIcon from "@mui/icons-material/Sort";
import CalendarTodayIcon from "@mui/icons-material/CalendarToday";
import { PieChart, Pie, Cell, Tooltip as ReTooltip, ResponsiveContainer, Legend } from "recharts";
import { supabase } from "../services/supabase";
import { AppContext } from "../context/AppContext";

const CATEGORIES = ["All Tasks", "Personal", "Work", "Study", "Bills", "Others"];
const PRIORITIES = ["low", "medium", "high"];

const PRIORITY_COLOR = {
  low:    "#4a9b82",
  medium: "#f4a261",
  high:   "#e53935",
};

const STATUS_OPTIONS = ["pending", "completed"];

function isOverdue(task) {
  if (!task.due_date || task.status === "completed") return false;
  return new Date(task.due_date) < new Date();
}

// ── Task Modal ─────────────────────────────────────────────────────────────
function TaskModal({ open, onClose, onSave, editTask, chartColors }) {
  const empty = { title: "", description: "", category: "Personal", priority: "medium", due_date: "", reminder_at: "" };
  const [form, setForm] = useState(empty);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (editTask) {
      setForm({
        title:       editTask.title || "",
        description: editTask.description || "",
        category:    editTask.category || "Personal",
        priority:    editTask.priority || "medium",
        due_date:    editTask.due_date ? editTask.due_date.slice(0, 16) : "",
        reminder_at: editTask.reminder_at ? editTask.reminder_at.slice(0, 16) : "",
      });
    } else {
      setForm(empty);
    }
    setError("");
  }, [editTask, open]);

  const handleSave = async () => {
    if (!form.title.trim()) { setError("Title is required."); return; }
    setLoading(true);
    await onSave(form);
    setLoading(false);
    onClose();
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth
      PaperProps={{ sx: { borderRadius: 3 } }}>
      <DialogTitle sx={{ fontWeight: 600, fontFamily: "'Playfair Display', serif" }}>
        {editTask ? "Edit Task" : "New Task"}
      </DialogTitle>
      <DialogContent sx={{ display: "flex", flexDirection: "column", gap: 2, pt: "12px !important" }}>
        {error && <Alert severity="error" sx={{ borderRadius: 2 }}>{error}</Alert>}

        <TextField
          label="Title" fullWidth required
          value={form.title} onChange={e => setForm({ ...form, title: e.target.value })}
          sx={{ "& .MuiOutlinedInput-root": { borderRadius: 2 } }}
        />

        <TextField
          label="Description" fullWidth multiline rows={3}
          value={form.description} onChange={e => setForm({ ...form, description: e.target.value })}
          sx={{ "& .MuiOutlinedInput-root": { borderRadius: 2 } }}
        />

        <Grid container spacing={2}>
          <Grid item xs={6}>
            <FormControl fullWidth>
              <InputLabel>Category</InputLabel>
              <Select value={form.category} label="Category"
                onChange={e => setForm({ ...form, category: e.target.value })}
                sx={{ borderRadius: 2 }}>
                {CATEGORIES.filter(c => c !== "All Tasks").map(c => (
                  <MenuItem key={c} value={c}>{c}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={6}>
            <FormControl fullWidth>
              <InputLabel>Priority</InputLabel>
              <Select value={form.priority} label="Priority"
                onChange={e => setForm({ ...form, priority: e.target.value })}
                sx={{ borderRadius: 2 }}>
                {PRIORITIES.map(p => (
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

        <TextField
          label="Due Date" type="datetime-local" fullWidth
          InputLabelProps={{ shrink: true }}
          value={form.due_date} onChange={e => setForm({ ...form, due_date: e.target.value })}
          sx={{ "& .MuiOutlinedInput-root": { borderRadius: 2 } }}
        />

        <TextField
          label="Reminder" type="datetime-local" fullWidth
          InputLabelProps={{ shrink: true }}
          value={form.reminder_at} onChange={e => setForm({ ...form, reminder_at: e.target.value })}
          sx={{ "& .MuiOutlinedInput-root": { borderRadius: 2 } }}
        />
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 3, gap: 1 }}>
        <Button onClick={onClose} sx={{ borderRadius: 50 }}>Cancel</Button>
        <Button onClick={handleSave} variant="contained" disabled={loading}
          sx={{ borderRadius: 50, px: 3 }}>
          {loading ? "Saving..." : editTask ? "Save Changes" : "Add Task"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

// ── Main Tasks Page ────────────────────────────────────────────────────────
export default function Tasks() {
  const { user } = useContext(AppContext);
  const { themeName } = useContext(ThemeContext);
  const CHART_COLORS = THEMES[themeName]?.custom?.chartColors ?? ["#4a9b82","#f4a261","#2a9d8f","#e76f51","#a855f7","#3b82f6"];

  const [tasks, setTasks]               = useState([]);
  const [loading, setLoading]           = useState(true);
  const [activeCategory, setActiveCategory] = useState("All Tasks");
  const [search, setSearch]             = useState("");
  const [sortAnchor, setSortAnchor]     = useState(null);
  const [sortBy, setSortBy]             = useState("created_at");
  const [modalOpen, setModalOpen]       = useState(false);
  const [editTask, setEditTask]         = useState(null);
  const [snack, setSnack]               = useState({ open: false, msg: "", severity: "success" });

  // ── Fetch tasks ────────────────────────────────────────────────────────
  const fetchTasks = async () => {
    setLoading(true);
    const { data, error } = await supabase
      .from("tasks")
      .select("*")
      .eq("user_id", user.id)
      .order(sortBy, { ascending: sortBy === "title" });

    if (!error) setTasks(data || []);
    setLoading(false);
  };

  useEffect(() => { if (user) fetchTasks(); }, [user, sortBy]);

  // ── Create / Edit ──────────────────────────────────────────────────────
  const handleSave = async (form) => {
    const payload = {
      ...form,
      user_id:     user.id,
      due_date:    form.due_date    || null,
      reminder_at: form.reminder_at || null,
      status:      editTask?.status || "pending",
    };

    if (editTask) {
      const { error } = await supabase.from("tasks").update(payload).eq("id", editTask.id);
      if (!error) { showSnack("Task updated!"); fetchTasks(); }
      else showSnack(error.message, "error");
    } else {
      const { error } = await supabase.from("tasks").insert(payload);
      if (!error) { showSnack("Task added!"); fetchTasks(); }
      else showSnack(error.message, "error");
    }
  };

  // ── Toggle complete ────────────────────────────────────────────────────
  const toggleComplete = async (task) => {
    const newStatus = task.status === "completed" ? "pending" : "completed";
    const { error } = await supabase.from("tasks").update({ status: newStatus }).eq("id", task.id);
    if (!error) {
      setTasks(prev => prev.map(t => t.id === task.id ? { ...t, status: newStatus } : t));
      showSnack(newStatus === "completed" ? "Task completed! 🎉" : "Marked as pending.");
    }
  };

  // ── Delete ─────────────────────────────────────────────────────────────
  const deleteTask = async (id) => {
    const { error } = await supabase.from("tasks").delete().eq("id", id);
    if (!error) { setTasks(prev => prev.filter(t => t.id !== id)); showSnack("Task deleted."); }
    else showSnack(error.message, "error");
  };

  const showSnack = (msg, severity = "success") => setSnack({ open: true, msg, severity });

  // ── Filtered & searched tasks ──────────────────────────────────────────
  const filtered = tasks.filter(t => {
    const matchCat = activeCategory === "All Tasks" || t.category === activeCategory;
    const matchSearch = t.title.toLowerCase().includes(search.toLowerCase()) ||
                        (t.description || "").toLowerCase().includes(search.toLowerCase());
    return matchCat && matchSearch;
  });

  // ── Stats ──────────────────────────────────────────────────────────────
  const total     = tasks.length;
  const completed = tasks.filter(t => t.status === "completed").length;
  const pending   = tasks.filter(t => t.status === "pending").length;
  const overdue   = tasks.filter(isOverdue).length;
  const progress  = total ? Math.round((completed / total) * 100) : 0;

  // ── Category mix for pie chart ─────────────────────────────────────────
  const categoryData = CATEGORIES.filter(c => c !== "All Tasks").map(cat => ({
    name:  cat,
    value: tasks.filter(t => t.category === cat).length,
  })).filter(d => d.value > 0);

  

  return (
    <Box sx={{ width: "100%" }}>
      <Grid container spacing={3}>

        {/* ── LEFT: Task Panel ────────────────────────────────────────── */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, borderRadius: 3, minHeight: 600 }}>

            {/* Header row */}
            <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
              <Typography variant="h5" sx={{ fontWeight: 600, fontFamily: "'Playfair Display', serif" }}>
                Tasks
              </Typography>
              <Button
                variant="contained" startIcon={<AddIcon />}
                onClick={() => { setEditTask(null); setModalOpen(true); }}
                sx={{ borderRadius: 50, px: 2.5 }}
              >
                Add Task
              </Button>
            </Box>

            {/* Search + Sort */}
            <Box sx={{ display: "flex", gap: 1.5, mb: 2 }}>
              <TextField
                fullWidth size="small" placeholder="Search tasks..."
                value={search} onChange={e => setSearch(e.target.value)}
                InputProps={{
                  startAdornment: <InputAdornment position="start"><SearchIcon fontSize="small" /></InputAdornment>,
                  sx: { borderRadius: 50 },
                }}
              />
              <Tooltip title="Sort">
                <IconButton onClick={e => setSortAnchor(e.currentTarget)}
                  sx={{ border: "1px solid", borderColor: "divider", borderRadius: 2 }}>
                  <SortIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Menu anchorEl={sortAnchor} open={Boolean(sortAnchor)} onClose={() => setSortAnchor(null)}>
                {[
                  { label: "Date Created", value: "created_at" },
                  { label: "Due Date",     value: "due_date" },
                  { label: "Priority",     value: "priority" },
                  { label: "Title (A-Z)",  value: "title" },
                ].map(s => (
                  <MenuItem key={s.value} selected={sortBy === s.value}
                    onClick={() => { setSortBy(s.value); setSortAnchor(null); }}>
                    {s.label}
                  </MenuItem>
                ))}
              </Menu>
            </Box>

            {/* Category filter chips */}
            <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1, mb: 3 }}>
              {CATEGORIES.map(cat => (
                <Chip
                  key={cat} label={cat}
                  onClick={() => setActiveCategory(cat)}
                  variant={activeCategory === cat ? "filled" : "outlined"}
                  color={activeCategory === cat ? "primary" : "default"}
                  sx={{ borderRadius: 50, fontWeight: activeCategory === cat ? 600 : 400 }}
                />
              ))}
            </Box>

            {/* Task list */}
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
              <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5 }}>
                {filtered.map(task => {
                  const done = task.status === "completed";
                  const over = isOverdue(task);
                  return (
                    <Paper key={task.id} variant="outlined" sx={{
                      p: 2, borderRadius: 2.5,
                      borderColor: over ? "error.main" : done ? "success.light" : "divider",
                      opacity: done ? 0.7 : 1,
                      transition: "all 0.2s",
                      "&:hover": { boxShadow: 2 },
                    }}>
                      <Box sx={{ display: "flex", alignItems: "flex-start", gap: 1.5 }}>

                        {/* Complete toggle */}
                        <IconButton size="small" onClick={() => toggleComplete(task)} sx={{ mt: 0.3 }}>
                          {done
                            ? <CheckCircleIcon fontSize="small" color="success" />
                            : <RadioButtonUncheckedIcon fontSize="small" sx={{ color: "text.disabled" }} />
                          }
                        </IconButton>

                        {/* Content */}
                        <Box sx={{ flex: 1, minWidth: 0 }}>
                          <Box sx={{ display: "flex", alignItems: "center", gap: 1, flexWrap: "wrap" }}>
                            <Typography fontWeight={500}
                              sx={{ textDecoration: done ? "line-through" : "none", color: done ? "text.disabled" : "text.primary" }}>
                              {task.title}
                            </Typography>
                            <Chip label={task.category} size="small" sx={{ borderRadius: 50, fontSize: 11, height: 20 }} />
                            <Box sx={{
                              width: 8, height: 8, borderRadius: "50%",
                              bgcolor: PRIORITY_COLOR[task.priority] || "#999",
                              flexShrink: 0,
                            }} />
                            {over && <Chip label="Overdue" size="small" color="error" sx={{ borderRadius: 50, fontSize: 11, height: 20 }} />}
                          </Box>

                          {task.description && (
                            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.3, fontSize: 13 }}
                              noWrap>
                              {task.description}
                            </Typography>
                          )}

                          {task.due_date && (
                            <Box sx={{ display: "flex", alignItems: "center", gap: 0.5, mt: 0.5 }}>
                              <CalendarTodayIcon sx={{ fontSize: 12, color: over ? "error.main" : "text.disabled" }} />
                              <Typography variant="caption" color={over ? "error.main" : "text.disabled"}>
                                {new Date(task.due_date).toLocaleString([], { dateStyle: "medium", timeStyle: "short" })}
                              </Typography>
                            </Box>
                          )}
                        </Box>

                        {/* Actions */}
                        <Box sx={{ display: "flex", gap: 0.5, flexShrink: 0 }}>
                          <Tooltip title="Edit">
                            <IconButton size="small" onClick={() => { setEditTask(task); setModalOpen(true); }}>
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
          </Paper>
        </Grid>

        {/* ── RIGHT: Sidebar ──────────────────────────────────────────── */}
        <Grid item xs={12} md={4}>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>

            {/* Category Mix pie chart */}
            <Paper sx={{ p: 3, borderRadius: 3, minHeight: 260 }}>
              <Typography variant="h6" fontWeight={600} mb={2}
                sx={{ fontFamily: "'Playfair Display', serif" }}>
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
                    <Pie data={categoryData} cx="50%" cy="50%" innerRadius={45} outerRadius={70}
                      dataKey="value" paddingAngle={3}>
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

            {/* Progress summary */}
            <Paper sx={{ p: 3, borderRadius: 3 }}>
              <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 1.5 }}>
                <Typography variant="h6" fontWeight={600} sx={{ fontFamily: "'Playfair Display', serif" }}>
                  Progress
                </Typography>
                <Typography variant="body2" color="text.secondary" fontWeight={500}>
                  {progress}%
                </Typography>
              </Box>

              <LinearProgress variant="determinate" value={progress}
                sx={{ borderRadius: 50, height: 6, mb: 2.5 }} />

              <Grid container spacing={1.5}>
                {[
                  { label: "Total",     value: total,     icon: "📋", color: "primary.main" },
                  { label: "Pending",   value: pending,   icon: "🕐", color: "text.secondary" },
                  { label: "Completed", value: completed, icon: "✅", color: "success.main" },
                  { label: "Overdue",   value: overdue,   icon: "⚠️", color: "error.main" },
                ].map(stat => (
                  <Grid item xs={6} key={stat.label}>
                    <Paper variant="outlined" sx={{ p: 1.5, borderRadius: 2, textAlign: "center" }}>
                      <Typography fontSize={20}>{stat.icon}</Typography>
                      <Typography variant="h6" fontWeight={600} color={stat.color}>{stat.value}</Typography>
                      <Typography variant="caption" color="text.secondary">{stat.label}</Typography>
                    </Paper>
                  </Grid>
                ))}
              </Grid>

              <Box sx={{ display: "flex", gap: 1, mt: 2 }}>
                <Button fullWidth variant="outlined" size="small" sx={{ borderRadius: 50 }}
                  component={Link} to="/calendar">
                  Open Calendar
                </Button>
                <Button fullWidth variant="outlined" size="small" sx={{ borderRadius: 50 }}
                  component={Link} to="/settings">
                  Settings
                </Button>
              </Box>
            </Paper>

          </Box>
        </Grid>
      </Grid>

      {/* Task Modal */}
      <TaskModal
        open={modalOpen}
        onClose={() => { setModalOpen(false); setEditTask(null); }}
        onSave={handleSave}
        editTask={editTask}
      />

      {/* Snackbar */}
      <Snackbar
        open={snack.open} autoHideDuration={3000}
        onClose={() => setSnack(s => ({ ...s, open: false }))}
        anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
      >
        <Alert severity={snack.severity} sx={{ borderRadius: 2 }} onClose={() => setSnack(s => ({ ...s, open: false }))}>
          {snack.msg}
        </Alert>
      </Snackbar>
    </Box>
  );
}
