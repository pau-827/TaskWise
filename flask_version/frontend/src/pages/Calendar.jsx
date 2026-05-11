import { useState, useEffect, useContext, useCallback } from "react";
import {
  Box, Paper, Typography, IconButton, Chip, CircularProgress, Tooltip,
  Checkbox, Divider, TextField, Button,
} from "@mui/material";
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import TodayIcon from "@mui/icons-material/Today";
import FlagIcon from "@mui/icons-material/Flag";
import SyncIcon from "@mui/icons-material/Sync";
import CalendarMonthIcon from "@mui/icons-material/CalendarMonth";
import EventNoteIcon from "@mui/icons-material/EventNote";
import DeleteIcon from "@mui/icons-material/Delete";
import { supabase } from "../services/supabase";
import { AppContext } from "../context/AppContext";
import { ThemeContext } from "../context/ThemeContext";
import { THEMES } from "../theme/themes";

const WEEKDAYS = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"];
const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
const STATUS_COLOR = { completed: "#4CAF50", pending: "#f4a261", overdue: "#e53935" };
const HOLIDAY_COLOR = "#e53935";

function isOverdue(task) {
  if (!task.due_date || task.status === "completed") return false;
  return new Date(task.due_date) < new Date();
}

function isSameDay(a, b) {
  return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate();
}

