import { API_BASE } from "./constants";

export interface AuthUser {
  id: number;
  email?: string | null;
  phone?: string | null;
  role: "job_seeker" | "employer" | "admin";
  preferred_locale: string;
}

export function authHeaders(): HeadersInit {
  if (typeof window === "undefined") return {};
  const token = localStorage.getItem("access_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export function parseApiError(detail: unknown): string {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((e) => (typeof e === "object" && e && "msg" in e ? String((e as { msg: string }).msg) : String(e))).join(", ");
  }
  return "Something went wrong";
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const headers: Record<string, string> = {
    ...(authHeaders() as Record<string, string>),
    ...(init?.headers as Record<string, string>),
  };
  if (init?.body && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(parseApiError(body.detail));
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export function setTokens(access: string, refresh: string) {
  localStorage.setItem("access_token", access);
  localStorage.setItem("refresh_token", refresh);
}

export function clearTokens() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

export function getStoredToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

export async function login(email: string, password: string): Promise<AuthUser> {
  const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(parseApiError(body.detail));
  }
  const data = await res.json();
  setTokens(data.access_token, data.refresh_token);
  return getMe();
}

export async function register(email: string, password: string, role: "job_seeker" | "employer"): Promise<AuthUser> {
  const res = await fetch(`${API_BASE}/api/v1/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, role }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(parseApiError(body.detail));
  }
  const data = await res.json();
  setTokens(data.access_token, data.refresh_token);
  return getMe();
}

export async function getMe(): Promise<AuthUser> {
  return apiFetch<AuthUser>("/api/v1/auth/me");
}

export function logout() {
  clearTokens();
}
