export type Profile = { name: string; age: string; state: string; district: string; category: string; gender: string; classLevel: string; course: string; marks: string; income: string; rural: boolean };
export type Opportunity = { id: string; title: string; org: string; tag: string; amount: string; period: string; desc: string; criteria: string; is_mock: true };
export type EligibilityResult = { opportunity_id: string; eligible: boolean; reason: string; is_mock: true };

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, { ...options, headers: { 'Content-Type': 'application/json', ...options?.headers } });
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
};
