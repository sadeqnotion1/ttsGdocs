// Offscreen document: performs the actual tab-audio capture.
//
// Receives a tabCapture stream id from the service worker, opens it with
// getUserMedia, records it with MediaRecorder, and sends the finished audio
// back as a data URL. Also pipes the audio to the speakers so the user still
// hears the doc being read while it records.

let recorder = null;
let chunks = [];
let audioCtx = null;
let stream = null;

chrome.runtime.onMessage.addListener((msg) => {
  if (!msg || msg.target !== "offscreen") return;
  if (msg.type === "OFFSCREEN_START") startCapture(msg.streamId);
  else if (msg.type === "OFFSCREEN_STOP") stopCapture();
});

function blobToDataUrl(blob) {
  return new Promise((resolve, reject) => {
    const r = new FileReader();
    r.onload = () => resolve(r.result);
    r.onerror = () => reject(r.error);
    r.readAsDataURL(blob);
  });
}

function cleanup() {
  try {
    if (stream) stream.getTracks().forEach((t) => t.stop());
  } catch (e) {
    /* ignore */
  }
  try {
    if (audioCtx) audioCtx.close();
  } catch (e) {
    /* ignore */
  }
  recorder = null;
  stream = null;
  audioCtx = null;
  chunks = [];
}

async function startCapture(streamId) {
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        mandatory: {
          chromeMediaSource: "tab",
          chromeMediaSourceId: streamId,
        },
      },
    });
  } catch (e) {
    chrome.runtime.sendMessage({
      type: "RECORDING_DONE",
      error: "capture failed: " + (e && e.message ? e.message : e),
    });
    return;
  }

  // Keep the audio audible while recording (tab capture would otherwise mute it).
  try {
    audioCtx = new AudioContext();
    const src = audioCtx.createMediaStreamSource(stream);
    src.connect(audioCtx.destination);
  } catch (e) {
    /* non-fatal: recording still works even if playback passthrough fails */
  }

  chunks = [];
  const mime = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
    ? "audio/webm;codecs=opus"
    : "audio/webm";
  recorder = new MediaRecorder(stream, { mimeType: mime });
  recorder.ondataavailable = (e) => {
    if (e.data && e.data.size) chunks.push(e.data);
  };
  recorder.onstop = async () => {
    const blob = new Blob(chunks, { type: "audio/webm" });
    try {
      const dataUrl = await blobToDataUrl(blob);
      chrome.runtime.sendMessage({ type: "RECORDING_DONE", dataUrl: dataUrl });
    } catch (e) {
      chrome.runtime.sendMessage({
        type: "RECORDING_DONE",
        error: "could not encode recording",
      });
    }
    cleanup();
  };
  recorder.start();
}

function stopCapture() {
  if (recorder && recorder.state !== "inactive") {
    recorder.stop();
  } else {
    chrome.runtime.sendMessage({ type: "RECORDING_DONE", error: "not recording" });
  }
}

// Tell the service worker we're ready to receive the stream id.
chrome.runtime.sendMessage({ type: "OFFSCREEN_READY" });
