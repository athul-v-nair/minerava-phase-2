import { authHeaders } from "./auth";

const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export async function fetchHealth(): Promise<{ status: string; version: string }> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
  return res.json();
}

// auth
export type UserOut = { id: string; email: string; orgId: string | null; role: string; created_at: string };
export type OrgOut = { id: string; name: string; created_at: string };

function apiError(detail: unknown, fallback: string): string {
  if (typeof detail === "string") return detail;
  if (detail == null) return fallback;
  try {
    return JSON.stringify(detail);
  } catch {
    return fallback;
  }
}

export async function register(payload: { email: string; password: string; orgName?: string }) {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(apiError(body.detail, `Register failed ${res.status}`));
  }
  return res.json() as Promise<{ access_token: string; refresh_token: string; user: UserOut; org: OrgOut | null }>;
}

export async function login(payload: { email: string; password: string }) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(apiError(body.detail, `Login failed ${res.status}`));
  }
  return res.json() as Promise<{ access_token: string; refresh_token: string; user: UserOut; org: OrgOut | null }>;
}

export async function fetchMe(): Promise<{ user: UserOut; org: OrgOut | null }> {
  const res = await fetch(`${API_BASE}/me`, { headers: { ...authHeaders() } });
  if (!res.ok) throw new Error(`me failed ${res.status}`);
  return res.json();
}

export async function fetchMyOrg(): Promise<OrgOut> {
  const res = await fetch(`${API_BASE}/orgs/me`, { headers: { ...authHeaders() } });
  if (!res.ok) throw new Error(`orgs/me failed ${res.status}`);
  return res.json();
}

export async function fetchOrgDetail(orgId: string): Promise<{ org: OrgOut; members: UserOut[] }> {
  const res = await fetch(`${API_BASE}/orgs/${orgId}`, { headers: { ...authHeaders() } });
  if (!res.ok) throw new Error(`org detail failed ${res.status}`);
  return res.json();
}

export async function patchOrg(orgId: string, name: string): Promise<OrgOut> {
  const res = await fetch(`${API_BASE}/orgs/${orgId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ name }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(apiError(body.detail, `patch failed ${res.status}`));
  }
  return res.json();
}