function formatTime(value) {
  return new Date(value).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function getTodayKey() {
  return new Date().toISOString().slice(0, 10);
}

export default function Calendar() {
  const { user } = useContext(AppContext);
  const { themeName } = useContext(ThemeContext);

  const palette = THEMES[themeName]?.palette;
  const isDark = palette?.mode === "dark";
  const bgPaper = palette?.background?.paper ?? "#fff1f5";
  const primary = palette?.primary?.main ?? "#ff4f8b";
  const textMain = palette?.text?.primary ?? "#4a001f";
  const textMuted = palette?.text?.secondary ?? "#9b4b66";
  const borderCol = isDark ? "rgba(255,255,255,0.16)" : "rgba(255,79,139,0.18)";
  const selectedBg = isDark ? "rgba(125,184,210,0.35)" : primary + "22";
  const gcalColor = "#4285F4";

  const cardBg = isDark ? "rgba(255,255,255,0.08)" : "rgba(255,255,255,0.65)";
  const softCardBg = isDark ? "rgba(255,255,255,0.10)" : "rgba(255,255,255,0.75)";
  const inputBg = isDark ? "rgba(255,255,255,0.12)" : "rgba(255,255,255,0.7)";
  const cardText = isDark ? "#ffffff" : textMain;
  const shadow = isDark ? "0 8px 24px rgba(0,0,0,0.38)" : "0 8px 24px rgba(0,0,0,0.06)";

  const today = new Date();
  const [viewDate, setViewDate] = useState(new Date(today.getFullYear(), today.getMonth(), 1));
  const [selectedDate, setSelectedDate] = useState(today);
  const [tasks, setTasks] = useState([]);
  const [gcalEvents, setGcalEvents] = useState([]);
  const [holidays, setHolidays] = useState([]);
  const [loadingTasks, setLoadingTasks] = useState(true);
  const [loadingGcal, setLoadingGcal] = useState(false);
  const [gcalConnected, setGcalConnected] = useState(false);
  const [snackMsg, setSnackMsg] = useState("");
  const [todoInput, setTodoInput] = useState("");
  const [miniTodos, setMiniTodos] = useState([]);

  const year = viewDate.getFullYear();
  const month = viewDate.getMonth();

  const todoStorageKey = `taskwise_todo_today_${user?.id || "guest"}_${getTodayKey()}`;

  useEffect(() => {
    const saved = localStorage.getItem(todoStorageKey);
    setMiniTodos(saved ? JSON.parse(saved) : []);
  }, [todoStorageKey]);

  useEffect(() => {
    localStorage.setItem(todoStorageKey, JSON.stringify(miniTodos));
  }, [miniTodos, todoStorageKey]);

  const fetchTasks = useCallback(async () => {
    if (!user) return;
    setLoadingTasks(true);

    const { data } = await supabase
      .from("tasks")
      .select("*")
      .eq("user_id", user.id);

    setTasks(data || []);
    setLoadingTasks(false);
  }, [user]);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const fetchGcalEvents = useCallback(async () => {
    const {
      data: { session },
    } = await supabase.auth.getSession();

    const token = session?.provider_token;

    if (!token) {
      setGcalConnected(false);
      return;
    }

    setGcalConnected(true);
    setLoadingGcal(true);

    try {
      const now = new Date();
      const timeMin = new Date(now.getFullYear(), now.getMonth() - 1, 1).toISOString();
      const timeMax = new Date(now.getFullYear(), now.getMonth() + 3, 0).toISOString();

      const res = await fetch(
        `https://www.googleapis.com/calendar/v3/calendars/primary/events?timeMin=${timeMin}&timeMax=${timeMax}&singleEvents=true&orderBy=startTime&maxResults=100`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (!res.ok) {
        setGcalConnected(false);
        setLoadingGcal(false);
        return;
      }

      const data = await res.json();

      const events = (data.items || [])
        .map((e) => {
          const start = e.start?.dateTime || e.start?.date;
          const due_date = start ? new Date(start) : null;

          return {
            id: e.id,
            title: e.summary || "Untitled Event",
            description: e.description || "",
            due_date,
            link: e.htmlLink || "",
            isGcal: true,
          };
        })
        .filter((e) => e.due_date);

      setGcalEvents(events);
    } catch (err) {
      console.error("GCal fetch error:", err);
      setGcalConnected(false);
    }

    setLoadingGcal(false);
  }, []);

  useEffect(() => {
    fetchGcalEvents();
  }, [fetchGcalEvents]);

  const fetchHolidays = useCallback(async (yr) => {
    try {
      const res = await fetch(`https://date.nager.at/api/v3/PublicHolidays/${yr}/PH`);
      if (!res.ok) return;

      const data = await res.json();

      setHolidays((prev) => {
        const existing = new Set(prev.map((h) => h.date));
        const newOnes = data.filter((h) => !existing.has(h.date));
        return [...prev, ...newOnes];
      });
    } catch (err) {
      console.error("Holiday fetch error:", err);
    }
  }, []);

  useEffect(() => {
    fetchHolidays(year);
    fetchHolidays(year + 1);
  }, [year, fetchHolidays]);

  const tasksForDate = (date) => tasks.filter((t) => t.due_date && isSameDay(new Date(t.due_date), date));
  const gcalForDate = (date) => gcalEvents.filter((e) => isSameDay(e.due_date, date));
  const allForDate = (date) => [...tasksForDate(date), ...gcalForDate(date)];

  const holidayForDate = (date) => {
    const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
    return holidays.find((h) => h.date === key) || null;
  };

  const monthTasks = tasks.filter((t) => {
    if (!t.due_date) return false;
    const d = new Date(t.due_date);
    return d.getFullYear() === year && d.getMonth() === month;
  });

  const monthGcal = gcalEvents.filter((e) => e.due_date.getFullYear() === year && e.due_date.getMonth() === month);

  const monthHolidays = holidays.filter((h) => {
    const d = new Date(h.date);
    return d.getFullYear() === year && d.getMonth() === month;
  });

  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const calCells = [];

  for (let i = 0; i < firstDay; i++) calCells.push(null);
  for (let d = 1; d <= daysInMonth; d++) calCells.push(new Date(year, month, d));

  const selectedItems = allForDate(selectedDate);
  const selectedHoliday = holidayForDate(selectedDate);

  const goToday = () => {
    const now = new Date();
    setSelectedDate(now);
    setViewDate(new Date(now.getFullYear(), now.getMonth(), 1));
  };

  const addMiniTodo = () => {
    if (!todoInput.trim()) return;
    setMiniTodos((prev) => [...prev, { id: Date.now(), title: todoInput.trim(), done: false }]);
    setTodoInput("");
  };

  const toggleMiniTodo = (id) => {
    setMiniTodos((prev) => prev.map((t) => (t.id === id ? { ...t, done: !t.done } : t)));
  };

  const deleteMiniTodo = (id) => {
    setMiniTodos((prev) => prev.filter((t) => t.id !== id));
  };

  return (
    <Box sx={{ width: "100%", display: "flex", flexDirection: { xs: "column", xl: "row" }, gap: { xs: 2, md: 3 }, alignItems: "stretch", minHeight: "calc(100vh - 88px)" }}>
      <Box sx={{ width: { xs: "100%", xl: 320 }, flex: { xs: "1 1 auto", xl: "0 0 320px" }, display: "flex", flexDirection: { xs: "column", md: "row", xl: "column" }, gap: 2 }}>
        <Paper sx={{ p: 3, borderRadius: 4, bgcolor: bgPaper, boxShadow: shadow, flex: 1 }}>
          <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", mb: 2 }}>
            <Box>
              <Typography variant="h5" fontWeight={700} color={textMain} sx={{ fontFamily: "'Playfair Display', serif" }}>
                {selectedDate.toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })}
              </Typography>
              <Typography variant="body2" color={textMuted} mt={0.5}>
                Selected Schedule
              </Typography>
            </Box>

            <Chip label="Today" size="small" onClick={goToday} sx={{ borderRadius: 50, bgcolor: primary, color: "#fff", cursor: "pointer", fontWeight: 700 }} />
          </Box>

          <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap", mb: 2 }}>
            {selectedHoliday ? (
              <Chip label={`🇵🇭 ${selectedHoliday.name}`} size="small" sx={{ borderRadius: 50, bgcolor: HOLIDAY_COLOR + "22", color: HOLIDAY_COLOR, fontWeight: 700 }} />
            ) : (
              <Chip label="No holiday" size="small" sx={{ borderRadius: 50, bgcolor: isDark ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.06)", color: textMuted }} />
            )}

            <Chip label={`${tasksForDate(selectedDate).length} task(s)`} size="small" sx={{ borderRadius: 50, bgcolor: primary + "22", color: primary, fontWeight: 700 }} />

            {gcalConnected && (
              <Chip label={`${gcalForDate(selectedDate).length} GCal event(s)`} size="small" sx={{ borderRadius: 50, bgcolor: gcalColor + "22", color: gcalColor, fontWeight: 700 }} />
            )}
          </Box>

          <Box sx={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 1.5 }}>
            {[
              { icon: <TodayIcon sx={{ fontSize: 20 }} />, label: "Today", value: tasksForDate(today).length },
              { icon: <CalendarMonthIcon sx={{ fontSize: 20 }} />, label: "Month", value: monthTasks.length },
              { icon: <FlagIcon sx={{ fontSize: 20 }} />, label: "Holidays", value: monthHolidays.length },
            ].map((s) => (
              <Paper key={s.label} variant="outlined" sx={{ p: 1.5, borderRadius: 3, textAlign: "center", borderColor: borderCol, bgcolor: cardBg }}>
                <Box sx={{ color: primary, mb: 0.5 }}>{s.icon}</Box>
                <Typography fontWeight={800} fontSize={20} color={cardText}>
                  {s.value}
                </Typography>
                <Typography variant="caption" color={textMuted}>
                  {s.label}
                </Typography>
              </Paper>
            ))}
          </Box>
        </Paper>

        <Paper sx={{ p: 3, borderRadius: 4, bgcolor: bgPaper, flexGrow: 1, boxShadow: shadow, flex: 1 }}>
          <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
            <Typography fontWeight={700} color={textMain} sx={{ fontFamily: "'Playfair Display', serif" }}>
              On This Day
            </Typography>

            {gcalConnected && (
              <Tooltip title="Refresh Google Calendar">
                <IconButton size="small" onClick={fetchGcalEvents} disabled={loadingGcal}>
                  <SyncIcon fontSize="small" sx={{ animation: loadingGcal ? "spin 1s linear infinite" : "none", "@keyframes spin": { "100%": { transform: "rotate(360deg)" } } }} />
                </IconButton>
              </Tooltip>
            )}
          </Box>

          {!gcalConnected && (
            <Box sx={{ p: 2, borderRadius: 3, bgcolor: gcalColor + "11", border: `1px solid ${gcalColor}33`, mb: 2 }}>
              <Typography fontSize={12} color={gcalColor} fontWeight={600}>
                Log in with Google to see Google Calendar events here.
              </Typography>
            </Box>
          )}

          {loadingTasks ? (
            <Box sx={{ display: "flex", justifyContent: "center", py: 5 }}>
              <CircularProgress size={28} />
            </Box>
          ) : (
            <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5, maxHeight: 430, overflowY: "auto", pr: 0.5, scrollbarWidth: "thin", scrollbarColor: `${primary}88 rgba(0,0,0,0.04)`, "&::-webkit-scrollbar": { width: 8 }, "&::-webkit-scrollbar-track": { background: "rgba(0,0,0,0.04)", borderRadius: 10 }, "&::-webkit-scrollbar-thumb": { background: primary + "88", borderRadius: 10 } }}>
              {selectedHoliday && (
                <Paper variant="outlined" sx={{ p: 2, borderRadius: 3, borderColor: HOLIDAY_COLOR + "55", bgcolor: isDark ? "rgba(229,57,53,0.14)" : HOLIDAY_COLOR + "08" }}>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <Typography fontSize={18}>🇵🇭</Typography>
                    <Box>
                      <Typography fontWeight={700} fontSize={14} color={HOLIDAY_COLOR}>
                        {selectedHoliday.name}
                      </Typography>
                      <Typography variant="caption" color={textMuted}>
                        Philippine Public Holiday
                      </Typography>
                    </Box>
                  </Box>
                </Paper>
              )}

              {selectedItems.length === 0 && !selectedHoliday && (
                <Box sx={{ textAlign: "center", py: 6, color: textMuted }}>
                  <Typography fontSize={36} mb={1}>
                    📭
                  </Typography>
                  <Typography variant="body2">Nothing scheduled for this day.</Typography>
                </Box>
              )}

              {selectedItems.map((item, i) => {
                const isGcal = item.isGcal;
                const over = !isGcal && isOverdue(item);
                const status = isGcal ? "gcal" : item.status === "completed" ? "completed" : over ? "overdue" : "pending";
                const dotColor = isGcal ? gcalColor : STATUS_COLOR[status] || STATUS_COLOR.pending;

                return (
                  <Paper key={item.id || i} variant="outlined" sx={{ p: 2, borderRadius: 3, borderColor: isGcal ? gcalColor + "44" : borderCol, bgcolor: softCardBg }}>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                      <Box sx={{ width: 9, height: 9, borderRadius: "50%", bgcolor: dotColor }} />
                      <Typography fontWeight={700} fontSize={14} color={cardText} sx={{ textDecoration: item.status === "completed" ? "line-through" : "none" }}>
                        {item.title}
                      </Typography>
                    </Box>

                    {item.description && (
                      <Typography variant="caption" color={textMuted} display="block" mt={0.7} noWrap>
                        {item.description}
                      </Typography>
                    )}

                    <Box sx={{ display: "flex", gap: 1, mt: 1, flexWrap: "wrap" }}>
                      <Chip label={isGcal ? "Google Calendar" : item.category} size="small" sx={{ borderRadius: 50, height: 22, fontSize: 11, bgcolor: isGcal ? gcalColor + "22" : primary + "22", color: isGcal ? gcalColor : primary, fontWeight: 700 }} />

                      {item.due_date && (
                        <Chip label={formatTime(item.due_date)} size="small" sx={{ borderRadius: 50, height: 22, fontSize: 11, bgcolor: borderCol, color: textMuted }} />
                      )}

                      {isGcal && item.link && (
                        <Chip label="Open" size="small" onClick={() => window.open(item.link, "_blank")} sx={{ borderRadius: 50, height: 22, fontSize: 11, bgcolor: gcalColor + "22", color: gcalColor, cursor: "pointer" }} />
                      )}
                    </Box>
                  </Paper>
                );
              })}
            </Box>
          )}
        </Paper>
      </Box>

      <Box sx={{ flex: "1 1 0", minWidth: 0, display: "flex", flexDirection: "column", overflowX: "auto" }}>
        <Paper sx={{ p: 3, borderRadius: 4, bgcolor: bgPaper, flexGrow: 1, display: "flex", flexDirection: "column", boxShadow: shadow }}>
          <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", mb: 3 }}>
            <IconButton onClick={() => setViewDate(new Date(year, month - 1, 1))} sx={{ bgcolor: isDark ? "rgba(255,255,255,0.07)" : "rgba(0,0,0,0.05)", borderRadius: 3 }}>
              <ChevronLeftIcon />
            </IconButton>

            <Box sx={{ textAlign: "center" }}>
              <Typography fontWeight={800} fontSize={20} color={textMain} letterSpacing={1}>
                {MONTHS[month].toUpperCase()} {year}
              </Typography>

              <Box sx={{ display: "flex", justifyContent: "center", gap: 1, mt: 1, flexWrap: "wrap" }}>
                <Chip label={`${monthTasks.length} task(s)`} size="small" sx={{ borderRadius: 50, bgcolor: primary + "22", color: primary, fontWeight: 700 }} />

                {monthHolidays.length > 0 && (
                  <Chip label={`${monthHolidays.length} holiday(s)`} size="small" sx={{ borderRadius: 50, bgcolor: HOLIDAY_COLOR + "22", color: HOLIDAY_COLOR, fontWeight: 700 }} />
                )}

                {gcalConnected && (
                  <Chip label={`${monthGcal.length} event(s)`} size="small" sx={{ borderRadius: 50, bgcolor: gcalColor + "22", color: gcalColor, fontWeight: 700 }} />
                )}
              </Box>
            </Box>

            <IconButton onClick={() => setViewDate(new Date(year, month + 1, 1))} sx={{ bgcolor: isDark ? "rgba(255,255,255,0.07)" : "rgba(0,0,0,0.05)", borderRadius: 3 }}>
              <ChevronRightIcon />
            </IconButton>
          </Box>

          <Box sx={{ display: "grid", gridTemplateColumns: "repeat(7, minmax(90px, 1fr))", mb: 1, minWidth: 700 }}>
            {WEEKDAYS.map((d) => (
              <Typography key={d} align="center" variant="caption" fontWeight={800} color={textMuted} letterSpacing={1} fontSize={11}>
                {d}
              </Typography>
            ))}
          </Box>

          <Box sx={{ display: "grid", gridTemplateColumns: "repeat(7, minmax(90px, 1fr))", gap: 1, flexGrow: 1, minWidth: 700 }}>
            {calCells.map((date, i) => {
              if (!date) return <Box key={`empty-${i}`} />;

              const isToday = isSameDay(date, today);
              const isSelected = isSameDay(date, selectedDate);
              const hasTask = tasksForDate(date).length > 0;
              const hasGcal = gcalForDate(date).length > 0;
              const holiday = holidayForDate(date);

              const tooltipParts = [];
              if (holiday) tooltipParts.push(`🇵🇭 ${holiday.name}`);
              if (tasksForDate(date).length > 0) tooltipParts.push(`${tasksForDate(date).length} task(s)`);
              if (gcalForDate(date).length > 0) tooltipParts.push(`${gcalForDate(date).length} event(s)`);

              return (
                <Tooltip key={date.toISOString()} title={tooltipParts.join(" · ") || ""} placement="top">
                  <Box
                    onClick={() => setSelectedDate(date)}
                    sx={{
                      minHeight: { xs: 72, sm: 90, md: 110 },
                      p: 1.2,
                      borderRadius: 3,
                      cursor: "pointer",
                      position: "relative",
                      border: `1px solid ${holiday && !isToday ? HOLIDAY_COLOR + "55" : isSelected ? primary : borderCol}`,
                      bgcolor: isToday ? primary : isSelected ? selectedBg : cardBg,
                      transition: "all 0.18s ease",
                      "&:hover": {
                        transform: "translateY(-3px)",
                        boxShadow: isDark ? "0 8px 18px rgba(0,0,0,0.4)" : 3,
                        bgcolor: isToday ? primary : isDark ? "rgba(255,255,255,0.14)" : primary + "14",
                      },
                    }}
                  >
                    <Typography fontSize={14} fontWeight={isToday || isSelected ? 800 : 600} color={isToday ? "#fff" : holiday ? HOLIDAY_COLOR : cardText}>
                      {date.getDate()}
                    </Typography>

                    <Box sx={{ position: "absolute", bottom: 10, left: 10, display: "flex", gap: 0.5, alignItems: "center" }}>
                      {holiday && <Box sx={{ width: 7, height: 7, borderRadius: "50%", bgcolor: isToday ? "#fff" : HOLIDAY_COLOR }} />}

                      {hasTask && (
                        <Tooltip title="Has Task">
                          <EventNoteIcon sx={{ fontSize: 13, color: isToday ? "#fff" : "#4CAF50" }} />
                        </Tooltip>
                      )}

                      {hasGcal && <Box sx={{ width: 7, height: 7, borderRadius: "50%", bgcolor: isToday ? "#fff" : gcalColor }} />}
                    </Box>
                  </Box>
                </Tooltip>
              );
            })}
          </Box>

          <Box sx={{ display: "flex", gap: 2.5, mt: 2, justifyContent: "center", flexWrap: "wrap" }}>
            {[
              { color: HOLIDAY_COLOR, label: "PH Holiday" },
              { color: "#4CAF50", label: "Has Tasks" },
              { color: gcalColor, label: "GCal Event" },
              { color: primary, label: "Today" },
              { color: primary + "55", label: "Selected" },
            ].map((l) => (
              <Box key={l.label} sx={{ display: "flex", alignItems: "center", gap: 0.6 }}>
                <Box sx={{ width: 8, height: 8, borderRadius: "50%", bgcolor: l.color }} />
                <Typography variant="caption" color={textMuted} fontSize={11}>
                  {l.label}
                </Typography>
              </Box>
            ))}

            {!gcalConnected && (
              <Typography variant="caption" color={gcalColor} fontSize={11} fontStyle="italic">
                📅 Log in with Google to see GCal events
              </Typography>
            )}
          </Box>
        </Paper>
      </Box>

      <Box sx={{ width: { xs: "100%", xl: 300 }, flex: { xs: "1 1 auto", xl: "0 0 300px" }, display: "flex", alignSelf: "stretch" }}>
        <Paper sx={{ p: 3, borderRadius: 4, bgcolor: bgPaper, boxShadow: shadow, height: "95%", display: "flex", flexDirection: "column" }}>
          <Typography fontWeight={800} color={textMain} sx={{ fontFamily: "'Playfair Display', serif" }}>
            To-do Today
          </Typography>

          <Typography variant="body2" color={textMuted} mt={0.5} mb={2}>
            Minor checklist for today
          </Typography>

          <Box sx={{ display: "flex", gap: 1, mb: 2 }}>
            <TextField
              size="small"
              fullWidth
              placeholder="Add mini task..."
              value={todoInput}
              onChange={(e) => setTodoInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") addMiniTodo();
              }}
              sx={{
                "& .MuiOutlinedInput-root": {
                  borderRadius: 3,
                  bgcolor: inputBg,
                },
              }}
            />

            <Button variant="contained" onClick={addMiniTodo} sx={{ minWidth: 44, borderRadius: 3, fontWeight: 800 }}>
              +
            </Button>
          </Box>

          <Divider sx={{ mb: 2 }} />

          {miniTodos.length === 0 ? (
            <Box sx={{ textAlign: "center", py: 5, color: textMuted }}>
              <Typography fontSize={34} mb={1}>
                ✅
              </Typography>
              <Typography variant="body2">No mini tasks yet.</Typography>
            </Box>
          ) : (
          <Box sx={{ flex: 1, minHeight: 0, overflowY: "auto", pr: 0.8, pb: 1, display: "flex", flexDirection: "column", gap: 1.2, bgcolor: isDark ? "rgba(255,255,255,0.04)" : "rgba(255,255,255,0.25)", borderRadius: 3, scrollbarWidth: "thin", scrollbarColor: `${primary}88 transparent`, "&::-webkit-scrollbar": { width: 8 }, "&::-webkit-scrollbar-track": { background: "transparent", borderRadius: 10 }, "&::-webkit-scrollbar-thumb": { background: primary + "88", borderRadius: 10 }, "&::-webkit-scrollbar-thumb:hover": { background: primary } }}>              {miniTodos.map((todo) => (
                <Paper key={todo.id} variant="outlined" sx={{ px: 1.5, py: 1.4, minHeight: 56, flexShrink: 0, borderRadius: 3, display: "flex", alignItems: "center", gap: 1, bgcolor: softCardBg, borderColor: todo.done ? "#4CAF50" : borderCol, boxShadow: isDark ? "0 4px 10px rgba(0,0,0,0.25)" : "0 3px 8px rgba(0,0,0,0.05)"  }}>
                  <Checkbox checked={todo.done} onChange={() => toggleMiniTodo(todo.id)} size="small" sx={{ p: 0.2, color: primary }} />

                  <Typography fontWeight={700} fontSize={13} color={todo.done ? textMuted : cardText} sx={{ flex: 1, textDecoration: todo.done ? "line-through" : "none", wordBreak: "break-word" }}>
                    {todo.title}
                  </Typography>

                  <IconButton size="small" color="error" onClick={() => deleteMiniTodo(todo.id)}>
                    <DeleteIcon sx={{ fontSize: 16 }} />
                  </IconButton>
                </Paper>
              ))}
            </Box>
          )}
        </Paper>
      </Box>

      {snackMsg && (
        <Box sx={{ position: "fixed", bottom: 24, right: 24, zIndex: 9999, bgcolor: primary, color: "#fff", px: 3, py: 1.5, borderRadius: 2, boxShadow: 4, fontSize: 14 }}>
          {snackMsg}
        </Box>
      )}
    </Box>
  );
}