import { getCache, isCacheValid } from "./cache.js";
import { sendLocation, sendFallback } from "./api.js";
import { fetchGPS } from "./gps.js";

// =========================
// CONFIG
// =========================
const ASK_KEY = "location_permission_asked";
const LAST_SENT = "location_last_sent";
const GEO_DENIED = "geo_denied";
const REFRESH_INTERVAL = 10 * 60 * 1000;

// =========================
// HELPERS
// =========================
const now = () => Date.now();

function getShouldForceRefresh() {
  const val = window.__LOCATION_EXPIRED__ === true;
  console.log("[Location] SHOULD_FORCE_REFRESH:", val);
  return val;
}

// =========================
// PERMISSION
// =========================
function setGeoDenied(val) {
  console.log("[Location] GEO_DENIED set:", val);

  if (val) localStorage.setItem(GEO_DENIED, "true");
  else localStorage.removeItem(GEO_DENIED);
}

function checkPermission() {
  console.log("[Location] Checking permission...");

  if (!navigator.permissions) {
    console.log("[Location] Permissions API not supported");
    return Promise.resolve("unknown");
  }

  return navigator.permissions.query({ name: "geolocation" })
    .then(result => {
      console.log("[Location] Permission state:", result.state);

      setGeoDenied(result.state === "denied");

      result.onchange = () => {
        console.log("[Location] Permission changed:", result.state);
        setGeoDenied(result.state === "denied");
      };

      return result.state;
    })
    .catch(() => {
      console.log("[Location] Permission check failed");
      return "unknown";
    });
}

// =========================
// LOGIC
// =========================
function shouldRefresh() {
  const last = localStorage.getItem(LAST_SENT);
  if (!last) {
    console.log("[Location] No last sent → should refresh");
    return true;
  }

  const refresh = (now() - parseInt(last)) > REFRESH_INTERVAL;
  console.log("[Location] shouldRefresh:", refresh);
  return refresh;
}

function useCacheIfValid() {
  const cached = getCache();

  if (isCacheValid(cached)) {
    console.log("[Location] Using cached location");
    sendLocation(cached.lat, cached.lon, "CACHE");
    return true;
  }

  console.log("[Location] No valid cache");
  return false;
}

// =========================
// BACKGROUND
// =========================
function runInBackground(fn) {
  console.log("[Location] Running in background");

  if ("requestIdleCallback" in window) {
    requestIdleCallback(fn, { timeout: 2000 });
  } else {
    setTimeout(fn, 0);
  }
}

// =========================
// MAIN FLOW
// =========================
async function mainFlow() {
  console.log("===== [Location] MAIN FLOW START =====");

  // 0. FORCE REFRESH
  if (getShouldForceRefresh()) {
    console.log("[Location] Force refresh triggered");

    if (!useCacheIfValid()) {
      await fetchGPS("GPS_FORCE");
    }
    return;
  }

  // 1. CACHE FIRST
  if (useCacheIfValid()) return;

  // 2. FIRST ASK
  if (!localStorage.getItem(ASK_KEY)) {
    console.log("[Location] First time asking permission");

    localStorage.setItem(ASK_KEY, "true");

    const state = await checkPermission();

    if (state === "denied") {
      sendFallback();
    } else {
      await fetchGPS("GPS_FIRST");
    }

    return;
  }

  // 3. REFRESH
  if (shouldRefresh()) {
    console.log("[Location] Refreshing GPS");
    await fetchGPS("GPS_REFRESH");
  } else {
    console.log("[Location] Using fallback (no refresh needed)");
    sendFallback();
  }
}

// =========================
// PUBLIC INIT
// =========================
export function initLocation() {
  console.log("[Location] initLocation called");
  runInBackground(mainFlow);
}