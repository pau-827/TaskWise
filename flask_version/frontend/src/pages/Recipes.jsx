import { useMemo, useState, useContext, useEffect } from "react";
import {
  Box,
  Paper,
  Typography,
  TextField,
  InputAdornment,
  Chip,
  Grid,
  Button,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  MenuItem,
  Snackbar,
  Alert,
  LinearProgress,
} from "@mui/material";

import SearchIcon from "@mui/icons-material/Search";
import AddIcon from "@mui/icons-material/Add";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import RestaurantMenuIcon from "@mui/icons-material/RestaurantMenu";
import TimerIcon from "@mui/icons-material/Timer";
import LocalFireDepartmentIcon from "@mui/icons-material/LocalFireDepartment";

import { ThemeContext } from "../context/ThemeContext";
import { THEMES } from "../theme/themes";
import { AppContext } from "../context/AppContext";
import { supabase } from "../services/supabase";

const CATEGORIES = [
  "All",
  "Breakfast",
  "Lunch",
  "Dinner",
  "Dessert",
  "Snack",
];

const emptyRecipe = {
  title: "",
  category: "Dinner",
  cook_time: "",
  calories: "",
  image_url: "",
  ingredients: "",
  instructions: "",
  progress: 0,
};

function RecipeModal({
  open,
  onClose,
  onSave,
  editRecipe,
}) {
  const [form, setForm] = useState(emptyRecipe);

  useEffect(() => {
    if (editRecipe) {
      setForm({
        title: editRecipe.title || "",
        category: editRecipe.category || "Dinner",
        cook_time: editRecipe.cook_time || "",
        calories: editRecipe.calories || "",
        image_url: editRecipe.image_url || "",
        ingredients: editRecipe.ingredients || "",
        instructions: editRecipe.instructions || "",
        progress: editRecipe.progress || 0,
      });
    } else {
      setForm(emptyRecipe);
    }
  }, [editRecipe, open]);

  const handleSave = async () => {
    if (!form.title.trim()) return;
    await onSave(form);
    onClose();
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      fullWidth
      maxWidth="sm"
      PaperProps={{
        sx: {
          borderRadius: 4,
        },
      }}
    >
      <DialogTitle
        sx={{
          fontWeight: 700,
          fontFamily: "'Playfair Display', serif",
        }}
      >
        {editRecipe ? "Edit Recipe" : "Add Recipe"}
      </DialogTitle>

      <DialogContent
        sx={{
          display: "flex",
          flexDirection: "column",
          gap: 2,
          pt: "12px !important",
        }}
      >
        <TextField
          label="Recipe Title"
          fullWidth
          value={form.title}
          onChange={(e) =>
            setForm({
              ...form,
              title: e.target.value,
            })
          }
        />

        <TextField
          select
          label="Category"
          value={form.category}
          onChange={(e) =>
            setForm({
              ...form,
              category: e.target.value,
            })
          }
        >
          {CATEGORIES.filter((c) => c !== "All").map(
            (cat) => (
              <MenuItem key={cat} value={cat}>
                {cat}
              </MenuItem>
            )
          )}
        </TextField>

        <Grid container spacing={2}>
          <Grid item xs={6}>
            <TextField
              label="Cook Time"
              fullWidth
              placeholder="30 mins"
              value={form.cook_time}
              onChange={(e) =>
                setForm({
                  ...form,
                  cook_time: e.target.value,
                })
              }
            />
          </Grid>

          <Grid item xs={6}>
            <TextField
              label="Calories"
              fullWidth
              placeholder="450"
              value={form.calories}
              onChange={(e) =>
                setForm({
                  ...form,
                  calories: e.target.value,
                })
              }
            />
          </Grid>
        </Grid>

        <TextField
          label="Food Image URL"
          fullWidth
          placeholder="https://..."
          value={form.image_url}
          onChange={(e) =>
            setForm({
              ...form,
              image_url: e.target.value,
            })
          }
        />

        <TextField
          label="Ingredients"
          multiline
          rows={4}
          fullWidth
          placeholder="List ingredients here..."
          value={form.ingredients}
          onChange={(e) =>
            setForm({
              ...form,
              ingredients: e.target.value,
            })
          }
        />

        <TextField
          label="Instructions"
          multiline
          rows={5}
          fullWidth
          placeholder="Write cooking steps here..."
          value={form.instructions}
          onChange={(e) =>
            setForm({
              ...form,
              instructions: e.target.value,
            })
          }
        />

        <Box>
          <Typography
            variant="body2"
            color="text.secondary"
            mb={1}
          >
            Cooking Progress ({form.progress}%)
          </Typography>

          <LinearProgress
            variant="determinate"
            value={form.progress}
            sx={{
              height: 10,
              borderRadius: 999,
              mb: 1,
            }}
          />

          <TextField
            type="number"
            fullWidth
            label="Progress %"
            value={form.progress}
            onChange={(e) =>
              setForm({
                ...form,
                progress: Number(e.target.value),
              })
            }
          />
        </Box>
      </DialogContent>

      <DialogActions sx={{ p: 2 }}>
        <Button
          onClick={onClose}
          sx={{
            borderRadius: 999,
          }}
        >
          Cancel
        </Button>

        <Button
          variant="contained"
          onClick={handleSave}
          sx={{
            borderRadius: 999,
            px: 3,
          }}
        >
          Save Recipe
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default function Recipes() {
  const { user } = useContext(AppContext);
  const { themeName } = useContext(ThemeContext);

  const landing =
    THEMES[themeName]?.custom?.landing;

  const [recipes, setRecipes] = useState([]);
  const [search, setSearch] = useState("");
  const [activeCategory, setActiveCategory] =
    useState("All");

  const [modalOpen, setModalOpen] =
    useState(false);

  const [editRecipe, setEditRecipe] =
    useState(null);

  const [snack, setSnack] = useState({
    open: false,
    msg: "",
    severity: "success",
  });

  const showSnack = (
    msg,
    severity = "success"
  ) => {
    setSnack({
      open: true,
      msg,
      severity,
    });
  };

  const fetchRecipes = async () => {
    const { data, error } = await supabase
      .from("recipes")
      .select("*")
      .eq("user_id", user.id)
      .order("created_at", {
        ascending: false,
      });

    if (!error) {
      setRecipes(data || []);
    }
  };

  useEffect(() => {
    if (user) {
      fetchRecipes();
    }
  }, [user]);

  const handleSave = async (form) => {
    const payload = {
      ...form,
      user_id: user.id,
    };

    if (editRecipe) {
      const { error } = await supabase
        .from("recipes")
        .update(payload)
        .eq("id", editRecipe.id);

      if (!error) {
        showSnack("Recipe updated!");
        fetchRecipes();
      }
    } else {
      const { error } = await supabase
        .from("recipes")
        .insert(payload);

      if (!error) {
        showSnack("Recipe added!");
        fetchRecipes();
      }
    }
  };

  const deleteRecipe = async (id) => {
    const { error } = await supabase
      .from("recipes")
      .delete()
      .eq("id", id);

    if (!error) {
      setRecipes((prev) =>
        prev.filter((recipe) => recipe.id !== id)
      );

      showSnack("Recipe deleted.");
    }
  };

  const filteredRecipes = useMemo(() => {
    return recipes.filter((recipe) => {
      const matchesCategory =
        activeCategory === "All" ||
        recipe.category === activeCategory;

      const matchesSearch =
        recipe.title
          .toLowerCase()
          .includes(search.toLowerCase());

      return matchesCategory && matchesSearch;
    });
  }, [recipes, search, activeCategory]);

  return (
    <Box
      sx={{
        width: "100%",
        maxWidth: "100%",
        overflowX: "hidden",
      }}
    >
      {/* HEADER */}
      <Paper
        sx={{
          p: { xs: 3, md: 5 },
          borderRadius: 5,
          mb: 4,
          background: `linear-gradient(135deg, ${landing?.accentLight}, ${landing?.pageBg})`,
          border: "1px solid",
          borderColor: landing?.cardBorder,
        }}
      >
        <Typography
          variant="h3"
          sx={{
            fontWeight: 700,
            mb: 1,
            fontFamily:
              "'Playfair Display', serif",
            color: landing?.headingMain,
            fontSize: {
              xs: "2rem",
              md: "3rem",
            },
          }}
        >
          🍳 My Recipes
        </Typography>

        <Typography
          sx={{
            color: landing?.bodyText,
            mb: 3,
            maxWidth: 700,
            lineHeight: 1.7,
          }}
        >
          Save your favorite meals, cooking
          ideas, ingredients, and instructions
          all in one place.
        </Typography>

        <Box
          sx={{
            display: "flex",
            gap: 2,
            flexDirection: {
              xs: "column",
              sm: "row",
            },
          }}
        >
          <TextField
            fullWidth
            placeholder="Search recipes..."
            value={search}
            onChange={(e) =>
              setSearch(e.target.value)
            }
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
              sx: {
                borderRadius: 999,
                bgcolor: "background.paper",
              },
            }}
          />

          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => {
              setEditRecipe(null);
              setModalOpen(true);
            }}
            sx={{
              borderRadius: 999,
              px: 3,
              minWidth: 180,
            }}
          >
            Add Recipe
          </Button>
        </Box>
      </Paper>

      {/* FILTERS */}
      <Box
        sx={{
          display: "flex",
          flexWrap: "wrap",
          gap: 1,
          mb: 4,
        }}
      >
        {CATEGORIES.map((category) => (
          <Chip
            key={category}
            label={category}
            clickable
            onClick={() =>
              setActiveCategory(category)
            }
            icon={<RestaurantMenuIcon />}
            color={
              activeCategory === category
                ? "primary"
                : "default"
            }
            variant={
              activeCategory === category
                ? "filled"
                : "outlined"
            }
            sx={{
              borderRadius: 999,
              fontWeight: 600,
            }}
          />
        ))}
      </Box>

      {/* RECIPE GRID */}
      <Grid container spacing={3}>
        {filteredRecipes.map((recipe) => (
          <Grid
            item
            xs={12}
            sm={6}
            xl={4}
            key={recipe.id}
          >
            <Paper
              sx={{
                borderRadius: 4,
                overflow: "hidden",
                height: "100%",
                display: "flex",
                flexDirection: "column",
                transition: "0.25s",
                border: "1px solid",
                borderColor: "divider",
                "&:hover": {
                  transform: "translateY(-4px)",
                  boxShadow: 6,
                },
              }}
            >
              <Box
                sx={{
                  height: 220,
                  overflow: "hidden",
                  bgcolor: "#ddd",
                }}
              >
                {recipe.image_url ? (
                  <Box
                    component="img"
                    src={recipe.image_url}
                    alt={recipe.title}
                    sx={{
                      width: "100%",
                      height: "100%",
                      objectFit: "cover",
                    }}
                  />
                ) : (
                  <Box
                    sx={{
                      width: "100%",
                      height: "100%",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                    }}
                  >
                    <Typography fontSize={50}>
                      🍽️
                    </Typography>
                  </Box>
                )}
              </Box>

              <Box
                sx={{
                  p: 2.5,
                  display: "flex",
                  flexDirection: "column",
                  flexGrow: 1,
                }}
              >
                <Box
                  sx={{
                    display: "flex",
                    justifyContent:
                      "space-between",
                    alignItems: "flex-start",
                    gap: 1,
                    mb: 1,
                  }}
                >
                  <Typography
                    variant="h6"
                    sx={{
                      fontWeight: 700,
                    }}
                  >
                    {recipe.title}
                  </Typography>

                  <Box
                    sx={{
                      display: "flex",
                    }}
                  >
                    <IconButton
                      size="small"
                      onClick={() => {
                        setEditRecipe(recipe);
                        setModalOpen(true);
                      }}
                    >
                      <EditIcon fontSize="small" />
                    </IconButton>

                    <IconButton
                      size="small"
                      color="error"
                      onClick={() =>
                        deleteRecipe(recipe.id)
                      }
                    >
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </Box>
                </Box>

                <Box
                  sx={{
                    display: "flex",
                    flexWrap: "wrap",
                    gap: 1,
                    mb: 2,
                  }}
                >
                  <Chip
                    size="small"
                    label={recipe.category}
                    sx={{
                      borderRadius: 999,
                    }}
                  />

                  {recipe.cook_time && (
                    <Chip
                      size="small"
                      icon={<TimerIcon />}
                      label={recipe.cook_time}
                      sx={{
                        borderRadius: 999,
                      }}
                    />
                  )}

                  {recipe.calories && (
                    <Chip
                      size="small"
                      icon={
                        <LocalFireDepartmentIcon />
                      }
                      label={`${recipe.calories} cal`}
                      sx={{
                        borderRadius: 999,
                      }}
                    />
                  )}
                </Box>

                {recipe.ingredients && (
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{
                      mb: 2,
                    }}
                  >
                    {recipe.ingredients.slice(
                      0,
                      120
                    )}
                    ...
                  </Typography>
                )}

                <Typography
                  variant="body2"
                  color="text.secondary"
                  mb={1}
                >
                  Cooking Progress
                </Typography>

                <LinearProgress
                  variant="determinate"
                  value={recipe.progress || 0}
                  sx={{
                    height: 8,
                    borderRadius: 999,
                  }}
                />
              </Box>
            </Paper>
          </Grid>
        ))}
      </Grid>

      {/* EMPTY STATE */}
      {filteredRecipes.length === 0 && (
        <Paper
          sx={{
            mt: 4,
            p: 6,
            borderRadius: 4,
            textAlign: "center",
          }}
        >
          <Typography fontSize={60}>
            🍳
          </Typography>

          <Typography
            variant="h6"
            fontWeight={700}
            mb={1}
          >
            No recipes yet
          </Typography>

          <Typography color="text.secondary">
            Add your first recipe and start
            building your personal cookbook.
          </Typography>
        </Paper>
      )}

      {/* MODAL */}
      <RecipeModal
        open={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setEditRecipe(null);
        }}
        onSave={handleSave}
        editRecipe={editRecipe}
      />

      {/* SNACKBAR */}
      <Snackbar
        open={snack.open}
        autoHideDuration={3000}
        onClose={() =>
          setSnack((s) => ({
            ...s,
            open: false,
          }))
        }
        anchorOrigin={{
          vertical: "bottom",
          horizontal: "right",
        }}
      >
        <Alert
          severity={snack.severity}
          sx={{
            borderRadius: 2,
          }}
          onClose={() =>
            setSnack((s) => ({
              ...s,
              open: false,
            }))
          }
        >
          {snack.msg}
        </Alert>
      </Snackbar>
    </Box>
  );
}