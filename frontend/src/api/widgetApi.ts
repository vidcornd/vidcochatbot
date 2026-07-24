export type WidgetSessionData = {
  botId: string;
  username?: string | null;
  userEmail?: string | null;
  userRoles: string[];
  rolesVerified: boolean;
  currentPage?: string | null;
  pageTitle?: string | null;
  origin: string;
};

export async function fetchWidgetSession(apiUrl: string, sessionToken: string): Promise<WidgetSessionData> {
  const response = await fetch(`${apiUrl}/api/widget/session/${encodeURIComponent(sessionToken)}`);
  const data = await response.json();

  if (!response.ok) {
    const errorMessage = data?.detail?.message || "Oturum bulunamadı veya süresi dolmuş.";
    throw new Error(errorMessage);
  }

  return data;
}