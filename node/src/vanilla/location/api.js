import { saveCache, getCache } from "./cache.js";

const LAST_SENT = "location_last_sent";
const now = () => Date.now();

export function postLocation(payload) {
  console.log("[Location] Sending to API:", payload);

  return fetch("/api/location", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: payload ? JSON.stringify(payload) : undefined
  }).catch(() => {
    console.log("[Location] API request failed");
  });
}

export function sendLocation(lat, lon, source = "GPS") {
  console.log(`[Location] sendLocation (${source})`, lat, lon);

  localStorage.setItem(LAST_SENT, now());
  saveCache(lat, lon, source);
  postLocation({ lat, lon });
}

export function sendFallback() {
  console.log("[Location] Using fallback");

  localStorage.setItem(LAST_SENT, now());

  const cached = getCache();
  if (cached) {
    console.log("[Location] Fallback using cached location");
    postLocation({ lat: cached.lat, lon: cached.lon });
  } else {
    console.log("[Location] Fallback without cache (IP-based)");
    postLocation();
  }
}