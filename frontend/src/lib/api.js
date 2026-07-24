import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "";
export const API = `${BACKEND_URL}/api`;

export const api = axios.create({ baseURL: API, timeout: 10000 });

/**
 * Runs an API call and falls back to local seed-style data if the backend
 * isn't reachable yet (e.g. while wiring up hosting/DB). Once the backend is
 * live, real data flows through automatically — nothing else to change.
 */
export async function fetchWithFallback(request, fallback) {
  try {
    const res = await request();
    return res.data;
  } catch (err) {
    return fallback;
  }
}

export const subscribeToNewsletter = (payload) =>
  api.post("/newsletter/subscribe", payload);

export const submitEnquiry = (payload) => api.post("/enquiries", payload);

export const getArticles = (params) => api.get("/articles", { params });
export const getMagazineCurrentIssue = () => api.get("/magazine/current");
export const getMagazineIssues = (params) => api.get("/magazine/issues", { params });
export const getAwardCategories = (params) => api.get("/awards/categories", { params });
export const getAwardWinners = (params) => api.get("/awards/winners", { params });
export const getPodcastEpisodes = (params) => api.get("/podcast/episodes", { params });
