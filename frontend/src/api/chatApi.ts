export type Source = {
  title?: string | null;
  source?: string | null;
  page?: number | null;
};

export type ChatResponse = {
  answer: string;
  sources: Source[];
  confidence: "low" | "medium" | "high";
  conversation_id: string;
};

export async function sendChatMessage(apiUrl: string,conversationId: string,message: string,apiKey?: string,userRoles?: string[],currentPage?: string): Promise<ChatResponse> {
  const headers: Record<string, string> = {"Content-Type": "application/json"};
  if (apiKey) headers["X-API-Key"] = apiKey;

  const response = await fetch(`${apiUrl}/api/chat`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      conversation_id: conversationId,
      message,
      user_roles: userRoles || [],
      current_page: currentPage,
    }),
  });
  const data = await response.json();

  if (!response.ok) {
    const errorMessage = data?.detail?.message || "Mesaj gönderilirken bir hata oluştu.";
    throw new Error(errorMessage);
  }
  return data;
}

export async function sendFeedback(apiUrl: string,conversationId: string,rating: "up" | "down",question: string,answer: string,apiKey?: string): Promise<void> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (apiKey) {
    headers["X-API-Key"] = apiKey;
  }

  const response = await fetch(`${apiUrl}/api/feedback`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      conversation_id: conversationId,
      rating,
      question,
      answer,
    }),
  });

  if (!response.ok) {
    throw new Error("Geri bildirim gönderilirken bir hata oluştu.");
  }
}

export async function sendConsent(apiUrl: string,sessionToken: string,name: string,apiKey?: string): Promise<void> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (apiKey) {
    headers["X-API-Key"] = apiKey;
  }

  const response = await fetch(`${apiUrl}/api/consent`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      session_token: sessionToken,
      name,
    }),
  });

  if (!response.ok) {
    throw new Error("Onay kaydedilemedi. Lütfen tekrar deneyin.");
  }
}