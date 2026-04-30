// =========================
// ⚙️ CONFIG
// =========================
const ENDPOINT = "/track-event";    // mesti buat endpoint
const BATCH_INTERVAL = 5000; // kirim tiap x ms detik
const MAX_BATCH_SIZE = 10;

// =========================
// 🧠 STATE
// =========================
let queue = [];
let initialized = false;
let timer = null;

// =========================
// 📦 SEND BATCH
// =========================
async function sendBatch() {
  if (queue.length === 0) {
    console.log("[Tracking] No events to send");
    return;
  }

  const payload = [...queue];
  queue = []; // reset dulu biar tidak duplicate

  console.log("[Tracking] Sending batch:", payload);

  try {
    await fetch(ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    console.log("[Tracking] Batch sent successfully");
  } catch (err) {
    console.log("[Tracking] Batch failed, retrying later", err);

    // ❌ gagal → balikin ke queue (retry nanti)
    queue.unshift(...payload);

    console.log("[Tracking] Queue restored:", queue);
  }
}

// =========================
// ⏱️ START BATCH LOOP
// =========================
function startBatching() {
  if (timer) {
    console.log("[Tracking] Batching already running");
    return;
  }

  console.log("[Tracking] Starting batch loop");

  timer = setInterval(() => {
    console.log("[Tracking] Interval trigger → sendBatch");
    sendBatch();
  }, BATCH_INTERVAL);
}

// =========================
// 📥 ADD EVENT
// =========================
function trackEvent(action) {
  const event = {
    action,
    page: window.location.pathname,
    time: new Date().toISOString()
  };

  queue.push(event);

  console.log("[Tracking] Event added:", event);
  console.log("[Tracking] Current queue size:", queue.length);

  // 🚀 kirim langsung kalau sudah penuh
  if (queue.length >= MAX_BATCH_SIZE) {
    console.log("[Tracking] Max batch size reached → sending immediately");
    sendBatch();
  }
}

// =========================
// 🛑 HANDLE PAGE EXIT
// =========================
function flushOnExit() {
  window.addEventListener("beforeunload", () => {
    if (queue.length === 0) {
      console.log("[Tracking] No events to flush on exit");
      return;
    }

    console.log("[Tracking] Flushing events on exit:", queue);

    navigator.sendBeacon(
      ENDPOINT,
      JSON.stringify(queue)
    );
  });
}

// =========================
// 🖱️ CLICK LISTENER
// =========================
function setupClickTracking() {

  console.log("[Tracking] Setting up click tracking");

  let lastClickTime = 0;

  document.addEventListener("click", (e) => {
    // implement in class html -> class=track-btn
    const btn = e.target.closest(".track-btn");
    if (!btn) return;

    const now = Date.now();

    // ⛔ debounce 300ms (hindari spam klik cepat)
    if (now - lastClickTime < 300) {
      console.log("[Tracking] Click ignored (debounce)");
      return;
    }

    lastClickTime = now;

    // implement in logging action -> data-action=sample string
    const action = btn.dataset.action;

    if (!action) {
      console.log("[Tracking] Click without data-action ignored");
      return;
    }

    console.log("[Tracking] Click detected:", action);

    trackEvent(action);
  });
}

// =========================
// 🌐 ONLINE RECOVERY
// =========================
function setupOnlineRetry() {
  console.log("[Tracking] Setting up online retry");

  window.addEventListener("online", () => {
    console.log("[Tracking] Back online → retry sending batch");
    sendBatch();
  });
}

// =========================
// 🎯 INIT
// =========================
export function initTracking() {
  if (initialized) {
    console.log("[Tracking] Already initialized");
    return;
  }

  console.log("===== [Tracking] INIT START =====");

  initialized = true;

  setupClickTracking();
  setupOnlineRetry();
  flushOnExit();
  startBatching();
}