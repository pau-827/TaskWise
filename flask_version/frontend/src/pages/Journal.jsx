import { useState, useEffect, useContext, useCallback } from "react";
import {
  Box, Paper, Typography, IconButton, TextField, Button,
  Chip, CircularProgress, Tooltip, Snackbar, Alert, InputAdornment,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/Delete";
import SaveIcon from "@mui/icons-material/Save";
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";
import SearchIcon from "@mui/icons-material/Search";
import { supabase } from "../services/supabase";
import { AppContext } from "../context/AppContext";
import { ThemeContext } from "../context/ThemeContext";
import { THEMES } from "../theme/themes";

const MOODS = [
  { label: "Happy",   emoji: "😊" },
  { label: "Calm",    emoji: "😌" },
  { label: "Neutral", emoji: "😐" },
  { label: "Sad",     emoji: "😢" },
  { label: "Anxious", emoji: "😰" },
  { label: "Angry",   emoji: "😠" },
];

export default function Journal() {
  const { user } = useContext(AppContext);
  const { themeName } = useContext(ThemeContext);
  const palette  = THEMES[themeName]?.palette;
  const isDark   = palette?.mode === "dark";
  const bgPaper  = palette?.background?.paper  ?? "#E3F4F4";
  const primary  = palette?.primary?.main      ?? "#4A707A";
  const textMain = palette?.text?.primary      ?? "#1a3a40";
  const textMuted= palette?.text?.secondary    ?? "#4A707A";
  const borderCol= isDark ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.08)";
  const rowBg    = isDark ? "rgba(255,255,255,0.05)" : "rgba(255,255,255,0.75)";

  const [entries,  setEntries]  = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading,  setLoading]  = useState(true);
  const [saving,   setSaving]   = useState(false);
  const [reflecting, setReflecting] = useState(false);
  const [search,   setSearch]   = useState("");
  const [snack,    setSnack]    = useState({ open: false, msg: "", severity: "success" });

  // ── Editing state ──────────────────────────────────────────────────────
  const [title,   setTitle]   = useState("");
  const [content, setContent] = useState("");
  const [mood,    setMood]    = useState("");
  const [aiText,  setAiText]  = useState("");

  const showSnack = (msg, severity = "success") => setSnack({ open: true, msg, severity });

  // ── Fetch entries ──────────────────────────────────────────────────────
  const fetchEntries = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    const { data } = await supabase
      .from("journal_entries").select("*")
      .eq("user_id", user.id)
      .order("created_at", { ascending: false });
    setEntries(data || []);
    setLoading(false);
  }, [user]);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { fetchEntries(); }, [fetchEntries]);

  // ── Select entry ───────────────────────────────────────────────────────
  const selectEntry = (entry) => {
    setSelected(entry);
    setTitle(entry.title || "");
    setContent(entry.content || "");
    setMood(entry.mood || "");
    setAiText(entry.ai_reflection || "");
  };

  // ── New entry ──────────────────────────────────────────────────────────
  const newEntry = async () => {
    const count = entries.length + 1;
    const { data, error } = await supabase.from("journal_entries").insert({
      user_id: user.id,
      title: `Untitled (${count})`,
      content: "",
      mood: "",
      ai_reflection: "",
    }).select().single();
    if (!error) {
      await fetchEntries();
      selectEntry(data);
      showSnack("New entry created!");
    }
  };

  // ── Save entry ─────────────────────────────────────────────────────────
  const saveEntry = async () => {
    if (!selected) return;
    setSaving(true);
    const { error } = await supabase.from("journal_entries").update({
      title, content, mood, ai_reflection: aiText,
      updated_at: new Date().toISOString(),
    }).eq("id", selected.id);
    if (!error) {
      showSnack("Entry saved!");
      await fetchEntries();
      setSelected(prev => ({ ...prev, title, content, mood, ai_reflection: aiText }));
    } else showSnack(error.message, "error");
    setSaving(false);
  };

  // ── Delete entry ───────────────────────────────────────────────────────
  const deleteEntry = async (id) => {
    const { error } = await supabase.from("journal_entries").delete().eq("id", id);
    if (!error) {
      showSnack("Entry deleted.");
      if (selected?.id === id) {
        setSelected(null); setTitle(""); setContent(""); setMood(""); setAiText("");
      }
      await fetchEntries();
    }
  };

  // ── AI Reflect (placeholder — Flask will handle this later) ────────────
  const handleReflect = async () => {
    if (!content.trim()) { showSnack("Write something first!", "warning"); return; }
    setReflecting(true);
    // TODO: call Flask /api/journal/reflect endpoint
    // For now, show a placeholder message
    setTimeout(() => {
      setAiText("AI reflection will be available once the Flask backend is connected. Your entry has been noted!");
      setReflecting(false);
      showSnack("AI reflection ready!");
    }, 1500);
  };

  const filtered = entries.filter(e =>
    e.title?.toLowerCase().includes(search.toLowerCase()) ||
    e.content?.toLowerCase().includes(search.toLowerCase())
  );

  const fmt = (iso) => iso ? new Date(iso).toLocaleString("en-US", {
    month: "short", day: "numeric", year: "numeric", hour: "2-digit", minute: "2-digit",
  }) : "";

  return (
    <Box sx={{ width: "100%", display: "flex", gap: 3, alignItems: "stretch" }}>

      {/* ── LEFT: Entry List ─────────────────────────────────────────────── */}
      <Box sx={{ flex: "0 0 320px", display: "flex", flexDirection: "column" }}>
        <Paper sx={{ p: 2.5, borderRadius: 3, bgcolor: bgPaper, height: "100%", display: "flex", flexDirection: "column" }}>

          {/* Header */}
          <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
            <Typography variant="h5" fontWeight={700} color={textMain}
              sx={{ fontFamily: "'Playfair Display', serif" }}>
              Journal
            </Typography>
            <Button variant="contained" startIcon={<AddIcon />} size="small"
              onClick={newEntry} sx={{ borderRadius: 50, px: 2 }}>
              New Entry
            </Button>
          </Box>

          {/* Search */}
          <TextField fullWidth size="small" placeholder="Search entries..."
            value={search} onChange={e => setSearch(e.target.value)}
            InputProps={{
              startAdornment: <InputAdornment position="start"><SearchIcon fontSize="small" /></InputAdornment>,
              sx: { borderRadius: 50, mb: 0 },
            }}
            sx={{ mb: 2 }}
          />

          {/* Entry list */}
          <Box sx={{ flexGrow: 1, overflowY: "auto",
            "&::-webkit-scrollbar": { width: 4 },
            "&::-webkit-scrollbar-thumb": { borderRadius: 4, bgcolor: primary + "44" },
          }}>
            {loading ? (
              <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
                <CircularProgress size={28} />
              </Box>
            ) : filtered.length === 0 ? (
              <Box sx={{ textAlign: "center", py: 6, color: textMuted }}>
                <Typography fontSize={36} mb={1}>📓</Typography>
                <Typography variant="body2">No entries yet.</Typography>
                <Typography variant="caption">Click New Entry to start writing!</Typography>
              </Box>
            ) : (
              <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5 }}>
                {filtered.map(entry => {
                  const isActive = selected?.id === entry.id;
                  const moodObj  = MOODS.find(m => m.label === entry.mood);
                  return (
                    <Box key={entry.id}
                      onClick={() => selectEntry(entry)}
                      sx={{
                        p: 2, borderRadius: 2.5, cursor: "pointer",
                        bgcolor: isActive ? primary + "22" : rowBg,
                        border: `1px solid ${isActive ? primary : borderCol}`,
                        transition: "all 0.2s",
                        "&:hover": { bgcolor: primary + "15", transform: "translateY(-1px)" },
                      }}>
                      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                        <Typography fontWeight={600} fontSize={14} color={textMain} noWrap sx={{ flex: 1 }}>
                          {entry.title || "Untitled"}
                        </Typography>
                        <Tooltip title="Delete">
                          <IconButton size="small" color="error"
                            onClick={e => { e.stopPropagation(); deleteEntry(entry.id); }}
                            sx={{ ml: 0.5, p: 0.3 }}>
                            <DeleteIcon sx={{ fontSize: 16 }} />
                          </IconButton>
                        </Tooltip>
                      </Box>
                      {entry.content && (
                        <Typography variant="caption" color={textMuted} display="block" mt={0.3} noWrap>
                          {entry.content}
                        </Typography>
                      )}
                      <Box sx={{ display: "flex", alignItems: "center", gap: 1, mt: 0.8 }}>
                        {moodObj && (
                          <Chip label={`${moodObj.emoji} ${moodObj.label}`} size="small"
                            sx={{ borderRadius: 50, height: 20, fontSize: 11,
                              bgcolor: primary + "22", color: primary, fontWeight: 600 }} />
                        )}
                        <Typography variant="caption" color={textMuted} fontSize={10}>
                          {fmt(entry.created_at)}
                        </Typography>
                      </Box>
                    </Box>
                  );
                })}
              </Box>
            )}
          </Box>
        </Paper>
      </Box>

      {/* ── RIGHT: Editor ───────────────────────────────────────────────── */}
      <Box sx={{ flex: "1 1 0", minWidth: 0 }}>
        {!selected ? (
          <Paper sx={{ p: 4, borderRadius: 3, bgcolor: bgPaper, height: "100%",
            display: "flex", alignItems: "center", justifyContent: "center" }}>
            <Box sx={{ textAlign: "center", color: textMuted }}>
              <Typography fontSize={52} mb={2}>📝</Typography>
              <Typography variant="h6" fontWeight={500} color={textMain}>Select an entry to edit</Typography>
              <Typography variant="body2" mt={1}>Or create a new one using the button on the left.</Typography>
            </Box>
          </Paper>
        ) : (
          <Paper sx={{ p: 3, borderRadius: 3, bgcolor: bgPaper, height: "100%",
            display: "flex", flexDirection: "column", gap: 2 }}>

            {/* Title + delete */}
            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              <TextField
                fullWidth variant="outlined" placeholder="Entry title..."
                value={title} onChange={e => setTitle(e.target.value)}
                sx={{ "& .MuiOutlinedInput-root": { borderRadius: 2, fontSize: 18, fontWeight: 600 } }}
              />
              <Tooltip title="Delete entry">
                <IconButton color="error" onClick={() => deleteEntry(selected.id)}>
                  <DeleteIcon />
                </IconButton>
              </Tooltip>
            </Box>

            {/* Mood selector */}
            <Box>
              <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 1 }}>
                <Typography variant="caption" fontWeight={600} color={textMuted} letterSpacing={1}
                  textTransform="uppercase">
                  Mood
                </Typography>
                <Typography variant="caption" color={textMuted} fontStyle="italic">
                  AI will suggest a mood when you Reflect
                </Typography>
              </Box>
              <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
                {MOODS.map(m => (
                  <Chip
                    key={m.label}
                    label={`${m.emoji} ${m.label}`}
                    onClick={() => setMood(mood === m.label ? "" : m.label)}
                    sx={{
                      borderRadius: 50, cursor: "pointer", fontWeight: mood === m.label ? 700 : 400,
                      bgcolor: mood === m.label ? primary : rowBg,
                      color: mood === m.label ? "#fff" : textMain,
                      border: `1px solid ${mood === m.label ? primary : borderCol}`,
                      transition: "all 0.2s",
                      "&:hover": { bgcolor: mood === m.label ? primary : primary + "22" },
                    }}
                  />
                ))}
              </Box>
            </Box>

            <Box sx={{ borderTop: `1px solid ${borderCol}` }} />

            {/* Content */}
            <TextField
              fullWidth multiline
              placeholder="Write your thoughts here..."
              value={content} onChange={e => setContent(e.target.value)}
              sx={{
                flexGrow: 1,
                "& .MuiOutlinedInput-root": { borderRadius: 2, alignItems: "flex-start", height: "100%" },
                "& textarea": { height: "100% !important" },
              }}
              InputProps={{ sx: { height: "100%", alignItems: "flex-start" } }}
            />

            {/* AI Reflection */}
            {aiText && (
              <Box sx={{
                p: 2, borderRadius: 2.5, bgcolor: primary + "11",
                border: `1px solid ${primary}33`,
              }}>
                <Box sx={{ display: "flex", alignItems: "center", gap: 0.8, mb: 0.8 }}>
                  <AutoAwesomeIcon sx={{ fontSize: 16, color: primary }} />
                  <Typography variant="caption" fontWeight={700} color={primary}>AI Reflection</Typography>
                </Box>
                <Typography variant="body2" color={textMuted} fontStyle="italic" lineHeight={1.7}>
                  {aiText}
                </Typography>
              </Box>
            )}

            {/* Footer */}
            <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <Box>
                <Typography variant="caption" color={textMuted} display="block">
                  Created  {fmt(selected.created_at)}
                </Typography>
                <Typography variant="caption" color={textMuted} display="block">
                  Last saved  {fmt(selected.updated_at)}
                </Typography>
              </Box>
              <Box sx={{ display: "flex", gap: 1 }}>
                <Button
                  variant="outlined" startIcon={<AutoAwesomeIcon />}
                  onClick={handleReflect} disabled={reflecting}
                  sx={{ borderRadius: 50, px: 2.5 }}>
                  {reflecting ? "Reflecting..." : "Reflect"}
                </Button>
                <Button
                  variant="contained" startIcon={<SaveIcon />}
                  onClick={saveEntry} disabled={saving}
                  sx={{ borderRadius: 50, px: 2.5 }}>
                  {saving ? "Saving..." : "Save"}
                </Button>
              </Box>
            </Box>
          </Paper>
        )}
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
