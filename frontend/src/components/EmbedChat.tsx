import { useCallback, useEffect, useState } from "react";
import { ChatConversation } from "./ChatConversation";
import type { WidgetSessionData } from "../api/widgetApi";
import { KvkkConsentGate } from "./KvkkConsentGate";

type EmbedChatProps = {sessionData: WidgetSessionData; sessionToken: string;};

type ParentMessage = {
  source?: string;
  type?: string;
  payload?: unknown;
};

const OPEN_SIZE = { width: 520, height: 760 };
const CLOSED_SIZE = { width: 80, height: 80 };
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
const API_KEY = import.meta.env.VITE_WIDGET_API_KEY || "";

function getConsentStorageKey(botId: string): string {
  return `vidco-chat-consent:${botId}`;
}

export function EmbedChat({sessionData,sessionToken} : EmbedChatProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [hasConsented, setHasConsented] = useState( () => window.localStorage.getItem(getConsentStorageKey(sessionData.botId)) === "1");
  const sendToParent = useCallback(
    (type: string, payload?: unknown) => {
      if (!sessionData.origin || window.parent === window) return;

      window.parent.postMessage(
        { source: "vidco-chat-iframe", type, payload: payload || {} },
        sessionData.origin
      );
    },
    [sessionData.origin]
  );

  const open = useCallback(() => {
    setIsOpen(true);
    sendToParent("RESIZE", OPEN_SIZE);
  }, [sendToParent]);

  const close = useCallback(() => {
    setIsOpen(false);
    sendToParent("RESIZE", CLOSED_SIZE);
  }, [sendToParent]);

  useEffect(() => {
    sendToParent("READY");

    function handleParentMessage(event: MessageEvent) {
      if (event.origin !== sessionData.origin) return;
      if (event.source !== window.parent) return;

      const data = event.data as ParentMessage;
      if (!data || data.source !== "vidco-chat-parent") return;

      switch (data.type) {
        case "OPEN":
          open();
          break;

        case "CLOSE":
          close();
          break;

        case "UPDATE_USER":
        case "UPDATE_CONTEXT":
          break;

        default:
          break;
      }
    }

    window.addEventListener("message", handleParentMessage);
    return () => window.removeEventListener("message", handleParentMessage);
  }, [sessionData.origin, sendToParent, open, close]);

  if (!isOpen) {
    return (
      <button
        className="chatBubble"
        onClick={open}
        aria-label="Vidco yardım asistanını aç"
        type="button"
      >
        <span className="chatBubbleLogoWrap">
          <img src="/vidco-logo.png" alt="Vidco" className="chatBubbleLogo" />
        </span>
      </button>
    );
  }

  if (sessionData.requireConsent && !hasConsented) {
    return (
      <KvkkConsentGate
        apiUrl={API_URL}
        sessionToken={sessionToken}
        apiKey={API_KEY}
        onClose={close}
        onConsented={() => {
          window.localStorage.setItem(getConsentStorageKey(sessionData.botId), "1");
          setHasConsented(true);
        }}
      />
    );
  }

  return (
    <ChatConversation
      onClose={close}
      userRoles={sessionData.userRoles}
      currentPage={sessionData.currentPage ?? undefined}
    />
  );
}