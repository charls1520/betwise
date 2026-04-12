export interface Source {
  type: "news" | "odds";
  title?: string;
  snippet?: string;
  market?: string;
  value?: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "bot";
  content: string;
  sources?: Source[];
}