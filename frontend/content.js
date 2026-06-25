// Runs inside the Google Docs page. Reports the document id, url, title and
// any selected text back to the popup when asked. Kept tiny on purpose --
// the heavy lifting (reading + synthesizing) happens in the popup.

function getDocId(url) {
  const m = url.match(/\/document\/d\/([a-zA-Z0-9_-]+)/);
  return m ? m[1] : null;
}

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg && msg.type === "GET_DOC_INFO") {
    const selection =
      (window.getSelection && String(window.getSelection())) || "";
    sendResponse({
      docId: getDocId(location.href),
      url: location.href,
      selection: selection,
      title: document.title.replace(/ - Google Docs$/, ""),
    });
  }
  // Synchronous response above; no need to keep the channel open.
  return false;
});
