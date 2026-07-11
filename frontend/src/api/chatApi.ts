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

export async function sendChatMessage(apiUrl: string,conversationId: string,message: string,apiKey?: string): Promise<ChatResponse> {
  const headers: Record<string, string> = {"Content-Type": "application/json"};
  if (apiKey) headers["X-API-Key"] = apiKey;

  const response = await fetch(`${apiUrl}/api/chat`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      conversation_id: conversationId,
      message,
    }),
  });
  const data = await response.json();

  if (!response.ok) {
    const errorMessage = data?.detail?.message || "Mesaj gönderilirken bir hata oluştu.";
    throw new Error(errorMessage);
  }
  return data;
}