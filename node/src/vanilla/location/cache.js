const CACHE_KEY = "location_cache";
const REFRESH_INTERVAL = 10 * 60 * 1000;

const now = () => Date.now();

export function saveCache(lat, lon, source) {
  console.log("[Location] Saving cache:", { lat, lon, source });

  localStorage.setItem(CACHE_KEY, JSON.stringify({
    lat, lon, source, ts: now()
  }));
}

export function getCache() {
  try {
    const data = JSON.parse(localStorage.getItem(CACHE_KEY));
    console.log("[Location] Loaded cache:", data);
    return data;
  } catch {
    console.log("[Location] Cache parse error");
    return null;
  }
}

export function isCacheValid(data) {
  const valid = data && (now() - data.ts) < REFRESH_INTERVAL;
  console.log("[Location] Cache valid:", valid);
  return valid;
}