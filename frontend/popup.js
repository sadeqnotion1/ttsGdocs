// Popup logic. The popup is an extension page, so (with host_permissions) it
// can read the Google Doc's plain-text export AND call the local backend.

const $ = (sel) => document.querySelector(sel);
const BACKEND = "http://127.0.0.1:5000";

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
  try {
    const res = await fetch(url, { credentials: "include" });
    if (res.ok) {
      const text = await res.text();
      if (text && text.trim()) return text;
    }
  } catch (e) {
    /* fall through to the selection fallback */
  }
  if (fallbackSelection && fallbackSelection.trim()) return fallbackSelection;
  throw new Error("Could not read the document text (try selecting text first).");
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
    const objUrl = URL.createObjectURL(blob);

    const audio = $("#player");
    audio.src = objUrl;
    audio.hidden = false;
    audio.play().catch(() => {});

    const ext = (blob.type || "").includes("mpeg") ? "mp3" : "wav";
    const safe = (info.title || "google-doc")
      .replace(/[^\w.-]+/g, "_")
      .slice(0, 60);
    const dl = $("#download");
    dl.href = objUrl;
    dl.download = safe + "." + ext;
    dl.hidden = false;

    setStatus("Done. Press play or download below.", "ok");
  } catch (err) {
    setStatus(err.message || String(err), "error");
  } finally {
    $("#go").disabled = false;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  $("#rate").addEventListener("input", () => {
    $("#rateVal").textContent = $("#rate").value;
  });
  $("#go").addEventListener("click", run);

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
