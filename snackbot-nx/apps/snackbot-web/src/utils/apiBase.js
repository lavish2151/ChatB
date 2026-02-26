/**
 * Returns the base URL for API requests.
 * When the app is served from the same origin as the API (e.g. Flask at localhost:5000),
 * use relative URL ('') so fetch('/api/...') works. When on a different origin (e.g. Vite
 * dev server at 5173), use VITE_SNACKBOT_API_URL so requests go to the backend.
 */
export function getApiBase() {
  const env = import.meta.env.VITE_SNACKBOT_API_URL || '';
  if (typeof window === 'undefined') return env;
  if (!env) return '';
  try {
    if (window.location.origin === new URL(env).origin) return '';
  } catch (_) {}
  return env;
}
