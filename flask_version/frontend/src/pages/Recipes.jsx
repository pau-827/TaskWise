import { useState, useEffect, useContext, useCallback, useRef } from "react";
import {
  Box, Paper, Typography, IconButton, TextField, Button,
  Chip, CircularProgress, Tooltip, Snackbar, Alert, InputAdornment,
  Dialog, DialogTitle, DialogContent, DialogActions,
  FormControl, InputLabel, Select, MenuItem,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";
import SaveIcon from "@mui/icons-material/Save";
import SearchIcon from "@mui/icons-material/Search";
import ImageIcon from "@mui/icons-material/Image";
import AttachMoneyIcon from "@mui/icons-material/AttachMoney";
import { supabase } from "../services/supabase";
import { AppContext } from "../context/AppContext";
import { ThemeContext } from "../context/ThemeContext";
import { THEMES } from "../theme/themes";

const CATEGORIES = ["All", "Breakfast", "Lunch", "Dinner", "Dessert", "Snack", "Beverages", "Others"];

const CATEGORY_EMOJI = {
  Breakfast: "🍳", Lunch: "🥗", Dinner: "🍽️",
  Dessert: "🍰", Snack: "🍿", Beverages: "🧋", Others: "🍴",
};

const empty = {
  title: "", category: "Others", ingredients: "", steps: "",
  budget_min: "", budget_max: "", image_url: "",
};

export default function Recipes() {
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

  const [recipes,   setRecipes]   = useState([]);
  const [loading,   setLoading]   = useState(true);
  const [search,    setSearch]    = useState("");
  const [category,  setCategory]  = useState("All");
  const [selected,  setSelected]  = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [editMode,  setEditMode]  = useState(false);
  const [form,      setForm]      = useState(empty);
  const [imgUploading, setImgUploading] = useState(false);
  const [saving,    setSaving]    = useState(false);
  const [snack,     setSnack]     = useState({ open: false, msg: "", severity: "success" });
  const fileRef = useRef();

  const showSnack = (msg, severity = "success") => setSnack({ open: true, msg, severity });

  // ── Fetch recipes ──────────────────────────────────────────────────────
  const fetchRecipes = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    const { data } = await supabase.from("recipes").select("*")
      .eq("user_id", user.id).order("created_at", { ascending: false });
    setRecipes(data || []);
    setLoading(false);
  }, [user]);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { fetchRecipes(); }, [fetchRecipes]);

  // ── Image upload ───────────────────────────────────────────────────────
  const handleImageUpload = async (file) => {
    if (!file) return;
    setImgUploading(true);
    const ext  = file.name.split(".").pop();
    const path = `${user.id}/${Date.now()}.${ext}`;
    const { error } = await supabase.storage.from("recipe-images").upload(path, file);
    if (error) { showSnack("Image upload failed.", "error"); setImgUploading(false); return; }
    const { data } = supabase.storage.from("recipe-images").getPublicUrl(path);
    setForm(f => ({ ...f, image_url: data.publicUrl }));
    setImgUploading(false);
    showSnack("Image uploaded!");
  };

  // ── Save recipe ────────────────────────────────────────────────────────
  const handleSave = async () => {
    if (!form.title.trim()) { showSnack("Title is required.", "warning"); return; }
    setSaving(true);
    const payload = {
      ...form,
      user_id:    user.id,
      budget_min: form.budget_min ? Number(form.budget_min) : null,
      budget_max: form.budget_max ? Number(form.budget_max) : null,
    };
    if (editMode && selected) {
      const { error } = await supabase.from("recipes").update(payload).eq("id", selected.id);
      if (!error) { showSnack("Recipe updated!"); await fetchRecipes(); setModalOpen(false); }
      else showSnack(error.message, "error");
    } else {
      const { error } = await supabase.from("recipes").insert(payload);
      if (!error) { showSnack("Recipe added! 🍳"); await fetchRecipes(); setModalOpen(false); }
      else showSnack(error.message, "error");
    }
    setSaving(false);
  };

  // ── Delete recipe ──────────────────────────────────────────────────────
  const handleDelete = async (id) => {
    const { error } = await supabase.from("recipes").delete().eq("id", id);
    if (!error) {
      showSnack("Recipe deleted.");
      if (selected?.id === id) setSelected(null);
      await fetchRecipes();
    }
  };

  const openAdd = () => { setForm(empty); setEditMode(false); setModalOpen(true); };
  const openEdit = (r) => {
    setForm({
      title: r.title || "", category: r.category || "Others",
      ingredients: r.ingredients || "", steps: r.steps || "",
      budget_min: r.budget_min || "", budget_max: r.budget_max || "",
      image_url: r.image_url || "",
    });
    setEditMode(true); setModalOpen(true);
  };

  const filtered = recipes.filter(r => {
    const matchCat = category === "All" || r.category === category;
    const matchSearch = r.title?.toLowerCase().includes(search.toLowerCase());
    return matchCat && matchSearch;
  });

  const inputSx = { "& .MuiOutlinedInput-root": { borderRadius: 2 } };

  return (
    <Box sx={{ width: "100%", display: "flex", gap: 3, alignItems: "stretch" }}>

      {/* ── LEFT: Recipe List ─────────────────────────────────────────────── */}
      <Box sx={{ flex: "0 0 340px", display: "flex", flexDirection: "column" }}>
        <Paper sx={{ p: 2.5, borderRadius: 3, bgcolor: bgPaper, height: "100%",
          display: "flex", flexDirection: "column" }}>

          {/* Header */}
          <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
            <Typography variant="h5" fontWeight={700} color={textMain}
              sx={{ fontFamily: "'Playfair Display', serif" }}>
              Recipes
            </Typography>
            <Button variant="contained" startIcon={<AddIcon />} size="small"
              onClick={openAdd} sx={{ borderRadius: 50, px: 2 }}>
              Add Recipe
            </Button>
          </Box>

          {/* Search */}
          <TextField fullWidth size="small" placeholder="Search recipes..."
            value={search} onChange={e => setSearch(e.target.value)}
            InputProps={{
              startAdornment: <InputAdornment position="start"><SearchIcon fontSize="small" /></InputAdornment>,
              sx: { borderRadius: 50 },
            }}
            sx={{ mb: 1.5 }}
          />

          {/* Category chips */}
          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.8, mb: 2 }}>
            {CATEGORIES.map(cat => (
              <Chip key={cat}
                label={cat === "All" ? "All" : `${CATEGORY_EMOJI[cat]} ${cat}`}
                size="small"
                onClick={() => setCategory(cat)}
                variant={category === cat ? "filled" : "outlined"}
                color={category === cat ? "primary" : "default"}
                sx={{ borderRadius: 50, fontSize: 11, fontWeight: category === cat ? 600 : 400 }}
              />
            ))}
          </Box>

          {/* Recipe list */}
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
                <Typography fontSize={36} mb={1}>🍴</Typography>
                <Typography variant="body2">No recipes yet.</Typography>
                <Typography variant="caption">Add one using the button above!</Typography>
              </Box>
            ) : (
              <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5 }}>
                {filtered.map(r => (
                  <Box key={r.id}
                    onClick={() => setSelected(r)}
                    sx={{
                      borderRadius: 2.5, overflow: "hidden", cursor: "pointer",
                      border: `1px solid ${selected?.id === r.id ? primary : borderCol}`,
                      bgcolor: selected?.id === r.id ? primary + "15" : rowBg,
                      transition: "all 0.2s",
                      "&:hover": { bgcolor: primary + "11", transform: "translateY(-1px)" },
                    }}>
                    {/* Recipe image */}
                    {r.image_url ? (
                      <Box component="img" src={r.image_url} alt={r.title}
                        sx={{ width: "100%", height: 120, objectFit: "cover" }} />
                    ) : (
                      <Box sx={{ width: "100%", height: 80, bgcolor: primary + "11",
                        display: "flex", alignItems: "center", justifyContent: "center" }}>
                        <Typography fontSize={32}>{CATEGORY_EMOJI[r.category] || "🍴"}</Typography>
                      </Box>
                    )}
                    <Box sx={{ p: 1.5 }}>
                      <Typography fontWeight={600} fontSize={14} color={textMain} noWrap>
                        {r.title}
                      </Typography>
                      <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", mt: 0.5 }}>
                        <Chip label={`${CATEGORY_EMOJI[r.category] || "🍴"} ${r.category}`}
                          size="small" sx={{ borderRadius: 50, height: 18, fontSize: 10,
                            bgcolor: primary + "22", color: primary }} />
                        {(r.budget_min || r.budget_max) && (
                          <Typography variant="caption" color={textMuted} fontSize={10}>
                            ₱{r.budget_min || 0}–{r.budget_max || "?"}
                          </Typography>
                        )}
                      </Box>
                    </Box>
                  </Box>
                ))}
              </Box>
            )}
          </Box>
        </Paper>
      </Box>

      {/* ── RIGHT: Recipe Detail ─────────────────────────────────────────── */}
      <Box sx={{ flex: "1 1 0", minWidth: 0 }}>
        {!selected ? (
          <Paper sx={{ p: 4, borderRadius: 3, bgcolor: bgPaper, height: "100%",
            display: "flex", alignItems: "center", justifyContent: "center" }}>
            <Box sx={{ textAlign: "center", color: textMuted }}>
              <Typography fontSize={52} mb={2}>🍳</Typography>
              <Typography variant="h6" fontWeight={500} color={textMain}>Select a recipe to view</Typography>
              <Typography variant="body2" mt={1}>Or add a new one using the button on the left.</Typography>
            </Box>
          </Paper>
        ) : (
          <Paper sx={{ p: 3, borderRadius: 3, bgcolor: bgPaper, height: "100%",
            display: "flex", flexDirection: "column", gap: 2, overflowY: "auto",
            "&::-webkit-scrollbar": { width: 4 },
            "&::-webkit-scrollbar-thumb": { borderRadius: 4, bgcolor: primary + "44" },
          }}>

            {/* Image */}
            {selected.image_url ? (
              <Box component="img" src={selected.image_url} alt={selected.title}
                sx={{ width: "100%", height: 220, objectFit: "cover", borderRadius: 2.5 }} />
            ) : (
              <Box sx={{ width: "100%", height: 140, borderRadius: 2.5,
                bgcolor: primary + "11", display: "flex", alignItems: "center", justifyContent: "center" }}>
                <Typography fontSize={52}>{CATEGORY_EMOJI[selected.category] || "🍴"}</Typography>
              </Box>
            )}

            {/* Title row */}
            <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <Box>
                <Typography variant="h5" fontWeight={700} color={textMain}
                  sx={{ fontFamily: "'Playfair Display', serif" }}>
                  {selected.title}
                </Typography>
                <Box sx={{ display: "flex", gap: 1, mt: 0.5, flexWrap: "wrap" }}>
                  <Chip label={`${CATEGORY_EMOJI[selected.category]} ${selected.category}`}
                    size="small" sx={{ borderRadius: 50, bgcolor: primary + "22", color: primary, fontWeight: 600 }} />
                  {(selected.budget_min || selected.budget_max) && (
                    <Chip
                      icon={<AttachMoneyIcon sx={{ fontSize: 14 }} />}
                      label={`₱${selected.budget_min || 0} – ₱${selected.budget_max || "?"}`}
                      size="small"
                      sx={{ borderRadius: 50, bgcolor: "#4CAF5022", color: "#4CAF50", fontWeight: 600 }}
                    />
                  )}
                </Box>
              </Box>
              <Box sx={{ display: "flex", gap: 0.5 }}>
                <Tooltip title="Edit">
                  <IconButton onClick={() => openEdit(selected)}>
                    <EditIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Delete">
                  <IconButton color="error" onClick={() => handleDelete(selected.id)}>
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
            </Box>

            <Box sx={{ borderTop: `1px solid ${borderCol}` }} />

            {/* Ingredients */}
            <Box>
              <Typography fontWeight={700} fontSize={15} color={textMain} mb={1}>🧂 Ingredients</Typography>
              <Box sx={{ p: 2, borderRadius: 2, bgcolor: rowBg, border: `1px solid ${borderCol}` }}>
                {selected.ingredients ? (
                  selected.ingredients.split("\n").map((line, i) => (
                    <Box key={i} sx={{ display: "flex", gap: 1, mb: 0.5 }}>
                      <Typography color={primary} fontWeight={700}>•</Typography>
                      <Typography fontSize={14} color={textMain}>{line}</Typography>
                    </Box>
                  ))
                ) : (
                  <Typography fontSize={14} color={textMuted} fontStyle="italic">No ingredients listed.</Typography>
                )}
              </Box>
            </Box>

            {/* Steps */}
            <Box>
              <Typography fontWeight={700} fontSize={15} color={textMain} mb={1}>👨‍🍳 Steps</Typography>
              <Box sx={{ p: 2, borderRadius: 2, bgcolor: rowBg, border: `1px solid ${borderCol}` }}>
                {selected.steps ? (
                  selected.steps.split("\n").map((line, i) => (
                    <Box key={i} sx={{ display: "flex", gap: 1.5, mb: 1 }}>
                      <Box sx={{ width: 22, height: 22, borderRadius: "50%", bgcolor: primary,
                        display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                        <Typography fontSize={11} color="#fff" fontWeight={700}>{i + 1}</Typography>
                      </Box>
                      <Typography fontSize={14} color={textMain} mt={0.2}>{line}</Typography>
                    </Box>
                  ))
                ) : (
                  <Typography fontSize={14} color={textMuted} fontStyle="italic">No steps listed.</Typography>
                )}
              </Box>
            </Box>

          </Paper>
        )}
      </Box>

      {/* ── Add/Edit Modal ────────────────────────────────────────────────── */}
      <Dialog open={modalOpen} onClose={() => setModalOpen(false)} maxWidth="sm" fullWidth
        PaperProps={{ sx: { borderRadius: 3 } }}>
        <DialogTitle sx={{ fontWeight: 600, fontFamily: "'Playfair Display', serif" }}>
          {editMode ? "Edit Recipe" : "New Recipe"}
        </DialogTitle>
        <DialogContent sx={{ display: "flex", flexDirection: "column", gap: 2, pt: "12px !important" }}>

          {/* Image upload */}
          <Box
            onClick={() => fileRef.current?.click()}
            sx={{
              width: "100%", height: 140, borderRadius: 2.5,
              border: `2px dashed ${primary}55`,
              bgcolor: primary + "08",
              display: "flex", flexDirection: "column",
              alignItems: "center", justifyContent: "center",
              cursor: "pointer", transition: "all 0.2s",
              "&:hover": { bgcolor: primary + "15" },
              overflow: "hidden", position: "relative",
            }}>
            {form.image_url ? (
              <Box component="img" src={form.image_url} alt="preview"
                sx={{ width: "100%", height: "100%", objectFit: "cover" }} />
            ) : imgUploading ? (
              <CircularProgress size={28} />
            ) : (
              <>
                <ImageIcon sx={{ fontSize: 36, color: primary, mb: 0.5 }} />
                <Typography variant="caption" color={textMuted}>
                  Click to upload a photo
                </Typography>
              </>
            )}
          </Box>
          <input ref={fileRef} type="file" accept="image/*" style={{ display: "none" }}
            onChange={e => handleImageUpload(e.target.files[0])} />

          <TextField label="Recipe Title" fullWidth required value={form.title}
            onChange={e => setForm(f => ({ ...f, title: e.target.value }))} sx={inputSx} />

          <FormControl fullWidth>
            <InputLabel>Category</InputLabel>
            <Select value={form.category} label="Category"
              onChange={e => setForm(f => ({ ...f, category: e.target.value }))}
              sx={{ borderRadius: 2 }}>
              {CATEGORIES.filter(c => c !== "All").map(c => (
                <MenuItem key={c} value={c}>{CATEGORY_EMOJI[c]} {c}</MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* Budget range */}
          <Box sx={{ display: "flex", gap: 2 }}>
            <TextField label="Budget Min (₱)" type="number" fullWidth value={form.budget_min}
              onChange={e => setForm(f => ({ ...f, budget_min: e.target.value }))} sx={inputSx}
              InputProps={{ startAdornment: <InputAdornment position="start">₱</InputAdornment> }} />
            <TextField label="Budget Max (₱)" type="number" fullWidth value={form.budget_max}
              onChange={e => setForm(f => ({ ...f, budget_max: e.target.value }))} sx={inputSx}
              InputProps={{ startAdornment: <InputAdornment position="start">₱</InputAdornment> }} />
          </Box>

          <TextField label="Ingredients (one per line)" fullWidth multiline rows={4}
            placeholder={"2 cups flour\n1 tsp salt\n3 eggs"}
            value={form.ingredients}
            onChange={e => setForm(f => ({ ...f, ingredients: e.target.value }))} sx={inputSx} />

          <TextField label="Steps (one per line)" fullWidth multiline rows={5}
            placeholder={"Mix dry ingredients\nAdd wet ingredients\nBake at 180°C for 30 mins"}
            value={form.steps}
            onChange={e => setForm(f => ({ ...f, steps: e.target.value }))} sx={inputSx} />

        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3, gap: 1 }}>
          <Button onClick={() => setModalOpen(false)} sx={{ borderRadius: 50 }}>Cancel</Button>
          <Button onClick={handleSave} variant="contained" disabled={saving}
            startIcon={<SaveIcon />} sx={{ borderRadius: 50, px: 3 }}>
            {saving ? "Saving..." : editMode ? "Save Changes" : "Add Recipe"}
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
