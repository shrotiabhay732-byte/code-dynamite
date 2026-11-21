const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const ORG_KEY = "caraxes_org_id";
const ROLE_KEY = "caraxes_role";
const DEMO_KEY = "caraxes_demo_key";

// TEMPORARY identity until real login: the chosen organisation and role live here.
export const getOrgId = () => localStorage.getItem(ORG_KEY) || "";
export const setOrgId = (id) => localStorage.setItem(ORG_KEY, id);
export const getRole = () => localStorage.getItem(ROLE_KEY) || "admin";
export const setRole = (role) => localStorage.setItem(ROLE_KEY, role || "admin");
const DEMO_NAMES = { creator: "Charlie Rivera", reviewer: "Aria Chen", admin: "Elena Park" };
export async function api(path, options = {}) {
  const headers = { ...(options.headers ?? {}) };
  // For file uploads the browser sets the Content-Type itself
  if (options.body && !(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }
  const token = localStorage.getItem("caraxes_auth_token") || localStorage.getItem("sb_token");
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const orgId = getOrgId();
  if (orgId) headers["X-Org-Id"] = orgId;
  const role = getRole();
  headers["X-Role"] = role;
  headers["X-User-Name"] = DEMO_NAMES[role] ?? role;
  const demoKey = localStorage.getItem(DEMO_KEY);
  if (demoKey) headers["X-Demo-Key"] = demoKey;

  let res;
  try {
    res = await fetch(`${API_URL}${path}`, { ...options, headers });
  } catch {
    throw new Error("Cannot reach the backend. Is it running? (A hosted backend can take about a minute to wake up.)");
  }

  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      if (body.detail) {
        detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
      }
    } catch {
      /* no JSON body */
    }
    if (res.status === 401 && detail === "Demo passcode required") {
      const entered = window.prompt("Enter the demo passcode");
      if (entered) {
        localStorage.setItem(DEMO_KEY, entered.trim());
        window.location.reload();
      }
    }
    throw new Error(detail);
  }
  return res.json();
}
// Public (no login) requests: no identity headers are sent, so nothing private can leak by accident
export const publicUrl = (path) => `${API_URL}${path}`;

export async function publicApi(path) {
  let res;
  try {
    res = await fetch(`${API_URL}${path}`);
  } catch {
    throw new Error("Cannot reach the server. It may be waking up, so try again in a minute.");
  }
  if (!res.ok) {
    throw new Error(res.status === 404 ? "This session is not available." : `Request failed (${res.status})`);
  }
  return res.json();
}