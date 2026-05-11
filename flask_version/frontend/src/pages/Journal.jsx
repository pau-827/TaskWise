import { useState, useEffect, useContext, useCallback } from "react";
import {
  Box, Paper, Typography, IconButton, TextField, Button,
  Chip, CircularProgress, Tooltip, Snackbar, Alert, InputAdornment,
  Divider, Menu, MenuItem,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/Delete";
import SaveIcon from "@mui/icons-material/Save";
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";
import SearchIcon from "@mui/icons-material/Search";
import PictureAsPdfIcon from "@mui/icons-material/PictureAsPdf";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import { supabase } from "../services/supabase";
import { AppContext } from "../context/AppContext";
import { ThemeContext } from "../context/ThemeContext";
import { THEMES } from "../theme/themes";

const MOODS = [
  { label: "Happy", emoji: "😊" },
  { label: "Calm", emoji: "😌" },
  { label: "Neutral", emoji: "😐" },
  { label: "Sad", emoji: "😢" },
  { label: "Anxious", emoji: "😰" },
  { label: "Angry", emoji: "😠" },
];

export default function Journal() {
  const { user } = useContext(AppContext);
  const { themeName } = useContext(ThemeContext);

  const palette = THEMES[themeName]?.palette;
  const isDark = palette?.mode === "dark";
  const bgPaper = palette?.background?.paper ?? "#fff1f5";
  const primary = palette?.primary?.main ?? "#ff4f8b";
  const textMain = palette?.text?.primary ?? "#4a001f";
  const textMuted = palette?.text?.secondary ?? "#9b4b66";
  const borderCol = isDark ? "rgba(255,255,255,0.1)" : "rgba(255,79,139,0.18)";
  const rowBg = isDark ? "rgba(255,255,255,0.05)" : "rgba(255,255,255,0.75)";

  const [entries, setEntries] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [reflecting, setReflecting] = useState(false);
  const [search, setSearch] = useState("");
  const [menuAnchor, setMenuAnchor] = useState(null);
  const [snack, setSnack] = useState({ open: false, msg: "", severity: "success" });

  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [mood, setMood] = useState("");
  const [aiText, setAiText] = useState("");

  const showSnack = (msg, severity = "success") => {
    setSnack({ open: true, msg, severity });
  };

  const fmt = (iso) =>
    iso
      ? new Date(iso).toLocaleString("en-US", {
          month: "short",
          day: "numeric",
          year: "numeric",
          hour: "2-digit",
          minute: "2-digit",
        })
      : "";

  const fetchEntries = useCallback(async () => {
    if (!user) return;

    setLoading(true);

    const { data, error } = await supabase
      .from("journal_entries")
      .select("*")
      .eq("user_id", user.id)
      .order("created_at", { ascending: false });

    if (!error) {
      setEntries(data || []);
    } else {
      showSnack(error.message, "error");
    }

    setLoading(false);
  }, [user]);

  useEffect(() => {
    fetchEntries();
  }, [fetchEntries]);

  const selectEntry = (entry) => {
    setSelected(entry);
    setTitle(entry.title || "");
    setContent(entry.content || "");
    setMood(entry.mood || entry.ai_mood || "");
    setAiText(entry.ai_reflection || "");
  };

  const newEntry = async () => {
    const count = entries.length + 1;

    const { data, error } = await supabase
      .from("journal_entries")
      .insert({
        user_id: user.id,
        title: `Untitled (${count})`,
        content: "",
        mood: "",
        ai_reflection: "",
        ai_mood: "",
      })
      .select()
      .single();

    if (!error) {
      await fetchEntries();
      selectEntry(data);
      showSnack("New entry created!");
    } else {
      showSnack(error.message, "error");
    }
  };

  const saveEntry = async () => {
    if (!selected) return;

    setSaving(true);

    const { error } = await supabase
      .from("journal_entries")
      .update({
        title,
        content,
        mood,
        ai_reflection: aiText,
        updated_at: new Date().toISOString(),
      })
      .eq("id", selected.id);

    if (!error) {
      showSnack("Entry saved!");
      await fetchEntries();
      setSelected((prev) => ({
        ...prev,
        title,
        content,
        mood,
        ai_reflection: aiText,
      }));
    } else {
      showSnack(error.message, "error");
    }

    setSaving(false);
  };

  const deleteEntry = async (id) => {
    const { error } = await supabase
      .from("journal_entries")
      .delete()
      .eq("id", id);

    if (!error) {
      showSnack("Entry deleted.");

      if (selected?.id === id) {
        setSelected(null);
        setTitle("");
        setContent("");
        setMood("");
        setAiText("");
      }

      await fetchEntries();
    } else {
      showSnack(error.message, "error");
    }
  };

  const handleReflect = async () => {
    if (!content.trim()) {
      showSnack("Write something first!", "warning");
      return;
    }

    if (!selected) {
      showSnack("Save the entry first!", "warning");
      return;
    }

    setReflecting(true);

    try {
      const {
        data: { session },
      } = await supabase.auth.getSession();

      const user_jwt = session?.access_token;

      const res = await fetch("http://localhost:5000/api/journal/reflect", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ entry_id: selected.id, content, user_jwt }),
      });

      const data = await res.json();

      if (!res.ok) throw new Error(data.error || "Reflection failed");

      setAiText(data.reflection);

      if (data.mood) setMood(data.mood);

      showSnack("AI reflection ready!", "success");
      await fetchEntries();
    } catch (err) {
      showSnack(err.message, "error");
    }

    setReflecting(false);
  };

  const filtered = entries.filter(
    (e) =>
      e.title?.toLowerCase().includes(search.toLowerCase()) ||
      e.content?.toLowerCase().includes(search.toLowerCase())
  );

  const escapeHtml = (value = "") =>
    value
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;")
      .replaceAll("\n", "<br/>");

  const printEntries = (scope = "selected") => {
    const dataToPrint =
      scope === "all"
        ? entries
        : selected
        ? [{ ...selected, title, content, mood, ai_reflection: aiText }]
        : [];

    if (dataToPrint.length === 0) {
      showSnack("No journal entry to print.", "warning");
      return;
    }

    const displayName = user?.user_metadata?.display_name || user?.email?.split("@")[0] || "User";
    const generated = new Date().toLocaleString();

    const entryBlocks = dataToPrint
      .map((entry) => {
        const moodObj = MOODS.find((m) => m.label === (entry.mood || entry.ai_mood));
        const entryTitle = escapeHtml(entry.title || "Untitled Entry");
        const entryContent = escapeHtml(entry.content || "No content written.");
        const reflection = escapeHtml(entry.ai_reflection || "");

        return `
          <section class="entry">
            <div class="entry-header">
              <div>
                <h2>${entryTitle}</h2>
                <p class="date">Created: ${fmt(entry.created_at)}</p>
                <p class="date">Updated: ${fmt(entry.updated_at)}</p>
              </div>
              ${
                moodObj
                  ? `<div class="mood">${moodObj.emoji} ${moodObj.label}</div>`
                  : `<div class="mood empty">No Mood</div>`
              }
            </div>

            <div class="content">${entryContent}</div>

            ${
              reflection
                ? `
                  <div class="reflection">
                    <h3>AI Reflection</h3>
                    <p>${reflection}</p>
                  </div>
                `
                : ""
            }
          </section>
        `;
      })
      .join("");

    const html = `
      <!DOCTYPE html>
      <html>
        <head>
          <title>TaskWise Journal Report</title>
          <style>
            * {
              box-sizing: border-box;
            }

            body {
              margin: 0;
              padding: 40px;
              font-family: "Segoe UI", Arial, sans-serif;
              color: #32111f;
              background: #ffffff;
            }

            .top {
              display: flex;
              justify-content: space-between;
              align-items: flex-end;
              border-bottom: 3px solid ${primary};
              padding-bottom: 18px;
              margin-bottom: 28px;
            }

            .brand {
              font-size: 30px;
              font-weight: 800;
              color: ${primary};
            }

            .subtitle {
              font-size: 13px;
              color: #777;
              margin-top: 4px;
            }

            .meta {
              text-align: right;
              color: #777;
              font-size: 12px;
              line-height: 1.6;
            }

            .entry {
              page-break-inside: avoid;
              border: 1px solid #f0c7d6;
              border-radius: 18px;
              padding: 24px;
              margin-bottom: 24px;
              background: #fff8fb;
            }

            .entry-header {
              display: flex;
              justify-content: space-between;
              gap: 20px;
              border-bottom: 1px solid #f3d2de;
              padding-bottom: 14px;
              margin-bottom: 18px;
            }

            h2 {
              margin: 0 0 6px;
              font-size: 22px;
              color: #32111f;
            }

            .date {
              margin: 2px 0;
              font-size: 12px;
              color: #777;
            }

            .mood {
              align-self: flex-start;
              padding: 8px 14px;
              border-radius: 999px;
              background: ${primary}22;
              color: ${primary};
              font-weight: 700;
              white-space: nowrap;
              font-size: 13px;
            }

            .mood.empty {
              color: #777;
              background: #f2f2f2;
            }

            .content {
              font-size: 14px;
              line-height: 1.8;
              color: #3b2430;
              white-space: normal;
            }

            .reflection {
              margin-top: 20px;
              padding: 16px;
              border-left: 4px solid ${primary};
              background: #ffffff;
              border-radius: 12px;
            }

            .reflection h3 {
              margin: 0 0 8px;
              color: ${primary};
              font-size: 14px;
            }

            .reflection p {
              margin: 0;
              font-size: 13px;
              line-height: 1.7;
              color: #555;
              font-style: italic;
            }

            .footer {
              margin-top: 30px;
              text-align: center;
              font-size: 11px;
              color: #aaa;
            }

            @media print {
              body {
                padding: 24px;
              }

              .entry {
                page-break-inside: avoid;
              }
            }
          </style>
        </head>
        <body>
          <div class="top">
            <div>
              <div class="brand">TaskWise Journal</div>
              <div class="subtitle">${scope === "all" ? "All Journal Entries" : "Selected Journal Entry"}</div>
            </div>
            <div class="meta">
              <div>${displayName}</div>
              <div>Generated: ${generated}</div>
              <div>Total Entries: ${dataToPrint.length}</div>
            </div>
          </div>

          ${entryBlocks}

          <div class="footer">TaskWise • Journal Export</div>
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
  };

  return (
    <Box
      sx={{
        width: "100%",
        display: "flex",
        flexDirection: { xs: "column", lg: "row" },
        gap: 3,
        height: { xs: "auto", lg: "calc(100vh - 88px)" },
      }}
    >
      <Box
        sx={{
          width: { xs: "100%", lg: 340 },
          flex: { xs: "1 1 auto", lg: "0 0 340px" },
          display: "flex",
          flexDirection: "column",
          minHeight: 0,
        }}
      >
        <Paper
          sx={{
            p: 2.5,
            borderRadius: 4,
            bgcolor: bgPaper,
            flex: 1,
            display: "flex",
            flexDirection: "column",
            minHeight: 0,
            boxShadow: "0 8px 24px rgba(0,0,0,0.06)",
          }}
        >
          <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
            <Box>
              <Typography
                variant="h5"
                fontWeight={800}
                color={textMain}
                sx={{ fontFamily: "'Playfair Display', serif" }}
              >
                Journal
              </Typography>
              <Typography variant="caption" color={textMuted}>
                {entries.length} saved entr{entries.length === 1 ? "y" : "ies"}
              </Typography>
            </Box>

            <Button
              variant="contained"
              startIcon={<AddIcon />}
              size="small"
              onClick={newEntry}
              sx={{ borderRadius: 50, px: 2 }}
            >
              New
            </Button>
          </Box>

          <TextField
            fullWidth
            size="small"
            placeholder="Search entries..."
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
            sx={{ mb: 2 }}
          />

          <Box
            sx={{
              flexGrow: 1,
              overflowY: "auto",
              pr: 0.5,
              "&::-webkit-scrollbar": { width: 6 },
              "&::-webkit-scrollbar-track": { background: "rgba(0,0,0,0.04)", borderRadius: 10 },
              "&::-webkit-scrollbar-thumb": { borderRadius: 10, bgcolor: primary + "66" },
            }}
          >
            {loading ? (
              <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
                <CircularProgress size={28} />
              </Box>
            ) : filtered.length === 0 ? (
              <Box sx={{ textAlign: "center", py: 6, color: textMuted }}>
                <Typography fontSize={36} mb={1}>📓</Typography>
                <Typography variant="body2">No entries yet.</Typography>
                <Typography variant="caption">Click New to start writing.</Typography>
              </Box>
            ) : (
              <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5 }}>
                {filtered.map((entry) => {
                  const isActive = selected?.id === entry.id;
                  const moodObj = MOODS.find((m) => m.label === entry.mood);

                  return (
                    <Paper
                      key={entry.id}
                      variant="outlined"
                      onClick={() => selectEntry(entry)}
                      sx={{
                        p: 2,
                        borderRadius: 3,
                        cursor: "pointer",
                        bgcolor: isActive ? primary + "22" : rowBg,
                        borderColor: isActive ? primary : borderCol,
                        transition: "all 0.2s",
                        "&:hover": {
                          bgcolor: primary + "15",
                          transform: "translateY(-2px)",
                          boxShadow: 2,
                        },
                      }}
                    >
                      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                        <Typography fontWeight={700} fontSize={14} color={textMain} noWrap sx={{ flex: 1 }}>
                          {entry.title || "Untitled"}
                        </Typography>

                        <Tooltip title="Delete">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={(e) => {
                              e.stopPropagation();
                              deleteEntry(entry.id);
                            }}
                            sx={{ ml: 0.5, p: 0.3 }}
                          >
                            <DeleteIcon sx={{ fontSize: 16 }} />
                          </IconButton>
                        </Tooltip>
                      </Box>

                      {entry.content && (
                        <Typography variant="caption" color={textMuted} display="block" mt={0.5} noWrap>
                          {entry.content}
                        </Typography>
                      )}

                      <Box sx={{ display: "flex", alignItems: "center", gap: 1, mt: 1, flexWrap: "wrap" }}>
                        {moodObj && (
                          <Chip
                            label={`${moodObj.emoji} ${moodObj.label}`}
                            size="small"
                            sx={{
                              borderRadius: 50,
                              height: 22,
                              fontSize: 11,
                              bgcolor: primary + "22",
                              color: primary,
                              fontWeight: 700,
                            }}
                          />
                        )}

                        <Typography variant="caption" color={textMuted} fontSize={10}>
                          {fmt(entry.created_at)}
                        </Typography>
                      </Box>
                    </Paper>
                  );
                })}
              </Box>
            )}
          </Box>
        </Paper>
      </Box>

      <Box sx={{ flex: "1 1 0", minWidth: 0, display: "flex", flexDirection: "column", minHeight: 0 }}>
        <Paper
          sx={{
            p: 3,
            borderRadius: 4,
            bgcolor: bgPaper,
            flex: 1,
            display: "flex",
            flexDirection: "column",
            gap: 2,
            minHeight: 0,
            boxShadow: "0 8px 24px rgba(0,0,0,0.06)",
          }}
        >
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder={selected ? "Entry title..." : "Select or create an entry to start writing..."}
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              disabled={!selected}
              sx={{
                "& .MuiOutlinedInput-root": {
                  borderRadius: 3,
                  fontSize: 18,
                  fontWeight: 700,
                  bgcolor: rowBg,
                },
              }}
            />

            <Tooltip title="Print selected entry">
              <span>
                <IconButton
                  disabled={!selected}
                  onClick={() => printEntries("selected")}
                  sx={{
                    border: "1px solid",
                    borderColor: borderCol,
                    borderRadius: 3,
                  }}
                >
                  <PictureAsPdfIcon />
                </IconButton>
              </span>
            </Tooltip>

            <Tooltip title="More print options">
              <IconButton
                onClick={(e) => setMenuAnchor(e.currentTarget)}
                sx={{
                  border: "1px solid",
                  borderColor: borderCol,
                  borderRadius: 3,
                }}
              >
                <MoreVertIcon />
              </IconButton>
            </Tooltip>

            <Menu
              anchorEl={menuAnchor}
              open={Boolean(menuAnchor)}
              onClose={() => setMenuAnchor(null)}
            >
              <MenuItem
                disabled={!selected}
                onClick={() => {
                  setMenuAnchor(null);
                  printEntries("selected");
                }}
              >
                Print Selected Entry
              </MenuItem>

              <MenuItem
                disabled={entries.length === 0}
                onClick={() => {
                  setMenuAnchor(null);
                  printEntries("all");
                }}
              >
                Print All Entries
              </MenuItem>
            </Menu>

            {selected && (
              <Tooltip title="Delete entry">
                <IconButton color="error" onClick={() => deleteEntry(selected.id)}>
                  <DeleteIcon />
                </IconButton>
              </Tooltip>
            )}
          </Box>

          <Paper
            variant="outlined"
            sx={{
              p: 2,
              borderRadius: 3,
              borderColor: borderCol,
              bgcolor: rowBg,
            }}
          >
            <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 1 }}>
              <Typography
                variant="caption"
                fontWeight={800}
                color={textMuted}
                letterSpacing={1}
                textTransform="uppercase"
              >
                Mood
              </Typography>

              <Typography variant="caption" color={textMuted} fontStyle="italic">
                AI can suggest a mood when you reflect
              </Typography>
            </Box>

            <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
              {MOODS.map((m) => (
                <Chip
                  key={m.label}
                  label={`${m.emoji} ${m.label}`}
                  onClick={() => selected && setMood(mood === m.label ? "" : m.label)}
                  sx={{
                    borderRadius: 50,
                    cursor: selected ? "pointer" : "default",
                    fontWeight: mood === m.label ? 800 : 500,
                    bgcolor: mood === m.label ? primary : "rgba(255,255,255,0.75)",
                    color: mood === m.label ? "#fff" : textMain,
                    border: `1px solid ${mood === m.label ? primary : borderCol}`,
                    opacity: selected ? 1 : 0.5,
                    "&:hover": selected
                      ? { bgcolor: mood === m.label ? primary : primary + "22" }
                      : {},
                  }}
                />
              ))}
            </Box>
          </Paper>

          <Divider />

          <TextField
            fullWidth
            multiline
            placeholder={selected ? "Write your thoughts here..." : "Create or select an entry to begin writing..."}
            value={content}
            onChange={(e) => setContent(e.target.value)}
            disabled={!selected}
            sx={{
              flex: 1,
              minHeight: 0,
              "& .MuiOutlinedInput-root": {
                borderRadius: 3,
                height: "100%",
                alignItems: "flex-start",
                bgcolor: rowBg,
              },
              "& textarea": {
                height: "100% !important",
                lineHeight: 1.7,
              },
            }}
            InputProps={{ sx: { height: "100%", alignItems: "flex-start" } }}
          />

          {aiText && (
            <Paper
              variant="outlined"
              sx={{
                p: 2,
                borderRadius: 3,
                bgcolor: primary + "11",
                borderColor: primary + "33",
              }}
            >
              <Box sx={{ display: "flex", alignItems: "center", gap: 0.8, mb: 0.8 }}>
                <AutoAwesomeIcon sx={{ fontSize: 16, color: primary }} />
                <Typography variant="caption" fontWeight={800} color={primary}>
                  AI Reflection
                </Typography>
              </Box>

              <Typography variant="body2" color={textMuted} fontStyle="italic" lineHeight={1.7}>
                {aiText}
              </Typography>
            </Paper>
          )}

          <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 2, flexWrap: "wrap" }}>
            <Box>
              {selected ? (
                <>
                  <Typography variant="caption" color={textMuted} display="block">
                    Created: {fmt(selected.created_at)}
                  </Typography>
                  <Typography variant="caption" color={textMuted} display="block">
                    Last Saved: {fmt(selected.updated_at)}
                  </Typography>
                </>
              ) : (
                <Typography variant="caption" color={textMuted} fontStyle="italic">
                  No entry selected
                </Typography>
              )}
            </Box>

            <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
              <Button
                variant="outlined"
                startIcon={reflecting ? <CircularProgress size={14} color="inherit" /> : <AutoAwesomeIcon />}
                onClick={handleReflect}
                disabled={reflecting || !selected}
                sx={{ borderRadius: 50, px: 2.5 }}
              >
                {reflecting ? "Reflecting..." : "Reflect"}
              </Button>

              <Button
                variant="contained"
                startIcon={<SaveIcon />}
                onClick={saveEntry}
                disabled={saving || !selected}
                sx={{ borderRadius: 50, px: 2.5 }}
              >
                {saving ? "Saving..." : "Save"}
              </Button>
            </Box>
          </Box>
        </Paper>
      </Box>

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