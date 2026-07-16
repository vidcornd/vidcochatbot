import { useEffect, useState } from "react";
import { fetchWidgetSession, type WidgetSessionData } from "./api/widgetApi";
import { EmbedChat } from "./components/EmbedChat";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

type LoadState =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ready"; sessionData: WidgetSessionData };

function getSessionTokenFromUrl(): string | null {
  return new URLSearchParams(window.location.search).get("session");
}

function EmbedApp() {
  const [state, setState] = useState<LoadState>({ status: "loading" });

  useEffect(() => {
    document.documentElement.classList.add("is-embed");
    document.body.classList.add("is-embed");

    const sessionToken = getSessionTokenFromUrl();

    if (!sessionToken) {
      setState({ status: "error", message: "Oturum bilgisi eksik." });
      return;
    }

    fetchWidgetSession(API_URL, sessionToken)
      .then((sessionData) => setState({ status: "ready", sessionData }))
      .catch((error: unknown) => {
        const message = error instanceof Error ? error.message : "Oturum bulunamadı veya süresi dolmuş.";
        setState({ status: "error", message });
      });
  }, []);

  return (
    <div className="embedRoot">
      {state.status === "loading" && <div className="embedStatus">Yükleniyor...</div>}

      {state.status === "error" && (
        <div className="embedStatus">
          {state.message} Sayfayı yenilemeyi deneyin.
        </div>
      )}

      {state.status === "ready" && <EmbedChat sessionData={state.sessionData} />}
    </div>
  );
}

export default EmbedApp;