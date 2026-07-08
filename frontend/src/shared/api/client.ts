export interface ApiError {
  message: string;
  status?: number;
}

export async function apiRequest<T>(
  baseUrl: string,
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${baseUrl}${path}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      'Accept': 'application/json',
      ...(options.headers ?? {}),
    },
  });

  if (!response.ok) {
    let message = `HTTP ${response.status}: ${response.statusText}`;
    try {
      const data = await response.json();
      if (typeof data.detail === 'string') {
        message = data.detail;
      } else if (typeof data.message === 'string') {
        message = data.message;
      }
    } catch {
      // ignore parse error
    }
    throw { message, status: response.status } as ApiError;
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}
