const CONVERSATION_ID_KEY = "vidco_conversation_id";

export function getConversationId(): string {
  let conversationId = localStorage.getItem(CONVERSATION_ID_KEY);

  if (!conversationId) {
    conversationId = crypto.randomUUID();
    localStorage.setItem(CONVERSATION_ID_KEY, conversationId);
  }

  return conversationId;
}

export function resetConversationId(): string {
  const conversationId = crypto.randomUUID();
  localStorage.setItem(CONVERSATION_ID_KEY, conversationId);
  return conversationId;
}