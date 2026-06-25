// Background service worker.
//
// Orchestrates recording the *tab's* audio - i.e. Google Docs' own built-in
// read-aloud voices - using chrome.tabCapture + an offscreen document, then
// hands the captured audio to a Save As download.
//
// Why an offscreen document? Service workers have no DOM and can't run
// MediaRecorder, and the popup closes the moment the user clicks into the
// page to press Play. The offscreen document keeps recording alive.

const OFFSCREEN_PATH = "offscreen.html";

let recording = false;
let startedAt = 0;
let pendingName = "google-doc-audio";
let pendingStreamId = null;
let offscreenReady = false;

async function hasOffscreen() {
  if (!chrome.offscreen || !chrome.offscreen.hasDocument) return false;
  try {
    return await chrome.offscreen.hasDocument();
  } catch (e) {
    return false;
  }
}

async function ensureOffscreen() {
  if (await hasOffscreen()) return;
  await chrome.offscreen.createDocument({
    url: OFFSCREEN_PATH,
    reasons: ["USER_MEDIA"],
    justification: "Record the tab's read-aloud audio so it can be saved.",
  });
}

async function closeOffscreen() {
  offscreenReady = false;
  if (await hasOffscreen()) {
    try {
      await chrome.offscreen.closeDocument();
    } catch (e) {
      /* ignore */
    }
  }
}

function toSafeName(raw) {
  const base =
    (raw || "google-doc-audio")
      .replace(/[^\w.-]+/g, "_")
      .replace(/^_+|_+$/g, "") || "google-doc-audio";
  return base.toLowerCase().endsWith(".webm") ? base : base + ".webm";
}

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (!msg || !msg.type) return;

  if (msg.type === "OFFSCREEN_READY") {
    offscreenReady = true;
    if (pendingStreamId) {
      chrome.runtime.sendMessage({
        target: "offscreen",
        type: "OFFSCREEN_START",
        streamId: pendingStreamId,
      });
      pendingStreamId = null;
    }
    return;
  }

  if (msg.type === "START_CAPTURE") {
    pendingName = msg.title || "google-doc-audio";
    pendingStreamId = msg.streamId;
    recording = true;
    startedAt = Date.now();
    sendResponse({ ok: true });
    // Always start from a clean offscreen document so we get a fresh READY.
    (async () => {
      await closeOffscreen();
      await ensureOffscreen();
    })().catch((e) => {
      recording = false;
      pendingStreamId = null;
      chrome.runtime.sendMessage({ type: "CAPTURE_ERROR", error: String(e) });
    });
    return true; // async sendResponse
  }

  if (msg.type === "STOP_CAPTURE") {
    if (msg.filename) pendingName = msg.filename;
    chrome.runtime.sendMessage({ target: "offscreen", type: "OFFSCREEN_STOP" });
    sendResponse({ ok: true });
    return;
  }

  if (msg.type === "GET_STATE") {
    sendResponse({
      recording: recording,
      elapsedMs: recording ? Date.now() - startedAt : 0,
    });
    return;
  }

  if (msg.type === "RECORDING_DONE") {
    recording = false;
    if (msg.dataUrl) {
      const name = toSafeName(pendingName);
      chrome.downloads.download(
        {
          url: msg.dataUrl,
          filename: name,
          saveAs: true,
          conflictAction: "uniquify",
        },
        () => {
          if (chrome.runtime.lastError) {
            chrome.runtime.sendMessage({
              type: "CAPTURE_ERROR",
              error: chrome.runtime.lastError.message,
            });
          } else {
            chrome.runtime.sendMessage({ type: "CAPTURE_SAVED", name: name });
          }
          closeOffscreen();
        }
      );
    } else {
      chrome.runtime.sendMessage({
        type: "CAPTURE_ERROR",
        error: msg.error || "no audio captured",
      });
      closeOffscreen();
    }
    return;
  }
});
