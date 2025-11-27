const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function handleResponse(res: Response) {
  const contentType = res.headers.get("content-type") || "";
  if (!res.ok) {
    const body = contentType.includes("application/json") ? await res.json().catch(() => null) : await res.text().catch(() => null);
    let message = body?.detail || body?.message || res.statusText;
    if (typeof message === "object") message = JSON.stringify(message);
    throw new Error(message);
  }
  if (!contentType.includes("application/json")) return null;
  const data = await res.json();
  console.log("API response (raw):", res);
  return normalizeIds(data);
}

function normalizeIds(obj: any): any {
  if (Array.isArray(obj)) return obj.map(normalizeIds);
  if (obj && typeof obj === "object") {
    const out: Record<string, any> = {};
    for (const [k, v] of Object.entries(obj)) {
      if (k === "_id") out["id"] = String(v);
      else if (v && typeof v === "object") out[k] = normalizeIds(v);
      else out[k] = v;
    }
    return out;
  }
  return obj;
}

export async function apiFetch(
  path: string,
  method: string = "GET",
  body?: any,
  token?: string | null,
  options?: { headers?: Record<string, string> }
) {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...options?.headers,
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  if (body instanceof URLSearchParams && !options?.headers?.["Content-Type"]) {
    headers["Content-Type"] = "application/x-www-form-urlencoded";
  }

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body instanceof URLSearchParams ? body : (body ? JSON.stringify(body) : undefined),
  });

  console.log("API response (raw):", res);

  return handleResponse(res);
}
