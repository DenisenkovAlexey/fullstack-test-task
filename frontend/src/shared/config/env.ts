export function getApiUrl(): string {
  return process.env.API_URL ?? 'http://localhost:8000';
}
