import { sendLocation, sendFallback } from "./api.js";

const GEO_DENIED = "geo_denied";

function setGeoDenied(val) {
  console.log("[Location] GEO_DENIED set:", val);

  if (val) localStorage.setItem(GEO_DENIED, "true");
  else localStorage.removeItem(GEO_DENIED);
}

function isGeoDenied() {
  const denied = localStorage.getItem(GEO_DENIED) === "true";
  console.log("[Location] isGeoDenied:", denied);
  return denied;
}

export function fetchGPS(source = "GPS") {
  console.log(`[Location] Fetching GPS (${source})`);

  return new Promise((resolve) => {

    if (!navigator.geolocation) {
      console.log("[Location] Geolocation not supported");
      sendFallback();
      return resolve();
    }

    if (isGeoDenied()) {
      console.log("[Location] Skipping GPS (denied)");
      sendFallback();
      return resolve();
    }

    navigator.geolocation.getCurrentPosition(

      (pos) => {
        console.log("[Location] GPS success:", pos.coords);

        setGeoDenied(false);

        sendLocation(
          pos.coords.latitude,
          pos.coords.longitude,
          source
        );

        resolve();
      },

      (err) => {
        console.log("[Location] GPS error:", err);

        if (err.code === err.PERMISSION_DENIED) {
          console.log("[Location] User denied permission");
          setGeoDenied(true);
        }

        sendFallback();
        resolve();
      },

      {
        timeout: 2500,
        maximumAge: 300000,
        enableHighAccuracy: false
      }
    );
  });
}