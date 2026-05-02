import { useContext } from "react";
import { ThemeContext } from "../context/ThemeContext";

export function useAppTheme() {
  return useContext(ThemeContext);
}
