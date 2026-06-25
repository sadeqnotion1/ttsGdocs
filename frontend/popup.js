// Popup logic. The popup is an extension page, so (with host_permissions) it
// can read the Google Doc's plain-text export AND call the local backend.

const $ = (sel) => document.querySelector(sel);
const BACKEND = "http://127.0.0.1:5000";

// Audio captured from the backend, kept for the Save step.
let lastObjUrl = null; // object URL for the <audio> element
let lastDataUrl = null; // self-contained data URL for chrome.downloads (survives popup close)
let lastExt = "wav";

function blobToDataUrl(blob) {
  return new Promise((resolve, reject) => {
    const r = new FileReader();
    r.onload = () => resolve(r.result);
    r.onerror = () => reject(r.error);
    r.readAsDataURL(blob);
  });
}

// Controlled download: opens a "Save As" dialog so the user picks the folder
// and confirms the (editable) file name. Uses a data URL so it still works
// even if the popup loses focus and closes.
function saveAudio() {
  if (!lastDataUrl) return;
  const raw = ($("#filename").value || "google-doc").trim();
  const base =
    raw.replace(/[^\w.-]+/g, "_").replace(/^_+|_+$/g, "") || "google-doc";
  const name = base.toLowerCase().endsWith("." + lastExt)
    ? base
    : base + "." + lastExt;

  setStatus("Saving " + name + "...");
  chrome.downloads.download(
    { url: lastDataUrl, filename: name, saveAs: true, conflictAction: "uniquify" },
    (downloadId) => {
      if (chrome.runtime.lastError || downloadId === undefined) {
        setStatus(
          (chrome.runtime.lastError && chrome.runtime.lastError.message) ||
            "Download was cancelled.",
          "error"
        );
      }
    }
  );
}

// Report when the save actually finishes (or fails).
if (chrome.downloads && chrome.downloads.onChanged) {
  chrome.downloads.onChanged.addListener((delta) => {
    if (delta.state && delta.state.current === "complete") {
      setStatus("Saved. Check your chosen folder.", "ok");
    } else if (delta.error && delta.error.current) {
      setStatus("Save failed: " + delta.error.current, "error");
    }
  });
}

function setStatus(msg, kind = "info") {
  const el = $("#status");
  el.textContent = msg;
  el.dataset.kind = kind;
}

async function getActiveTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab;
}

function getDocInfo(tabId) {
  return new Promise((resolve) => {
    chrome.tabs.sendMessage(tabId, { type: "GET_DOC_INFO" }, (resp) => {
      if (chrome.runtime.lastError) resolve(null);
      else resolve(resp);
    });
  });
}

// Most reliable way to read a Google Doc's text: its plain-text export.
// Uses the user's existing session cookies (credentials: include).
async function fetchDocText(docId, fallbackSelection) {
  const url =
    "https://docs.google.com/document/d/" + docId + "/export?format=txt";
  let reason = "";
  try {
    const res = await fetch(url, { credentials: "include" });
    if (res.ok) {
      const text = await res.text();
      const trimmed = (text || "").trim();
      // When the session can't access the doc, Google returns an HTML sign-in /
      // error page (status 200) instead of plain text. Detect it so we don't
      // "speak" HTML and so we can explain what's wrong.
      const looksHtml = /^\s*<(?:!doctype|html)/i.test(text);
      if (trimmed && !looksHtml) return text;
      reason = looksHtml
        ? "sign in to this Google account in this browser (or the doc isn't shared with you)"
        : "the document looks empty - is there any text in it?";
    } else if (res.status === 401 || res.status === 403) {
      reason = "access denied - sign in to Google or check the doc is shared with you";
    } else {
      reason = "the export request failed (HTTP " + res.status + ")";
    }
  } catch (e) {
    reason = "couldn't reach the text export (network or permission issue)";
  }
  // Fall back to whatever the user has selected on the page.
  if (fallbackSelection && fallbackSelection.trim()) return fallbackSelection;
  throw new Error(
    "Couldn't read the document text" +
      (reason ? " - " + reason : "") +
      ". Tip: select some text in the doc and try again."
  );
}

async function synthesize(text) {
  const engine = $("#engine").value; // auto | pyttsx3 | gtts
  const body = {
    text: text,
    rate: Number($("#rate").value),
    lang: $("#lang").value.trim() || "en",
  };
  if (engine !== "auto") body.engine = engine;

  const res = await fetch(BACKEND + "/tts", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    let detail = "HTTP " + res.status;
    try {
      detail = (await res.json()).error || detail;
    } catch (e) {}
    throw new Error(detail);
  }
  return res.blob();
}

