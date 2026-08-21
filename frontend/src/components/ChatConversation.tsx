import { useEffect, useRef, useState } from "react";
import { sendChatMessage, sendFeedback, type Source } from "../api/chatApi";
import { getConversationId, resetConversationId } from "../utils/conversation";
import { SourceCard } from "./SourceCard";
import { FeedbackButtons } from "./FeedbackButtons";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  isError?: boolean;
  question?: string;
  feedback?: "up" | "down";
};

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
const API_KEY = import.meta.env.VITE_WIDGET_API_KEY || "";

const EXAMPLE_QUESTIONS = [
  "Muayene raporu nasıl hazırlanır?",
  "E-imza süreci nasıl yapılır?",
  "Mobil uygulama nasıl yüklenir?",
];

const WELCOME_MESSAGE: Message = {
  id: "welcome-message",
  role: "assistant",
  content: "Merhaba. Vidco 17020 kullanım kılavuzları hakkında yardımcı olabilirim.",
};

type ChatConversationProps = { onClose: () => void;userRoles?: string[];currentPage?: string;};

export function ChatConversation({ onClose, userRoles, currentPage }: ChatConversationProps) {
  const [conversationId, setConversationId] = useState(() => getConversationId());
  const [messages, setMessages] = useState<Message[]>([WELCOME_MESSAGE]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const shouldShowExamples = messages.length === 1 && !isLoading;

  useEffect(() => {messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });}, [messages, isLoading]);

  useEffect(() => { window.setTimeout(() => {inputRef.current?.focus();}, 100);}, []);

  async function sendMessage(messageText?: string) {
    const rawInput = messageText ?? input;
    const trimmedInput = rawInput.trim();

    if (!trimmedInput || isLoading) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: trimmedInput,
    };

    setMessages((currentMessages) => [...currentMessages, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await sendChatMessage(API_URL,conversationId,trimmedInput,API_KEY,userRoles,currentPage);
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: response.answer,
        sources: response.sources,
        question: trimmedInput,
      };

      setMessages((currentMessages) => [
        ...currentMessages,
        assistantMessage,
      ]);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Mesaj gönderilirken bir hata oluştu.";

      const assistantErrorMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: errorMessage,
        sources: [],
        isError: true,
      };

      setMessages((currentMessages) => [
        ...currentMessages,
        assistantErrorMessage,
      ]);
    } finally {
      setIsLoading(false);

      window.setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
    }
  }

  function handleFeedback(message: Message, rating: "up" | "down") {
    setMessages((currentMessages) =>
      currentMessages.map((current) =>
        current.id === message.id ? { ...current, feedback: rating } : current
      )
    );

    sendFeedback(API_URL,conversationId,rating,message.question ?? "",message.content,API_KEY).catch(() => {});
  }

  function handleResetConversation() {
    const newConversationId = resetConversationId();

    setConversationId(newConversationId);
    setMessages([
      {
        id: "welcome-message",
        role: "assistant",
        content:
          "Yeni konuşma başlatıldı. Vidco 17020 kullanım kılavuzları hakkında yardımcı olabilirim.",
      },
    ]);
    setInput("");

    window.setTimeout(() => {
      inputRef.current?.focus();
    }, 100);
  }

  function handleKeyDown(event: React.KeyboardEvent<HTMLInputElement>) {
    if (event.key === "Enter" && !isLoading) sendMessage();
  }

  return (
    <div className="chatWindow">
      <div className="chatHeader">
        <div>
          <h2>Vidco Dijital Yardım Asistanı</h2>
          <p>17020 Kullanım Kılavuzları</p>
        </div>

        <div className="chatHeaderActions">
          <button
            className="chatResetButton"
            onClick={handleResetConversation}
            type="button"
          >
            Yeni
          </button>

          <button
            className="chatCloseButton"
            onClick={onClose}
            aria-label="Chat penceresini kapat"
            type="button"
          >
            ×
          </button>
        </div>
      </div>

      <div className="chatSessionDebug">
        Session: {conversationId.slice(0, 8)}
      </div>

      <div className="chatMessages">
        {messages.map((message) => (
          <div
            key={message.id}
            className={
              message.role === "user"
                ? "chatMessageWrapper userMessageWrapper"
                : "chatMessageWrapper assistantMessageWrapper"
            }
          >
            <div
              className={
                message.role === "user"
                  ? "chatMessage userMessage"
                  : message.isError
                  ? "chatMessage assistantMessage errorMessage"
                  : "chatMessage assistantMessage"
              }
            >
              <div className="messageText">{message.content}</div>
            </div>

            {message.role === "assistant" &&
              !message.isError &&
              message.sources &&
              message.sources.length > 0 && (
                <SourceCard sources={message.sources} />
              )}

            {message.role === "assistant" &&
              !message.isError &&
              message.id !== "welcome-message" && (
                <FeedbackButtons
                  value={message.feedback}
                  onRate={(rating) => handleFeedback(message, rating)}
                />
              )}
          </div>
        ))}
        {shouldShowExamples && (
          <div className="emptyState">
            <div className="emptyStateTitle">Örnek sorular</div>

            <div className="exampleQuestions">
              {EXAMPLE_QUESTIONS.map((question) => (
                <button
                  key={question}
                  className="exampleQuestionButton"
                  type="button"
                  onClick={() => sendMessage(question)}
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        )}

        {isLoading && (
          <div className="chatMessageWrapper assistantMessageWrapper">
            <div className="chatMessage assistantMessage loadingMessage">
              <div className="typingDots" aria-label="Yanıt hazırlanıyor">
                <span />
                <span />
                <span />
              </div>
              <span>Yanıt hazırlanıyor...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="chatInputArea">
        <input
          ref={inputRef}
          value={input}
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Sorunuzu yazın..."
          className="chatInput"
          disabled={isLoading}
        />

        <button
          onClick={() => sendMessage()}
          className="chatSendButton"
          disabled={!input.trim() || isLoading}
          type="button"
        >
          {isLoading ? "..." : "Gönder"}
        </button>
      </div>
    </div>
  );
}