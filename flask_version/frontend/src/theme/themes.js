export const THEMES = {
  light: {
    palette: {
      mode: "light",
      background: {
        default: "#97C7C3",
        paper: "#E3F4F4"
      },
      primary: {
        main: "#4A707A"
      },
      secondary: {
        main: "#6B8F97"
      },
      success: {
        main: "#4CAF50"
      },
      error: {
        main: "#E53935"
      }
    },
    custom: {
      headerBg: "#F8F6F4",
      border: "#4A707A",
      chartColors: ["#035477","#2A9D8F","#4A707A","#F4A261","#A855F7"],

      // Used by LandingPage & LoadingScreen
      landing: {
        pageBg:      "#f0f7f5",
        blobColor:   "rgba(167,210,197,0.25)",
        blobColor2:  "rgba(167,210,197,0.18)",
        blobColor3:  "rgba(167,210,197,0.13)",
        navBg:       "rgba(240,247,245,0.88)",
        navBorder:   "rgba(120,180,160,0.18)",
        logoText:    "#2d6a55",
        headingMain: "#1a4a3a",
        headingAccent:"#4a9b82",
        bodyText:    "#4a7a68",
        mutedText:   "#7aaa97",
        pillBg:      "#d6ede6",
        pillText:    "#2d6a55",
        cardBg:      "#fff",
        cardBorder:  "#c5e0d8",
        accent:      "#4a9b82",
        accentHover: "#3a8270",
        accentLight: "#e8f5f0",
        progressBg:  "#c5e0d8",
        progressBar: "linear-gradient(90deg, #7bbfaa, #4a9b82)",
        iconBg:      "#4a9b82",
        tagBg:       "#e8f5f0",
        tagText:     "#2d6a55",
      }
    }
  },

  pink: {
    palette: {
      mode: "light",
      background: {
        default: "#FFD1D9",
        paper: "#FF8FB0"
      },
      primary: {
        main: "#FF4D84"
      }
    },
    custom: {
      headerBg: "#FF77A0",
      border: "#4A0B1F",
      chartColors: ["#BE123C","#FF4D84","#EE6983","#FFC4C4","#CD2C58"],

      landing: {
        pageBg:       "#fff0f3",
        blobColor:    "rgba(255,155,180,0.25)",
        blobColor2:   "rgba(255,155,180,0.18)",
        blobColor3:   "rgba(255,155,180,0.13)",
        navBg:        "rgba(255,240,243,0.88)",
        navBorder:    "rgba(255,120,160,0.18)",
        logoText:     "#c0325a",
        headingMain:  "#5a0a1f",
        headingAccent:"#ff4d84",
        bodyText:     "#a04060",
        mutedText:    "#d47090",
        pillBg:       "#ffd6e0",
        pillText:     "#c0325a",
        cardBg:       "#fff",
        cardBorder:   "#ffc0d0",
        accent:       "#ff4d84",
        accentHover:  "#e0336a",
        accentLight:  "#fff0f3",
        progressBg:   "#ffc0d0",
        progressBar:  "linear-gradient(90deg, #ff90b0, #ff4d84)",
        iconBg:       "#ff4d84",
        tagBg:        "#ffd6e0",
        tagText:      "#c0325a",
      }
    }
  },

  dark: {
    palette: {
      mode: "dark",
      background: {
        default: "#23262B",
        paper: "#3D4148"
      },
      primary: {
        main: "#959595"
      }
    },
    custom: {
      headerBg: "#0A1426",
      border: "#22314B",
      chartColors: ["#1B3C53","#234C6A","#456882","#D2C1B6","#715A5A"],

      landing: {
        pageBg:       "#1a1d22",
        blobColor:    "rgba(60,80,100,0.35)",
        blobColor2:   "rgba(60,80,100,0.25)",
        blobColor3:   "rgba(60,80,100,0.18)",
        navBg:        "rgba(26,29,34,0.92)",
        navBorder:    "rgba(100,120,150,0.2)",
        logoText:     "#a0b8c8",
        headingMain:  "#dce6ed",
        headingAccent:"#5b8fa8",
        bodyText:     "#8a9fad",
        mutedText:    "#5a7080",
        pillBg:       "#2a3540",
        pillText:     "#a0b8c8",
        cardBg:       "#23262b",
        cardBorder:   "#2e3540",
        accent:       "#5b8fa8",
        accentHover:  "#4a7a90",
        accentLight:  "#2a3540",
        progressBg:   "#2e3540",
        progressBar:  "linear-gradient(90deg, #3a6080, #5b8fa8)",
        iconBg:       "#5b8fa8",
        tagBg:        "#2a3540",
        tagText:      "#a0b8c8",
      }
    }
  }
};