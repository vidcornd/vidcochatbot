import { useState } from "react";
import { ChatConversation } from "./ChatConversation";

export function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="chatWidget">
      {isOpen && <ChatConversation onClose={() => setIsOpen(false)} />}

      <button
        className="chatBubble"
        onClick={() => setIsOpen((currentValue) => !currentValue)}
        aria-label="Vidco yardım asistanını aç"
        type="button"
      >
        <span className="chatBubbleLogoWrap">
          <img src="/vidco-logo.png" alt="Vidco" className="chatBubbleLogo" />
        </span>
      </button>
    </div>
  );
}