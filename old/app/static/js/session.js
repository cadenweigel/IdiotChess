// session.js
export async function ensureSession() {
    let sessionId = localStorage.getItem("session_id");
  
    if (!sessionId) {
      const response = await fetch("/api/new-game/bot", { method: "POST" });
      const data = await response.json();
      sessionId = data.session_id;
      localStorage.setItem("session_id", sessionId);
    }
  
    return sessionId;
  }
  