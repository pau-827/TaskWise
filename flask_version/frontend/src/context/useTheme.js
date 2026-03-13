import { useContext } from "react";
import { ThemeContext } from "./ThemeContext";

export function useAppTheme() {
  return useContext(ThemeContext);
}
