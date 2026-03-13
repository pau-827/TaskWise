import { Grid, Paper, Typography, Box } from "@mui/material";

export default function Tasks() {
  return (
    <Box sx={{ width: "100%" }}>

      <Grid container spacing={3}>

        {/* TASK PANEL */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, borderRadius: 3, minHeight: 600 }}>
            <Typography variant="h5" sx={{ mb: 2 }}>
              Tasks
            </Typography>

            <Typography color="text.secondary">
              No tasks found in this category.
            </Typography>
          </Paper>
        </Grid>

        {/* SIDEBAR */}
        <Grid item xs={12} md={4}>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>

            <Paper sx={{ p: 3, borderRadius: 3, minHeight: 260 }}>
              <Typography variant="h6">
                Category Analytics
              </Typography>
            </Paper>

            <Paper sx={{ p: 3, borderRadius: 3 }}>
              <Typography variant="h6">Summary</Typography>

              <Typography>Total Tasks: 0</Typography>
              <Typography>Completed: 0</Typography>
              <Typography>Overdue: 0</Typography>

            </Paper>

          </Box>
        </Grid>

      </Grid>

    </Box>
  );
}
