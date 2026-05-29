const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export type SectionMap = Record<string, string | string[]>;

export type PaperChunk = {
  chunk_id: string;
  paper_id: string;
  section: string;
  text: string;
  page: number | null;
  score?: number | null;
};

export type Paper = {
  paper_id: string;
  filename: string;
  original_filename?: string;
  sections: SectionMap;
  chunks?: PaperChunk[];
};

export type PaperAnalysis = {
  title: string;
  problem: string;
  objective: string;
  method: string;
  results: string[];
  limitations: string[];
  future_work: string[];
  citations?: string[];
};

export type ChatResponse = {
  answer: string;
  sources: PaperChunk[];
};

export async function uploadPaper(file: File): Promise<Paper> {
  const formData = new FormData();
  formData.append("file", file);

  return request<Paper>("/api/papers/upload", {
    method: "POST",
    body: formData,
  });
}

export async function getPapers(): Promise<Paper[]> {
  const data = await request<{ papers: Paper[] }>("/api/papers");
  return data.papers;
}

export async function getPaper(paperId: string): Promise<Paper> {
  return request<Paper>(`/api/papers/${paperId}`);
}

export async function askQuestion(
  paperId: string,
  question: string,
): Promise<ChatResponse> {
  return request<ChatResponse>("/api/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      paper_id: paperId,
      question,
    }),
  });
}

export async function getSummary(paperId: string): Promise<PaperAnalysis> {
  return request<PaperAnalysis>(`/api/papers/${paperId}/analysis`);
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, init);
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with ${response.status}`);
  }

  return response.json() as Promise<T>;
}
