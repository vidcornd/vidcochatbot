import { useCallback, useEffect, useState } from "react";
import { ChatConversation } from "./ChatConversation";
import type { WidgetSessionData } from "../api/widgetApi";

type EmbedChatProps = {sessionData: WidgetSessionData;};

type ParentMessage = {
  source?: string;
  type?: string;
  payload?: unknown;
};

const OPEN_SIZE = { width: 380, height: 600 };
const CLOSED_SIZE = { width: 80, height: 80 };

export function EmbedChat({ sessionData }: EmbedChatProps) {
  const [isOpen, setIsOpen] = useState(false);

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

  return <ChatConversation onClose={close} />;
}