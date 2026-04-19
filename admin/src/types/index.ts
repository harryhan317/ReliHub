export interface DashboardStats {
  total_users: number;
  active_users: number;
  total_resources: number;
  pending_resources: number;
  total_topics: number;
  total_posts: number;
  total_revenue: number;
  total_feedbacks: number;
  pending_feedbacks: number;
}

export interface AdminUser {
  id: string;
  nickname: string;
  phone: string | null;
  status: string;
  rank: string;
  reputation_points: number;
  gold_beans: number;
  bonus_beans: number;
  is_expert: boolean;
  created_at: string;
  last_login_at: string | null;
}

export interface AdminUserListResponse {
  users: AdminUser[];
  total: number;
  page: number;
  page_size: number;
}

export interface ResourceItem {
  id: string;
  uploader_id: string;
  title: string;
  description: string | null;
  category_id: number;
  price: number;
  status: string;
  view_count: number;
  download_count: number;
  created_at: string;
}

export interface ResourceListResponse {
  resources: ResourceItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface TopicItem {
  id: string;
  author_id: string;
  title: string;
  content: string;
  category_id: number;
  status: string;
  view_count: number;
  post_count: number;
  created_at: string;
}

export interface TopicListResponse {
  topics: TopicItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface FeedbackItem {
  id: string;
  user_id: string;
  type: string;
  content: string;
  status: string;
  reply: string | null;
  replied_at: string | null;
  created_at: string;
}

export interface FeedbackListResponse {
  feedbacks: FeedbackItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface AuditLogItem {
  id: string;
  admin_id: string;
  action: string;
  target_type: string;
  target_id: string;
  detail: string;
  ip_address: string | null;
  created_at: string;
}

export interface AuditLogListResponse {
  items: AuditLogItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface SystemConfig {
  id: string;
  config_key: string;
  config_value: string;
  description: string | null;
  updated_by: string | null;
  created_at: string;
  updated_at: string;
}

export interface SystemConfigListResponse {
  configs: SystemConfig[];
  total: number;
}

export interface LLMProvider {
  id: string;
  name: string;
  display_name: string;
  api_base_url: string;
  is_active: boolean;
  cost_per_1k_tokens: number;
  rate_limit_per_minute: number;
  created_at: string;
}

export interface AssetPackage {
  id: string;
  name: string;
  price_beans: number;
  discount_rate: number;
  description: string;
}

export interface AdminLoginRequest {
  username: string;
  password: string;
}

export interface AdminLoginResponse {
  access_token: string;
  admin_info: {
    id: string;
    username: string;
    role: 'SUPER_ADMIN' | 'OPERATOR' | 'AUDITOR';
  };
}
