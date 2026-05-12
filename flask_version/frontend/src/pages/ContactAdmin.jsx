import { Box, Paper, Typography, Avatar, Button, Chip } from "@mui/material";
import EmailIcon from "@mui/icons-material/Email";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { useNavigate } from "react-router-dom";

const admins = [
  {
    name: "Ayelyn Panliboton",
    role: "Developer",
    email: "dueitsquad.taskwise@gmail.com",
    image: "/admin-ayelyn.jpg",
  },
  {
    name: "Ivy Pauline Muit",
    role: "Developer",
    email: "dueitsquad.taskwise@gmail.com",
    image: "/admin-ivy.jpg",
  },
  {
    name: "Rhea Lizza Sanglay",
    role: "Developer",
    email: "dueitsquad.taskwise@gmail.com",
    image: "/admin-rhea.jpg",
  },
];

export default function ContactAdmin() {
  const navigate = useNavigate();

  return (
    <Box
      sx={{
        minHeight: "100vh",
        bgcolor: "rgba(34, 196, 172, 0.3)",
        px: { xs: 2, md: 6 },
        py: 4,
      }}
    >
      <Button
        startIcon={<ArrowBackIcon />}
        onClick={() => navigate("/")}
        sx={{ mb: 3, borderRadius: 50 }}
      >
        Back
      </Button>

      <Box sx={{ textAlign: "center", mb: 5 }}>
        <Typography
          variant="h3"
          fontWeight={800}
          sx={{ fontFamily: "'Playfair Display', serif" }}
        >
          Due-It Squad
        </Typography>

        <Typography color="text.secondary" mt={1}>
          Reach out to the TaskWise admins for account, task, or system support.
        </Typography>
      </Box>

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: {
            xs: "1fr",
            md: "repeat(3, 1fr)",
          },
          gap: 3,
          maxWidth: 1100,
          mx: "auto",
        }}
      >
        {admins.map((admin) => (
          <Paper
            key={admin.name}
            sx={{
              p: 4,
              borderRadius: 5,
              textAlign: "center",
              bgcolor: "background.paper",
              border: "1px solid",
              borderColor: "divider",
              boxShadow: "0 10px 30px rgba(0,0,0,0.08)",
              transition: "0.2s",
              "&:hover": {
                transform: "translateY(-6px)",
                boxShadow: "0 14px 35px rgba(0,0,0,0.12)",
              },
            }}
          >
            <Avatar
              src={admin.image}
              alt={admin.name}
              sx={{
                width: 110,
                height: 110,
                mx: "auto",
                mb: 2,
                border: "4px solid",
                borderColor: "primary.main",
              }}
            />

            <Typography variant="h5" fontWeight={800}>
              {admin.name}
            </Typography>

            <Chip
              label={admin.role}
              size="small"
              sx={{
                mt: 1,
                mb: 2,
                borderRadius: 50,
                bgcolor: "primary.main",
                color: "#fff",
                fontWeight: 700,
              }}
            />

            <Typography color="text.secondary" fontSize={14} mb={3}>
              Need help? Send a message to this admin for support.
            </Typography>

            <Button
              fullWidth
              component="a"
              target="_blank"
              rel="noopener noreferrer"
              variant="contained"
              startIcon={<EmailIcon />}
              href={`https://mail.google.com/mail/?view=cm&fs=1&to=${admin.email}`}
              sx={{ borderRadius: 50 }}
            >
              Email {admin.name}
            </Button>
          </Paper>
        ))}
      </Box>
    </Box>
  );
}