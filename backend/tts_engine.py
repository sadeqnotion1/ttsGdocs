"""Pluggable text-to-speech engines.

Two REAL engines are supported and tried in priority order:
  - pyttsx3 : fully offline, cross-platform (no network needed) -> .wav
  - gTTS    : online, Google Translate TTS (needs internet)     -> .mp3

Each engine import is guarded, so a missing dependency NEVER crashes the
server at startup -- the engine simply becomes unavailable and we fall back
to the next one. If none are installed, ``synthesize`` raises a clear,
actionable error that the HTTP layer turns into a friendly message.
"""
from __future__ import annotations

import time
from pathlib import Path

from config import OUTPUT_DIR, ENGINE_PRIORITY, DEFAULT_RATE, DEFAULT_LANG


class TTSUnavailableError(RuntimeError):
    """Raised when no TTS engine is installed/usable."""


def _ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _timestamp_name(ext: str) -> Path:
    _ensure_output_dir()
    stamp = time.strftime("%Y%m%d-%H%M%S")
    return OUTPUT_DIR / f"tts-{stamp}.{ext}"


# --- engine: pyttsx3 (offline) ----------------------------------------------
def _synthesize_pyttsx3(text: str, rate: int) -> Path:
    import pyttsx3  # type: ignore

    out = _timestamp_name("wav")
    engine = pyttsx3.init()
    engine.setProperty("rate", rate)
    engine.save_to_file(text, str(out))
    engine.runAndWait()
    return out


# --- engine: gTTS (online) --------------------------------------------------
def _synthesize_gtts(text: str, lang: str) -> Path:
    from gtts import gTTS  # type: ignore

    out = _timestamp_name("mp3")
    gTTS(text=text, lang=lang).save(str(out))
    return out


def available_engines() -> list:
    """Return the engines that can actually be imported right now."""
    found = []
    for name in ENGINE_PRIORITY:
        try:
            if name == "pyttsx3":
                import pyttsx3  # noqa: F401
            elif name == "gtts":
                from gtts import gTTS  # noqa: F401
            else:
                continue
            found.append(name)
        except Exception:
            continue
    return found


def synthesize(text, *, rate=DEFAULT_RATE, lang=DEFAULT_LANG, engine=None):
    """Generate speech audio from ``text``.

    Returns ``(path_to_audio_file, engine_used)``.
    Raises ``TTSUnavailableError`` if no engine works.
    """
    text = (text or "").strip()
    if not text:
        raise ValueError("No text provided to synthesize.")

    order = [engine] if engine else list(ENGINE_PRIORITY)
    last_err = None
    for name in order:
        try:
            if name == "pyttsx3":
                return _synthesize_pyttsx3(text, int(rate)), name
            if name == "gtts":
                return _synthesize_gtts(text, str(lang)), name
        except Exception as exc:  # try the next engine
            last_err = exc
            continue

    hint = (
        "No working TTS engine found. Install one:\n"
        "  pip install pyttsx3   (offline)\n"
        "  pip install gTTS      (online)"
    )
    if last_err:
        hint += f"\nLast error: {last_err!r}"
    raise TTSUnavailableError(hint)
