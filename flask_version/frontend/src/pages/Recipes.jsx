import { useState, useEffect, useContext, useCallback, useRef } from "react";
import {
  Box, Paper, Typography, IconButton, TextField, Button,
  Chip, CircularProgress, Tooltip, Snackbar, Alert, InputAdornment,
  Dialog, DialogTitle, DialogContent, DialogActions,
  FormControl, InputLabel, Select, MenuItem, Divider,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";
import SaveIcon from "@mui/icons-material/Save";
import SearchIcon from "@mui/icons-material/Search";
import ImageIcon from "@mui/icons-material/Image";
import AttachMoneyIcon from "@mui/icons-material/AttachMoney";
import RestaurantMenuIcon from "@mui/icons-material/RestaurantMenu";
import { supabase } from "../services/supabase";
import { AppContext } from "../context/AppContext";
import { ThemeContext } from "../context/ThemeContext";
import { THEMES } from "../theme/themes";

const CATEGORIES = ["All", "Breakfast", "Lunch", "Dinner", "Dessert", "Snack", "Beverages", "Others"];

const CATEGORY_EMOJI = {
  Breakfast: "🍳",
  Lunch: "🥗",
  Dinner: "🍽️",
  Dessert: "🍰",
  Snack: "🍿",
  Beverages: "🧋",
  Others: "🍴",
};

const empty = {
  title: "",
  category: "Others",
  ingredients: "",
  steps: "",
  budget_min: "",
  budget_max: "",
  image_url: "",
};

export default function Recipes() {
  const { user } = useContext(AppContext);
  const { themeName } = useContext(ThemeContext);

  const palette = THEMES[themeName]?.palette;
  const isDark = palette?.mode === "dark";

  const bgPaper = palette?.background?.paper ?? "#fff1f5";
  const primary = palette?.primary?.main ?? "#ff4f8b";
  const textMain = palette?.text?.primary ?? "#4a001f";
  const textMuted = palette?.text?.secondary ?? "#9b4b66";
  const borderCol = isDark ? "rgba(255,255,255,0.12)" : "rgba(0,0,0,0.08)";
  const rowBg = isDark ? "rgba(255,255,255,0.06)" : "rgba(255,255,255,0.75)";

  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("All");
  const [selected, setSelected] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [form, setForm] = useState(empty);
  const [imgUploading, setImgUploading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [snack, setSnack] = useState({ open: false, msg: "", severity: "success" });

  const fileRef = useRef();

  const showSnack = (msg, severity = "success") => {
    setSnack({ open: true, msg, severity });
  };

  const fetchRecipes = useCallback(async () => {
    if (!user) return;

    setLoading(true);

    const { data } = await supabase
      .from("recipes")
      .select("*")
      .eq("user_id", user.id)
      .order("created_at", { ascending: false });

    setRecipes(data || []);
    setLoading(false);
  }, [user]);

  useEffect(() => {
    fetchRecipes();
  }, [fetchRecipes]);

  const handleImageUpload = async (file) => {
    if (!file) return;

    setImgUploading(true);

    const ext = file.name.split(".").pop();
    const path = `${user.id}/${Date.now()}.${ext}`;

    const { error } = await supabase.storage
      .from("recipe-images")
      .upload(path, file);

    if (error) {
      showSnack("Image upload failed.", "error");
      setImgUploading(false);
      return;
    }

    const { data } = supabase.storage.from("recipe-images").getPublicUrl(path);

    setForm((f) => ({ ...f, image_url: data.publicUrl }));
    setImgUploading(false);
    showSnack("Image uploaded!");
  };

  const handleSave = async () => {
    if (!form.title.trim()) {
      showSnack("Title is required.", "warning");
      return;
    }

    setSaving(true);

    const payload = {
      ...form,
      user_id: user.id,
      budget_min: form.budget_min ? Number(form.budget_min) : null,
      budget_max: form.budget_max ? Number(form.budget_max) : null,
    };

    if (editMode && selected) {
      const { error } = await supabase
        .from("recipes")
        .update(payload)
        .eq("id", selected.id);

      if (!error) {
        showSnack("Recipe updated!");
        await fetchRecipes();
        setSelected((prev) => ({ ...prev, ...payload }));
        setModalOpen(false);
      } else {
        showSnack(error.message, "error");
      }
    } else {
      const { error } = await supabase.from("recipes").insert(payload);

      if (!error) {
        showSnack("Recipe added!");
        await fetchRecipes();
        setModalOpen(false);
      } else {
        showSnack(error.message, "error");
      }
    }

    setSaving(false);
  };

  const handleDelete = async (id) => {
    const { error } = await supabase.from("recipes").delete().eq("id", id);

    if (!error) {
      showSnack("Recipe deleted.");

      if (selected?.id === id) setSelected(null);

      await fetchRecipes();
    }
  };

  const openAdd = () => {
    setForm(empty);
    setEditMode(false);
    setModalOpen(true);
  };

  const openEdit = (r) => {
    setForm({
      title: r.title || "",
      category: r.category || "Others",
      ingredients: r.ingredients || "",
      steps: r.steps || "",
      budget_min: r.budget_min || "",
      budget_max: r.budget_max || "",
      image_url: r.image_url || "",
    });

    setEditMode(true);
    setModalOpen(true);
  };

  const filtered = recipes.filter((r) => {
    const matchCat = category === "All" || r.category === category;
    const matchSearch =
      r.title?.toLowerCase().includes(search.toLowerCase()) ||
      r.ingredients?.toLowerCase().includes(search.toLowerCase());

    return matchCat && matchSearch;
  });

  const inputSx = {
    "& .MuiOutlinedInput-root": {
      borderRadius: 3,
    },
  };

  return (
    <Box
      sx={{
        width: "100%",
        display: "flex",
        flexDirection: { xs: "column", lg: "row" },
        gap: 3,
        alignItems: "stretch",
        minHeight: "calc(100vh - 88px)",
      }}
    >
      <Box
        sx={{
          width: { xs: "100%", lg: 360 },
          flex: { xs: "1 1 auto", lg: "0 0 360px" },
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
            height: "calc(100vh - 140px)",
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
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
                Recipes
              </Typography>
              <Typography variant="caption" color={textMuted}>
                {recipes.length} saved recipe{recipes.length === 1 ? "" : "s"}
              </Typography>
            </Box>

            <Button
              variant="contained"
              startIcon={<AddIcon />}
              size="small"
              onClick={openAdd}
              sx={{ borderRadius: 50, px: 2 }}
            >
              Add
            </Button>
          </Box>

          <TextField
            fullWidth
            size="small"
            placeholder="Search recipes..."
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
            sx={{ mb: 1.5 }}
          />

          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.8, mb: 2 }}>
            {CATEGORIES.map((cat) => (
              <Chip
                key={cat}
                label={cat === "All" ? "All" : `${CATEGORY_EMOJI[cat]} ${cat}`}
                size="small"
                onClick={() => setCategory(cat)}
                variant={category === cat ? "filled" : "outlined"}
                color={category === cat ? "primary" : "default"}
                sx={{
                  borderRadius: 50,
                  fontSize: 11,
                  fontWeight: category === cat ? 700 : 500,
                }}
              />
            ))}
          </Box>

          <Box
            sx={{
              flexGrow: 1,
              minHeight: 0,
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
                <Typography fontSize={40} mb={1}>🍽️</Typography>
                <Typography fontWeight={700}>No recipes yet.</Typography>
                <Typography variant="caption">Add one using the button above.</Typography>
              </Box>
            ) : (
              <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5 }}>
                {filtered.map((r) => {
                  const active = selected?.id === r.id;

                  return (
                    <Paper
                      key={r.id}
                      variant="outlined"
                      onClick={() => setSelected(r)}
                      sx={{
                        borderRadius: 3,
                        overflow: "hidden",
                        cursor: "pointer",
                        borderColor: active ? primary : borderCol,
                        bgcolor: active ? primary + "18" : rowBg,
                        transition: "all 0.2s ease",
                        "&:hover": {
                          transform: "translateY(-3px)",
                          boxShadow: 3,
                          bgcolor: primary + "12",
                        },
                      }}
                    >
                      {r.image_url ? (
                        <Box
                          component="img"
                          src={r.image_url}
                          alt={r.title}
                          sx={{ width: "100%", height: 120, objectFit: "cover" }}
                        />
                      ) : (
                        <Box
                          sx={{
                            height: 92,
                            background: `linear-gradient(135deg, ${primary}24, ${primary}08)`,
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                          }}
                        >
                          <Typography fontSize={42}>{CATEGORY_EMOJI[r.category] || "🍴"}</Typography>
                        </Box>
                      )}

                      <Box sx={{ p: 1.5 }}>
                        <Typography fontWeight={800} fontSize={14} color={textMain} noWrap>
                          {r.title}
                        </Typography>

                        <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mt: 1, gap: 1 }}>
                          <Chip
                            label={`${CATEGORY_EMOJI[r.category] || "🍴"} ${r.category}`}
                            size="small"
                            sx={{
                              borderRadius: 50,
                              height: 20,
                              fontSize: 10,
                              bgcolor: primary + "22",
                              color: primary,
                              fontWeight: 700,
                            }}
                          />

                          {(r.budget_min || r.budget_max) && (
                            <Typography variant="caption" color={textMuted} fontWeight={700} fontSize={11}>
                              ₱{r.budget_min || 0}–{r.budget_max || "?"}
                            </Typography>
                          )}
                        </Box>
                      </Box>
                    </Paper>
                  );
                })}
              </Box>
            )}
          </Box>
        </Paper>
      </Box>

      <Box sx={{ flex: "1 1 0", minWidth: 0 }}>
        {!selected ? (
          <Paper
            sx={{
              p: 4,
              borderRadius: 4,
              bgcolor: bgPaper,
              minHeight: "calc(100vh - 140px)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "0 8px 24px rgba(0,0,0,0.06)",
            }}
          >
            <Box sx={{ textAlign: "center", color: textMuted }}>
              <RestaurantMenuIcon sx={{ fontSize: 70, color: primary, mb: 2 }} />
              <Typography variant="h5" fontWeight={800} color={textMain}>
                Select a recipe to view
              </Typography>
              <Typography variant="body2" mt={1}>
                Choose one from the list or add a new recipe.
              </Typography>
              <Button variant="contained" startIcon={<AddIcon />} onClick={openAdd} sx={{ mt: 3, borderRadius: 50 }}>
                Add Recipe
              </Button>
            </Box>
          </Paper>
        ) : (
          <Paper
            sx={{
              p: 3,
              borderRadius: 4,
              bgcolor: bgPaper,
              minHeight: "calc(100vh - 140px)",
              maxHeight: "calc(100vh - 140px)",
              display: "flex",
              flexDirection: "column",
              gap: 2,
              overflowY: "auto",
              boxShadow: "0 8px 24px rgba(0,0,0,0.06)",
              "&::-webkit-scrollbar": { width: 6 },
              "&::-webkit-scrollbar-track": { background: "rgba(0,0,0,0.04)", borderRadius: 10 },
              "&::-webkit-scrollbar-thumb": { borderRadius: 10, bgcolor: primary + "66" },
            }}
          >
            {selected.image_url ? (
              <Box
                component="img"
                src={selected.image_url}
                alt={selected.title}
                sx={{
                  width: "100%",
                  height: { xs: 180, md: 260 },
                  objectFit: "cover",
                  borderRadius: 3,
                }}
              />
            ) : (
              <Box
                sx={{
                  width: "100%",
                  height: { xs: 150, md: 220 },
                  borderRadius: 3,
                  background: `linear-gradient(135deg, ${primary}24, ${primary}08)`,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <Typography fontSize={72}>{CATEGORY_EMOJI[selected.category] || "🍴"}</Typography>
              </Box>
            )}

            <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 2 }}>
              <Box>
                <Typography
                  variant="h4"
                  fontWeight={800}
                  color={textMain}
                  sx={{ fontFamily: "'Playfair Display', serif" }}
                >
                  {selected.title}
                </Typography>

                <Box sx={{ display: "flex", gap: 1, mt: 1, flexWrap: "wrap" }}>
                  <Chip
                    label={`${CATEGORY_EMOJI[selected.category]} ${selected.category}`}
                    size="small"
                    sx={{ borderRadius: 50, bgcolor: primary + "22", color: primary, fontWeight: 700 }}
                  />

                  {(selected.budget_min || selected.budget_max) && (
                    <Chip
                      icon={<AttachMoneyIcon sx={{ fontSize: 14 }} />}
                      label={`₱${selected.budget_min || 0} – ₱${selected.budget_max || "?"}`}
                      size="small"
                      sx={{ borderRadius: 50, bgcolor: "#4CAF5022", color: "#4CAF50", fontWeight: 700 }}
                    />
                  )}
                </Box>
              </Box>

              <Box sx={{ display: "flex", gap: 0.5 }}>
                <Tooltip title="Edit">
                  <IconButton onClick={() => openEdit(selected)} sx={{ border: `1px solid ${borderCol}`, borderRadius: 2 }}>
                    <EditIcon fontSize="small" />
                  </IconButton>
                </Tooltip>

                <Tooltip title="Delete">
                  <IconButton color="error" onClick={() => handleDelete(selected.id)} sx={{ border: `1px solid ${borderCol}`, borderRadius: 2 }}>
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
            </Box>

            <Divider />

            <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: "1fr 1fr" }, gap: 2 }}>
              <Paper variant="outlined" sx={{ p: 2.5, borderRadius: 3, bgcolor: rowBg, borderColor: borderCol }}>
                <Typography fontWeight={800} fontSize={16} color={textMain} mb={1.5}>
                  Ingredients
                </Typography>

                {selected.ingredients ? (
                  selected.ingredients.split("\n").filter(Boolean).map((line, i) => (
                    <Box key={i} sx={{ display: "flex", gap: 1, mb: 1 }}>
                      <Typography color={primary} fontWeight={900}>•</Typography>
                      <Typography fontSize={14} color={textMain}>{line}</Typography>
                    </Box>
                  ))
                ) : (
                  <Typography fontSize={14} color={textMuted} fontStyle="italic">
                    No ingredients listed.
                  </Typography>
                )}
              </Paper>

              <Paper variant="outlined" sx={{ p: 2.5, borderRadius: 3, bgcolor: rowBg, borderColor: borderCol }}>
                <Typography fontWeight={800} fontSize={16} color={textMain} mb={1.5}>
                  Steps
                </Typography>

                {selected.steps ? (
                  selected.steps.split("\n").filter(Boolean).map((line, i) => (
                    <Box key={i} sx={{ display: "flex", gap: 1.5, mb: 1.5 }}>
                      <Box
                        sx={{
                          width: 24,
                          height: 24,
                          borderRadius: "50%",
                          bgcolor: primary,
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          flexShrink: 0,
                        }}
                      >
                        <Typography fontSize={11} color="#fff" fontWeight={800}>{i + 1}</Typography>
                      </Box>
                      <Typography fontSize={14} color={textMain} mt={0.2}>{line}</Typography>
                    </Box>
                  ))
                ) : (
                  <Typography fontSize={14} color={textMuted} fontStyle="italic">
                    No steps listed.
                  </Typography>
                )}
              </Paper>
            </Box>
          </Paper>
        )}
      </Box>

      <Dialog open={modalOpen} onClose={() => setModalOpen(false)} maxWidth="sm" fullWidth PaperProps={{ sx: { borderRadius: 4 } }}>
        <DialogTitle sx={{ fontWeight: 800, fontFamily: "'Playfair Display', serif" }}>
          {editMode ? "Edit Recipe" : "New Recipe"}
        </DialogTitle>

        <DialogContent sx={{ display: "flex", flexDirection: "column", gap: 2, pt: "12px !important" }}>
          <Box
            onClick={() => fileRef.current?.click()}
            sx={{
              width: "100%",
              height: 150,
              borderRadius: 3,
              border: `2px dashed ${primary}66`,
              bgcolor: primary + "08",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              cursor: "pointer",
              transition: "all 0.2s",
              "&:hover": { bgcolor: primary + "15" },
              overflow: "hidden",
            }}
          >
            {form.image_url ? (
              <Box component="img" src={form.image_url} alt="preview" sx={{ width: "100%", height: "100%", objectFit: "cover" }} />
            ) : imgUploading ? (
              <CircularProgress size={28} />
            ) : (
              <>
                <ImageIcon sx={{ fontSize: 38, color: primary, mb: 0.5 }} />
                <Typography variant="caption" color={textMuted}>
                  Click to upload a recipe photo
                </Typography>
              </>
            )}
          </Box>

          <input
            ref={fileRef}
            type="file"
            accept="image/*"
            style={{ display: "none" }}
            onChange={(e) => handleImageUpload(e.target.files[0])}
          />

          <TextField
            label="Recipe Title"
            fullWidth
            required
            value={form.title}
            onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
            sx={inputSx}
          />

          <FormControl fullWidth>
            <InputLabel>Category</InputLabel>
            <Select
              value={form.category}
              label="Category"
              onChange={(e) => setForm((f) => ({ ...f, category: e.target.value }))}
              sx={{ borderRadius: 3 }}
            >
              {CATEGORIES.filter((c) => c !== "All").map((c) => (
                <MenuItem key={c} value={c}>
                  {CATEGORY_EMOJI[c]} {c}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Box sx={{ display: "flex", gap: 2 }}>
            <TextField
              label="Budget Min"
              type="number"
              fullWidth
              value={form.budget_min}
              onChange={(e) => setForm((f) => ({ ...f, budget_min: e.target.value }))}
              sx={inputSx}
              InputProps={{ startAdornment: <InputAdornment position="start">₱</InputAdornment> }}
            />

            <TextField
              label="Budget Max"
              type="number"
              fullWidth
              value={form.budget_max}
              onChange={(e) => setForm((f) => ({ ...f, budget_max: e.target.value }))}
              sx={inputSx}
              InputProps={{ startAdornment: <InputAdornment position="start">₱</InputAdornment> }}
            />
          </Box>

          <TextField
            label="Ingredients"
            fullWidth
            multiline
            rows={4}
            placeholder={"2 cups flour\n1 tsp salt\n3 eggs"}
            value={form.ingredients}
            onChange={(e) => setForm((f) => ({ ...f, ingredients: e.target.value }))}
            sx={inputSx}
          />

          <TextField
            label="Steps"
            fullWidth
            multiline
            rows={5}
            placeholder={"Mix dry ingredients\nAdd wet ingredients\nBake for 30 minutes"}
            value={form.steps}
            onChange={(e) => setForm((f) => ({ ...f, steps: e.target.value }))}
            sx={inputSx}
          />
        </DialogContent>

        <DialogActions sx={{ px: 3, pb: 3, gap: 1 }}>
          <Button onClick={() => setModalOpen(false)} sx={{ borderRadius: 50 }}>
            Cancel
          </Button>

          <Button
            onClick={handleSave}
            variant="contained"
            disabled={saving}
            startIcon={<SaveIcon />}
            sx={{ borderRadius: 50, px: 3 }}
          >
            {saving ? "Saving..." : editMode ? "Save Changes" : "Add Recipe"}
          </Button>
        </DialogActions>
      </Dialog>

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