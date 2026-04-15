import streamlit.components.v1 as components

NOTIF_JS = """
<script>
(function() {
  const synth = window.speechSynthesis;
  let voices = [];

  function loadVoices() {
    voices = synth.getVoices().filter(v => v.lang.startsWith('en'));
  }
  loadVoices();
  if (synth.onvoiceschanged !== undefined) synth.onvoiceschanged = loadVoices;

  function speak(text, volume) {
    synth.cancel();
    const utt = new SpeechSynthesisUtterance(text);
    utt.volume  = volume || 0.9;
    utt.rate    = 0.95;
    utt.pitch   = 1;
    if (voices.length > 0) utt.voice = voices[0];
    synth.speak(utt);
  }

  function browserNotify(title, body) {
    if (!('Notification' in window)) return;
    if (Notification.permission === 'granted') {
      new Notification(title, { body });
    } else if (Notification.permission !== 'denied') {
      Notification.requestPermission().then(p => {
        if (p === 'granted') new Notification(title, { body });
      });
    }
  }

  // Expose globally so Streamlit can call after re-render
  window._hazardAlert = function(result, volume) {
    if (result === 1) {
      speak(
        "Warning! Hazard detected. Both a dustbin and a spill are present. Immediate attention is required.",
        volume
      );
      browserNotify(
        "HazardEye — Hazard Detected",
        "Both a dustbin and a spill were found. Immediate action needed."
      );
    } else {
      speak(
        "All clear. No hazard detected. The area appears safe.",
        volume
      );
      browserNotify(
        "HazardEye — All Clear",
        "No concurrent dustbin + spill detected. Area is safe."
      );
    }
  };

  // Auto-trigger if data attributes are set on this script's host div
  const host = document.currentScript ? document.currentScript.parentElement : null;
  if (host && host.dataset.result !== undefined) {
    window._hazardAlert(parseInt(host.dataset.result), parseFloat(host.dataset.volume || 0.9));
  }
})();
</script>
"""


def trigger_alert(result: int, volume: float = 0.9):
    """
    Call this right after predict() returns.
    result  — 0 (clear) or 1 (hazard)
    volume  — 0.0 to 1.0
    """
    html = f"""
    <div data-result="{result}" data-volume="{volume}">
      {NOTIF_JS}
    </div>
    """
    components.html(html, height=0)