export type Profile = { name: string; age: string; state: string; district: string; category: string; gender: string; classLevel: string; course: string; marks: string; income: string; rural: boolean };
export type Opportunity = { id: string; title: string; org: string; tag: string; amount: string; period: string; desc: string; criteria: string; is_mock: true };
export type EligibilityResult = { opportunity_id: string; eligible: boolean; reason: string; is_mock: true };
export type AssistantContext = { class_level?: string; course?: string; rural?: boolean; completed_documents?: string[] };
export type AssistantMessage = { role: 'user' | 'assistant'; content: string };
export type AssistantResponse = { answer: string; mode: 'llm' | 'demo_fallback'; label: string };

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/+$/, '');

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 15000);
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, { ...options, signal: controller.signal, headers: { 'Content-Type': 'application/json', ...options?.headers } });
  } catch (error) {
    if (controller.signal.aborted) throw new Error('The assistant request timed out. Please try again.');
    throw error;
  } finally {
    window.clearTimeout(timeout);
  }
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail || `API request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<{ status: string }>('/health'),
  opportunities: () => request<Opportunity[]>('/opportunities'),
  eligibility: (profile: Profile) => request<EligibilityResult[]>('/eligibility/check', { method: 'POST', body: JSON.stringify({ profile }) }),
  getProfile: (id: string) => request<{ student_id: string; profile: Profile }>(`/profile/${encodeURIComponent(id)}`),
  saveProfile: (id: string, profile: Profile) => request<{ saved: boolean }>(`/profile/${encodeURIComponent(id)}`, { method: 'PUT', body: JSON.stringify(profile) }),
  getDocuments: (id: string) => request<{ student_id: string; checked: string[] }>(`/documents/${encodeURIComponent(id)}`),
  saveDocuments: (id: string, checked: string[]) => request<{ saved: boolean }>(`/documents/${encodeURIComponent(id)}`, { method: 'PUT', body: JSON.stringify({ checked }) }),
  assistantChat: (question: string, context: AssistantContext, history: AssistantMessage[]) => request<AssistantResponse>('/assistant/chat', { method: 'POST', body: JSON.stringify({ question, context, history }) }),
  assistantGuidance: (documentId: string, context: AssistantContext) => request<AssistantResponse>('/assistant/guidance', { method: 'POST', body: JSON.stringify({ document_id: documentId, context }) }),
};