async function run() {
  $("#go").disabled = true;
  try {
    setStatus("Reading the document...");
    const tab = await getActiveTab();
    const isDoc =
      tab && /^https:\/\/docs\.google\.com\/document\//.test(tab.url || "");
    if (!isDoc) {
      setStatus("Open a Google Doc tab first.", "error");
      return;
    }
    const info = await getDocInfo(tab.id);
    if (!info || !info.docId) {
      setStatus("Couldn't detect the document id on this tab.", "error");
      return;
    }

    const text = await fetchDocText(info.docId, info.selection);
    setStatus("Generating speech (" + text.length.toLocaleString() + " chars)...");

    const blob = await synthesize(text);
    if (lastObjUrl) URL.revokeObjectURL(lastObjUrl);
    const objUrl = URL.createObjectURL(blob);
    lastObjUrl = objUrl;

    const audio = $("#player");
    audio.src = objUrl;
    audio.hidden = false;
    audio.play().catch(() => {});

    // Keep the audio (as a self-contained data URL) + a default name for Save.
    lastExt = (blob.type || "").includes("mpeg") ? "mp3" : "wav";
    lastDataUrl = await blobToDataUrl(blob);
    const safe =
      (info.title || "google-doc")
        .replace(/[^\w.-]+/g, "_")
        .replace(/^_+|_+$/g, "")
        .slice(0, 60) || "google-doc";
    $("#filename").value = safe;
    $("#saveRow").hidden = false;

    setStatus("Done. Press play, or name the file and Save below.", "ok");
  } catch (err) {
    setStatus(err.message || String(err), "error");
  } finally {
    $("#go").disabled = false;
  }
}

// --- Recording Google's built-in read-aloud (tab audio capture) ------------

function recStatus(msg, kind = "info") {
  const el = $("#recStatus");
  el.hidden = false;
  el.textContent = msg;
  el.dataset.kind = kind;
}

function setRecUi(active) {
  $("#recStart").disabled = active;
  $("#recStop").disabled = !active;
}

async function startRecording() {
  const tab = await getActiveTab();
  if (!tab) {
    recStatus("No active tab to record.", "error");
    return;
  }
  // Pre-fill a sensible name from the doc title when possible.
  try {
    const info = await getDocInfo(tab.id);
    if (info && info.title && !$("#recName").value) $("#recName").value = info.title;
  } catch (e) {
    /* not a docs tab / no content script - fine */
  }
  chrome.tabCapture.getMediaStreamId({ targetTabId: tab.id }, (streamId) => {
    if (chrome.runtime.lastError || !streamId) {
      recStatus(
        (chrome.runtime.lastError && chrome.runtime.lastError.message) ||
          "Couldn't start tab capture.",
        "error"
      );
      return;
    }
    chrome.runtime.sendMessage(
      {
        type: "START_CAPTURE",
        streamId: streamId,
        title: $("#recName").value || "google-doc-audio",
      },
      (resp) => {
        if (chrome.runtime.lastError || !resp || !resp.ok) {
          recStatus(
            "Couldn't start recording: " +
              ((resp && resp.error) ||
                (chrome.runtime.lastError && chrome.runtime.lastError.message) ||
                "unknown"),
            "error"
          );
          return;
        }
        setRecUi(true);
        recStatus(
          "Recording... press Play in Google's read-aloud, then Stop when it finishes.",
          "ok"
        );
      }
    );
  });
}

function stopRecording() {
  setRecUi(false);
  recStatus("Saving recording...");
  chrome.runtime.sendMessage({
    type: "STOP_CAPTURE",
    filename: $("#recName").value || "google-doc-audio",
  });
}

function refreshRecState() {
  chrome.runtime.sendMessage({ type: "GET_STATE" }, (resp) => {
    if (chrome.runtime.lastError) return;
    if (resp && resp.recording) {
      setRecUi(true);
      recStatus("Recording in progress... click Stop & save when done.", "ok");
    } else {
      setRecUi(false);
    }
  });
}

chrome.runtime.onMessage.addListener((msg) => {
  if (!msg || !msg.type) return;
  if (msg.type === "CAPTURE_SAVED") {
    setRecUi(false);
    recStatus("Saved " + (msg.name || "recording") + " - pick where in the dialog.", "ok");
  } else if (msg.type === "CAPTURE_ERROR") {
    setRecUi(false);
    recStatus("Recording failed: " + (msg.error || "unknown"), "error");
  }
});

document.addEventListener("DOMContentLoaded", () => {
  $("#rate").addEventListener("input", () => {
    $("#rateVal").textContent = $("#rate").value;
  });
  $("#go").addEventListener("click", run);
  $("#download").addEventListener("click", saveAudio);
  $("#recStart").addEventListener("click", startRecording);
  $("#recStop").addEventListener("click", stopRecording);
  refreshRecState();

  // Quick backend health hint on open.
  fetch(BACKEND + "/health")
    .then((r) => r.json())
    .then((d) => {
      if (d && d.engines && d.engines.length) {
        setStatus("Backend ready - engines: " + d.engines.join(", "), "ok");
      } else {
        setStatus("Backend up, but no TTS engine installed. See README.", "error");
      }
    })
    .catch(() => setStatus("Start the Python backend (run.sh / run.bat).", "error"));
});
