export interface ApiResponse<T = unknown> {
  code: number;
  data: T;
  msg: string;
}

export interface PaginatedResponse<T> {
  total: number;
  items: T[];
  has_more: boolean;
}

export interface User {
  id: string;
  phone: string;
  nickname: string;
  avatar_url: string;
  gender: string;
  company: string;
  position: string;
  email: string;
  level: string;
  credit_score: number;
  cocoa_beans: number;
  reputation_points: number;
  is_guest: boolean;
  checked_in_today: boolean;
  early_bird_available: boolean;
  early_bird_count: number;
  topic_count?: number;
  resource_count?: number;
  created_at: string;
}

export interface AuthState {
  isGuest: boolean;
  isLoggedIn: boolean;
  isNewUser: boolean;
  accessToken: string | null;
  refreshToken: string | null;
  user: User | null;
}

export interface LoginParams {
  phone: string;
  code?: string;
  password?: string;
  agreed_to_terms: boolean;
}

export interface RegisterParams {
  phone: string;
  code: string;
  password?: string;
  agreed_to_terms: boolean;
}

export interface AISession {
  id: string;
  title: string;
  message_count: number;
  status: 'active' | 'resolved';
  created_at: string;
  updated_at: string;
}

export interface AIMessage {
  id: string;
  session_id: string;
  role: 'user' | 'assistant';
  content: string;
  liked: boolean;
  disliked: boolean;
  created_at: string;
}

export interface Resource {
  id: string;
  title: string;
  description: string;
  category: string;
  tags: string[];
  file_url?: string;
  file_size: number;
  file_type: string;
  download_count: number;
  view_count?: number;
  like_count: number;
  collect_count?: number;
  price: number;
  is_free?: boolean;
  status?: 'pending' | 'approved' | 'rejected';
  author_id?: string;
  author_name?: string;
  author_avatar?: string;
  uploader_id?: string;
  uploader_name?: string;
  created_at: string;
  updated_at?: string;
}

export interface Topic {
  id: string;
  title: string;
  content: string;
  category: string;
  tags: string[];
  reply_count: number;
  like_count: number;
  view_count: number;
  is_essence: boolean;
  is_resolved?: boolean;
  bounty: number;
  status?: 'discussing' | 'resolved' | 'closed';
  author_id: string;
  author_name: string;
  author_avatar: string;
  author_level?: string;
  best_reply_id: string | null;
  created_at: string;
  updated_at?: string;
}

export interface Reply {
  id: string;
  topic_id: string;
  content: string;
  like_count: number;
  is_best: boolean;
  author_id: string;
  author_name: string;
  author_avatar: string;
  author_level: string;
  created_at: string;
}

export interface Notification {
  id: string;
  type: string;
  title: string;
  content?: string;
  description?: string;
  is_read: boolean;
  created_at: string;
}

export interface Feedback {
  id: string;
  type: string;
  content: string;
  screenshots: string[];
  contact: string;
  status: 'pending' | 'processing' | 'resolved';
  created_at: string;
}

export interface SearchParams {
  query: string;
  type: 'RESOURCE' | 'COMMUNITY' | 'AI';
  page?: number;
  page_size?: number;
}

export interface ResourceCategory {
  id: string;
  name: string;
  icon: string;
  count: number;
}

export interface CommunityCategory {
  id: string;
  name: string;
  icon: string;
  icon_bg_color: string;
}
