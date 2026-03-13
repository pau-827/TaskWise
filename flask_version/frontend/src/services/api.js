import axios from "axios";

const API_URL = "http://localhost:5000/api";

export const getTasks = async () => {
  const res = await axios.get(`${API_URL}/tasks`);
  return res.data;
};