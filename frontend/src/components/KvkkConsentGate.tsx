import { useState } from "react";
import { sendConsent } from "../api/chatApi";

const KVKK_URL = "https://vidco.com.tr/kvkk-aydinlatma-metni";

type KvkkConsentGateProps = {
  apiUrl: string;
  sessionToken: string;
  apiKey?: string;
  onConsented: () => void;
  onClose: () => void;
};

export function KvkkConsentGate({ apiUrl, sessionToken, apiKey, onConsented, onClose }: KvkkConsentGateProps) {
  const [name, setName] = useState("");
  const [accepted, setAccepted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const canSubmit = name.trim().length > 0 && accepted && !isSubmitting;

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!canSubmit) return;

    setIsSubmitting(true);
    setError(null);

    try {
      await sendConsent(apiUrl, sessionToken, name.trim(), apiKey);
      onConsented();
    } catch (submitError) {
      const message = submitError instanceof Error ? submitError.message : "Onay kaydedilemedi. Lütfen tekrar deneyin.";
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="chatWindow">
      <div className="chatHeader">
        <div>
          <h2>Vidco Yardım Asistanı</h2>
          <p>Sohbete başlamadan önce</p>
        </div>

        <div className="chatHeaderActions">
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

      <form className="consentGate" onSubmit={handleSubmit}>
        <p className="consentIntro">
          Sohbeti başlatmadan önce adınızı girip aydınlatma metnini onaylamanız gerekiyor.
        </p>

        <label className="consentLabel" htmlFor="consent-name">
          Ad Soyad
        </label>
        <input
          id="consent-name"
          className="chatInput consentNameInput"
          value={name}
          onChange={(event) => setName(event.target.value)}
          placeholder="Ad Soyad"
          disabled={isSubmitting}
          autoFocus
        />

        <label className="consentCheckboxRow">
          <input
            type="checkbox"
            checked={accepted}
            onChange={(event) => setAccepted(event.target.checked)}
            disabled={isSubmitting}
          />
          <span>
            <a href={KVKK_URL} target="_blank" rel="noopener noreferrer">
              KVKK Aydınlatma Metni
            </a>
            'ni okudum, kabul ediyorum.
          </span>
        </label>

        {error && <p className="consentError">{error}</p>}

        <button className="chatSendButton consentSubmitButton" type="submit" disabled={!canSubmit}>
          {isSubmitting ? "..." : "Sohbeti başlat"}
        </button>
      </form>
    </div>
  );
}