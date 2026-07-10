// Base URL is configurable via env instead of being hardcoded across the
// codebase; falls back to the previous hardcoded value for local dev.
export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type RequestOptions = RequestInit & {
  /** Message surfaced to the user if the request fails. */
  errorMessage: string;
};

async function request(path: string, { errorMessage, ...init }: RequestOptions): Promise<Response> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    cache: "no-store",
    ...init,
  });

  if (!response.ok) {
    throw new Error(errorMessage);
  }

  return response;
}

export async function apiGetJson<T>(path: string, errorMessage: string): Promise<T> {
  const response = await request(path, { errorMessage });
  return (await response.json()) as T;
}

export async function apiSendJson<T>(
  path: string,
  init: RequestInit,
  errorMessage: string,
): Promise<T> {
  const response = await request(path, { ...init, errorMessage });
  return (await response.json()) as T;
}

export async function apiDelete(path: string, errorMessage: string): Promise<void> {
  await request(path, { method: "DELETE", errorMessage });
}
