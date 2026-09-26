export type Row = Record<string, any>;
let csrf = "";
let sessionEpoch = 0;
export function setCsrf(value: string) {
  if (csrf !== value) sessionEpoch += 1;
  csrf = value;
}
export async function api<T = any>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const requestEpoch = sessionEpoch;
  const headers = new Headers(options.headers);
  if (!(options.body instanceof FormData) && options.body)
    headers.set("Content-Type", "application/json");
  if (csrf) headers.set("X-CSRF-Token", csrf);
  const response = await fetch("/api" + path, {
    ...options,
    headers,
    credentials: "same-origin",
  });
  if (requestEpoch !== sessionEpoch)
    throw new Error("Session changed; stale response discarded.");
  let data: any;
  try {
    data = await response.json();
  } catch {
    data = { detail: await response.text().catch(() => response.statusText) };
  }
  if (requestEpoch !== sessionEpoch)
    throw new Error("Session changed; stale response discarded.");
  if (!response.ok) {
    if (response.status === 401 && path !== "/auth/login")
      window.dispatchEvent(new Event("atlas:session-expired"));
    const message = Array.isArray(data.detail)
      ? data.detail
          .map((d: Row) => `${d.loc.slice(1).join(".")}: ${d.msg}`)
          .join("; ")
      : data.detail;
    throw new Error(message || `Request failed (${response.status})`);
  }
  return data as T;
}
export const post = (
  path: string,
  data: unknown = {},
  headers?: Record<string, string>,
) => api(path, { method: "POST", body: JSON.stringify(data), headers });
export const date = (value: number) =>
  new Date(value * 1000).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
export const short = (value: string, length = 14) =>
  value.length > length * 2
    ? value.slice(0, length) + "…" + value.slice(-8)
    : value;
export function amount(value: string, decimals: number) {
  const padded = value.padStart(decimals + 1, "0");
  const fraction = decimals ? padded.slice(-decimals).replace(/0+$/, "") : "";
  return (
    (decimals ? padded.slice(0, -decimals) : padded) +
    (fraction ? "." + fraction : "")
  );
}
