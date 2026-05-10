import { useState, useEffect, useContext, useCallback } from "react";
import {
  Box, Paper, Typography, IconButton, Chip, CircularProgress, Tooltip, Button,
} from "@mui/material";
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import TodayIcon from "@mui/icons-material/Today";
import FlagIcon from "@mui/icons-material/Flag";
import SyncIcon from "@mui/icons-material/Sync";
import { supabase } from "../services/supabase";
import { AppContext } from "../context/AppContext";
import { ThemeContext } from "../context/ThemeContext";
import { THEMES } from "../theme/themes";

const WEEKDAYS   = ["SUN","MON","TUE","WED","THU","FRI","SAT"];
const MONTHS     = ["January","February","March","April","May","June","July","August","September","October","November","December"];
const STATUS_COLOR = { completed: "#4CAF50", pending: "#f4a261", overdue: "#e53935" };

function isOverdue(task) {
  if (!task.due_date || task.status === "completed") return false;
  return new Date(task.due_date) < new Date();
}

function isSameDay(a, b) {
  return a.getFullYear() === b.getFullYear() &&
         a.getMonth()    === b.getMonth()    &&
         a.getDate()     === b.getDate();
}

export default function Calendar() {
  const { user }       = useContext(AppContext);
  const { themeName }  = useContext(ThemeContext);
  const palette        = THEMES[themeName]?.palette;
  const isDark         = palette?.mode === "dark";
  const bgPaper        = palette?.background?.paper   ?? "#E3F4F4";
  const primary        = palette?.primary?.main       ?? "#4A707A";
  const textMain       = palette?.text?.primary       ?? "#1a3a40";
  const textMuted      = palette?.text?.secondary     ?? "#4A707A";
  const borderCol      = isDark ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.08)";
  const selectedBg     = isDark ? "rgba(255,255,255,0.15)" : primary + "22";
  const gcalColor      = "#4285F4";

  const today = new Date();
  const [viewDate,      setViewDate]      = useState(new Date(today.getFullYear(), today.getMonth(), 1));
  const [selectedDate,  setSelectedDate]  = useState(today);
  const [tasks,         setTasks]         = useState([]);
  const [gcalEvents,    setGcalEvents]    = useState([]);
  const [loadingTasks,  setLoadingTasks]  = useState(true);
  const [loadingGcal,   setLoadingGcal]   = useState(false);
  const [gcalConnected, setGcalConnected] = useState(false);
  const [snackMsg,      setSnackMsg]      = useState("");

  const year  = viewDate.getFullYear();
  const month = viewDate.getMonth();

  // ── Fetch TaskWise tasks ───────────────────────────────────────────────
  const fetchTasks = useCallback(async () => {
    if (!user) return;
    setLoadingTasks(true);
    const { data } = await supabase.from("tasks").select("*").eq("user_id", user.id);
    setTasks(data || []);
    setLoadingTasks(false);
  }, [user]);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { fetchTasks(); }, [fetchTasks]);

  // ── Fetch Google Calendar events ───────────────────────────────────────
  const fetchGcalEvents = useCallback(async () => {
    const { data: { session } } = await supabase.auth.getSession();
    const token = session?.provider_token;
    if (!token) { setGcalConnected(false); return; }

    setGcalConnected(true);
    setLoadingGcal(true);

    try {
      const now      = new Date();
      const timeMin  = new Date(now.getFullYear(), now.getMonth() - 1, 1).toISOString();
      const timeMax  = new Date(now.getFullYear(), now.getMonth() + 3, 0).toISOString();

      const res = await fetch(
        `https://www.googleapis.com/calendar/v3/calendars/primary/events?timeMin=${timeMin}&timeMax=${timeMax}&singleEvents=true&orderBy=startTime&maxResults=100`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (!res.ok) { setGcalConnected(false); setLoadingGcal(false); return; }

      const data   = await res.json();
      const events = (data.items || []).map(e => {
        const start    = e.start?.dateTime || e.start?.date;
        const due_date = start ? new Date(start) : null;
        return {
          id:          e.id,
          title:       e.summary || "Untitled Event",
          description: e.description || "",
          due_date,
          link:        e.htmlLink || "",
          isGcal:      true,
        };
      }).filter(e => e.due_date);

      setGcalEvents(events);
    } catch (err) {
      console.error("GCal fetch error:", err);
      setGcalConnected(false);
    }
    setLoadingGcal(false);
  }, []);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { fetchGcalEvents(); }, [fetchGcalEvents]);

  // ── Helpers ────────────────────────────────────────────────────────────
  const tasksForDate  = (date) => tasks.filter(t => t.due_date && isSameDay(new Date(t.due_date), date));
  const gcalForDate   = (date) => gcalEvents.filter(e => isSameDay(e.due_date, date));
  const allForDate    = (date) => [...tasksForDate(date), ...gcalForDate(date)];

  const monthTasks    = tasks.filter(t => {
    if (!t.due_date) return false;
    const d = new Date(t.due_date);
    return d.getFullYear() === year && d.getMonth() === month;
  });
  const monthGcal     = gcalEvents.filter(e => e.due_date.getFullYear() === year && e.due_date.getMonth() === month);

  // ── Calendar grid ──────────────────────────────────────────────────────
  const firstDay    = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const calCells    = [];
  for (let i = 0; i < firstDay; i++) calCells.push(null);
  for (let d = 1; d <= daysInMonth; d++) calCells.push(new Date(year, month, d));

  const selectedItems = allForDate(selectedDate);

  const showSnack = (msg) => { setSnackMsg(msg); setTimeout(() => setSnackMsg(""), 3000); };

  return (
    <Box sx={{ width: "100%", display: "flex", gap: 3, alignItems: "stretch", minHeight: "calc(100vh - 88px)" }}>

      {/* ── LEFT PANEL ───────────────────────────────────────────────────── */}
      <Box sx={{ flex: "0 0 340px", display: "flex", flexDirection: "column", gap: 2 }}>
        <Paper sx={{ p: 3, borderRadius: 3, bgcolor: bgPaper }}>

          {/* Date heading */}
          <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
            <Typography variant="h5" fontWeight={700} color={textMain} sx={{ fontFamily: "'Playfair Display', serif" }}>
              {selectedDate.toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })}
            </Typography>
            <Chip label="Today" size="small" onClick={() => { setSelectedDate(today); setViewDate(new Date(today.getFullYear(), today.getMonth(), 1)); }}
              sx={{ borderRadius: 50, bgcolor: primary, color: "#fff", cursor: "pointer", fontWeight: 600 }} />
          </Box>

          {/* Pills */}
          <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap", mb: 3 }}>
            <Chip label={`${tasksForDate(selectedDate).length} task(s)`} size="small"
              sx={{ borderRadius: 50, bgcolor: primary + "22", color: primary, fontWeight: 600 }} />
            {gcalConnected && (
              <Chip label={`${gcalForDate(selectedDate).length} GCal event(s)`} size="small"
                sx={{ borderRadius: 50, bgcolor: gcalColor + "22", color: gcalColor, fontWeight: 600 }} />
            )}
          </Box>

          {/* Stat cards */}
          <Box sx={{ display: "flex", gap: 1.5 }}>
            {[
              { icon: <TodayIcon sx={{ fontSize: 18 }} />, label: "Tasks Today",  value: tasksForDate(today).length },
              { icon: <TodayIcon sx={{ fontSize: 18 }} />, label: "This Month",   value: monthTasks.length },
              { icon: <FlagIcon  sx={{ fontSize: 18 }} />, label: "GCal Events",  value: monthGcal.length },
            ].map(s => (
              <Box key={s.label} sx={{
                flex: 1, bgcolor: isDark ? "rgba(255,255,255,0.06)" : "rgba(255,255,255,0.7)",
                borderRadius: 2.5, p: 1.5, display: "flex", alignItems: "center", gap: 1,
                border: `1px solid ${borderCol}`,
              }}>
                <Box sx={{ color: primary }}>{s.icon}</Box>
                <Box>
                  <Typography variant="caption" color={textMuted} display="block" lineHeight={1.2}>{s.label}</Typography>
                  <Typography fontWeight={700} fontSize={18} color={textMain}>{s.value}</Typography>
                </Box>
              </Box>
            ))}
          </Box>
        </Paper>

        {/* Items on selected day */}
        <Paper sx={{ p: 3, borderRadius: 3, bgcolor: bgPaper, flexGrow: 1 }}>
          <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
            <Typography fontWeight={600} color={textMain} sx={{ fontFamily: "'Playfair Display', serif" }}>
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

          {/* GCal not connected notice */}
          {!gcalConnected && (
            <Box sx={{ p: 2, borderRadius: 2, bgcolor: gcalColor + "11", border: `1px solid ${gcalColor}33`, mb: 2 }}>
              <Typography fontSize={12} color={gcalColor} fontWeight={500}>
                📅 Log in with Google to see your Google Calendar events here.
              </Typography>
            </Box>
          )}

          {loadingTasks ? (
            <Box sx={{ display: "flex", justifyContent: "center", py: 4 }}><CircularProgress size={28} /></Box>
          ) : selectedItems.length === 0 ? (
            <Box sx={{ textAlign: "center", py: 5, color: textMuted }}>
              <Typography fontSize={32} mb={1}>📭</Typography>
              <Typography variant="body2">Nothing scheduled for this day.</Typography>
            </Box>
          ) : (
            <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5, maxHeight: 420, overflowY: "auto",
              "&::-webkit-scrollbar": { width: 4 },
              "&::-webkit-scrollbar-thumb": { borderRadius: 4, bgcolor: primary + "44" },
            }}>
              {selectedItems.map((item, i) => {
                const isGcal  = item.isGcal;
                const over    = !isGcal && isOverdue(item);
                const status  = isGcal ? "gcal" : item.status === "completed" ? "completed" : over ? "overdue" : "pending";
                const dotColor = isGcal ? gcalColor : STATUS_COLOR[status] || STATUS_COLOR.pending;

                return (
                  <Box key={item.id || i} sx={{
                    p: 2, borderRadius: 2.5,
                    bgcolor: isDark ? "rgba(255,255,255,0.05)" : "rgba(255,255,255,0.8)",
                    border: `1px solid ${isGcal ? gcalColor + "44" : borderCol}`,
                    transition: "box-shadow 0.2s",
                    "&:hover": { boxShadow: 2 },
                  }}>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 0.5 }}>
                      <Box sx={{ width: 8, height: 8, borderRadius: "50%", bgcolor: dotColor, flexShrink: 0 }} />
                      <Typography fontWeight={600} fontSize={14} color={textMain}
                        sx={{ textDecoration: item.status === "completed" ? "line-through" : "none" }}>
                        {item.title}
                      </Typography>
                    </Box>
                    {item.description && (
                      <Typography variant="caption" color={textMuted} display="block" mt={0.2} noWrap>
                        {item.description}
                      </Typography>
                    )}
                    <Box sx={{ display: "flex", gap: 1, mt: 0.8, flexWrap: "wrap" }}>
                      {isGcal ? (
                        <Chip label="📅 Google Calendar" size="small"
                          sx={{ borderRadius: 50, height: 20, fontSize: 11, bgcolor: gcalColor + "22", color: gcalColor, fontWeight: 600 }} />
                      ) : (
                        <>
                          <Chip label={item.category} size="small"
                            sx={{ borderRadius: 50, height: 20, fontSize: 11, bgcolor: primary + "22", color: primary }} />
                          <Chip label={item.status} size="small"
                            sx={{ borderRadius: 50, height: 20, fontSize: 11, bgcolor: dotColor + "22", color: dotColor, fontWeight: 600 }} />
                        </>
                      )}
                      {item.due_date && (
                        <Chip label={new Date(item.due_date).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                          size="small" sx={{ borderRadius: 50, height: 20, fontSize: 11, bgcolor: borderCol, color: textMuted }} />
                      )}
                      {isGcal && item.link && (
                        <Chip label="Open" size="small" onClick={() => window.open(item.link, "_blank")}
                          sx={{ borderRadius: 50, height: 20, fontSize: 11, bgcolor: gcalColor + "22", color: gcalColor, cursor: "pointer" }} />
                      )}
                    </Box>
                  </Box>
                );
              })}
            </Box>
          )}
        </Paper>
      </Box>

      {/* ── RIGHT PANEL: Month Grid ───────────────────────────────────────── */}
      <Box sx={{ flex: "1 1 0", minWidth: 0, display: "flex", flexDirection: "column" }}>
        <Paper sx={{ p: 3, borderRadius: 3, bgcolor: bgPaper, flexGrow: 1, display: "flex", flexDirection: "column" }}>

          {/* Month nav */}
          <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", mb: 3 }}>
            <IconButton onClick={() => setViewDate(new Date(year, month - 1, 1))}
              sx={{ bgcolor: isDark ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.05)", borderRadius: 2 }}>
              <ChevronLeftIcon />
            </IconButton>

            <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
              <Typography fontWeight={700} fontSize={18} color={textMain} letterSpacing={1}>
                {MONTHS[month].toUpperCase()}  {year}
              </Typography>
              {monthTasks.length > 0 && (
                <Chip label={`${monthTasks.length} tasks`} size="small"
                  sx={{ borderRadius: 50, bgcolor: primary + "22", color: primary, fontWeight: 600, height: 22 }} />
              )}
              {gcalConnected && monthGcal.length > 0 && (
                <Chip label={`${monthGcal.length} events`} size="small"
                  sx={{ borderRadius: 50, bgcolor: gcalColor + "22", color: gcalColor, fontWeight: 600, height: 22 }} />
              )}
            </Box>

            <IconButton onClick={() => setViewDate(new Date(year, month + 1, 1))}
              sx={{ bgcolor: isDark ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.05)", borderRadius: 2 }}>
              <ChevronRightIcon />
            </IconButton>
          </Box>

          {/* Month view label + today badge */}
          <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
            <Typography fontWeight={500} color={textMuted} fontSize={13}>Month View</Typography>
            <Chip label={today.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}
              size="small" sx={{ borderRadius: 50, bgcolor: primary, color: "#fff", fontWeight: 600, height: 26 }} />
          </Box>

          {/* Weekday headers */}
          <Box sx={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", mb: 1 }}>
            {WEEKDAYS.map(d => (
              <Typography key={d} align="center" variant="caption"
                fontWeight={700} color={textMuted} letterSpacing={1} fontSize={11}>{d}</Typography>
            ))}
          </Box>

          {/* Day cells */}
          <Box sx={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", gap: 0.5, flexGrow: 1 }}>
            {calCells.map((date, i) => {
              if (!date) return <Box key={`empty-${i}`} />;

              const isToday    = isSameDay(date, today);
              const isSelected = isSameDay(date, selectedDate);
              const hasTask    = tasksForDate(date).length > 0;
              const hasGcal    = gcalForDate(date).length > 0;
              const totalItems = tasksForDate(date).length + gcalForDate(date).length;

              return (
                <Tooltip key={date.toISOString()}
                  title={totalItems > 0 ? `${tasksForDate(date).length} task(s), ${gcalForDate(date).length} event(s)` : ""}
                  placement="top">
                  <Box onClick={() => setSelectedDate(date)} sx={{
                    display: "flex", flexDirection: "column", alignItems: "center",
                    justifyContent: "center", borderRadius: 2.5, py: 1,
                    cursor: "pointer", position: "relative", minHeight: 52,
                    border: `1px solid ${isSelected && !isToday ? primary + "55" : borderCol}`,
                    bgcolor: isToday ? primary : isSelected ? selectedBg : isDark ? "rgba(255,255,255,0.03)" : "rgba(255,255,255,0.6)",
                    transition: "all 0.15s",
                    "&:hover": { bgcolor: isToday ? primary : primary + "22", transform: "translateY(-1px)", boxShadow: 1 },
                  }}>
                    <Typography fontSize={14} fontWeight={isToday || isSelected ? 700 : 400}
                      color={isToday ? "#fff" : textMain}>
                      {date.getDate()}
                    </Typography>
                    <Box sx={{ display: "flex", gap: 0.4, mt: 0.4 }}>
                      {hasTask && <Box sx={{ width: 5, height: 5, borderRadius: "50%", bgcolor: isToday ? "#fff" : "#4CAF50" }} />}
                      {hasGcal && <Box sx={{ width: 5, height: 5, borderRadius: "50%", bgcolor: isToday ? "rgba(255,255,255,0.7)" : gcalColor }} />}
                    </Box>
                  </Box>
                </Tooltip>
              );
            })}
          </Box>

          {/* Legend */}
          <Box sx={{ display: "flex", gap: 2.5, mt: 2, justifyContent: "center", flexWrap: "wrap" }}>
            {[
              { color: "#4CAF50",  label: "Has Tasks" },
              { color: gcalColor,  label: "GCal Event" },
              { color: primary + "55", label: "Selected" },
              { color: primary,    label: "Today", isToday: true },
            ].map(l => (
              <Box key={l.label} sx={{ display: "flex", alignItems: "center", gap: 0.6 }}>
                <Box sx={{ width: 8, height: 8, borderRadius: "50%", bgcolor: l.isToday ? l.color : l.color }} />
                <Typography variant="caption" color={textMuted} fontSize={11}>{l.label}</Typography>
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

      {/* Snackbar */}
      {snackMsg && (
        <Box sx={{
          position: "fixed", bottom: 24, right: 24, zIndex: 9999,
          bgcolor: primary, color: "#fff", px: 3, py: 1.5,
          borderRadius: 2, boxShadow: 4, fontSize: 14,
        }}>
          {snackMsg}
        </Box>
      )}
    </Box>
  );
}
