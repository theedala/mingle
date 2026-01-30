/**
 * API Client for Mingle Backend
 */

// In production, use empty string for relative URLs (nginx proxies /api to backend)
// In development, use localhost:8000
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

interface ApiResponse<T> {
  data?: T;
  error?: string;
}

class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  setToken(token: string) {
    this.token = token;
  }

  clearToken() {
    this.token = null;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    };

    if (this.token) {
      (headers as Record<string, string>)['Authorization'] = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        ...options,
        headers,
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        return { error: error.detail || 'Request failed' };
      }

      const data = await response.json();
      return { data };
    } catch (error) {
      return { error: 'Network error' };
    }
  }

  // Profiles
  async createProfile(profile: {
    interests: string[];
    conversation_style: string;
    energy_level: string;
    languages?: string[];
    topics_to_avoid?: string[];
  }) {
    return this.request<{ anonymous_id: string; reputation_score: number }>('/api/v1/profiles/', {
      method: 'POST',
      body: JSON.stringify(profile),
    });
  }

  async getProfile(anonymousId: string) {
    return this.request<{
      anonymous_id: string;
      display_name: string;
      interests: string[];
      conversation_style: string;
      energy_level: string;
      reputation_score: number;
    }>(`/api/v1/profiles/${anonymousId}`);
  }

  async updateProfile(anonymousId: string, updates: Record<string, unknown>) {
    return this.request(`/api/v1/profiles/${anonymousId}`, {
      method: 'PATCH',
      body: JSON.stringify(updates),
    });
  }

  async updateMood(anonymousId: string, mood: string) {
    return this.request(`/api/v1/profiles/${anonymousId}/mood`, {
      method: 'POST',
      body: JSON.stringify({ mood }),
    });
  }

  // Matching
  async findMatch(anonymousId: string) {
    return this.request<{
      status: string;
      match_id?: string;
      partner?: {
        display_name: string;
        interests: string[];
        compatibility: number;
      };
    }>('/api/v1/matching/find', {
      method: 'POST',
      body: JSON.stringify({ anonymous_id: anonymousId }),
    });
  }

  async getQueueStatus() {
    return this.request<{
      queue_size: number;
      estimated_wait: number;
    }>('/api/v1/matching/queue/status');
  }

  async unmatch(matchId: string, anonymousId: string, reason?: string) {
    return this.request('/api/v1/matching/unmatch', {
      method: 'POST',
      body: JSON.stringify({ match_id: matchId, anonymous_id: anonymousId, reason }),
    });
  }

  async rateConversation(matchId: string, anonymousId: string, rating: number) {
    return this.request('/api/v1/matching/rate', {
      method: 'POST',
      body: JSON.stringify({ match_id: matchId, anonymous_id: anonymousId, rating }),
    });
  }

  // Moderation
  async reportUser(reporterId: string, reportedId: string, reason: string, details?: string) {
    return this.request('/api/v1/moderation/report', {
      method: 'POST',
      body: JSON.stringify({
        reporter_id: reporterId,
        reported_id: reportedId,
        reason,
        details,
      }),
    });
  }

  async blockUser(blockerId: string, blockedId: string) {
    return this.request('/api/v1/moderation/block', {
      method: 'POST',
      body: JSON.stringify({ blocker_id: blockerId, blocked_id: blockedId }),
    });
  }

  async unblockUser(blockerId: string, blockedId: string) {
    return this.request('/api/v1/moderation/unblock', {
      method: 'POST',
      body: JSON.stringify({ blocker_id: blockerId, blocked_id: blockedId }),
    });
  }

  async getBlockedUsers(anonymousId: string) {
    return this.request<{ blocked_users: Array<{ anonymous_id: string; blocked_at: string }> }>(
      `/api/v1/moderation/blocked/${anonymousId}`
    );
  }

  // Chat
  async getMessages(matchId: string, limit = 50) {
    return this.request<{
      messages: Array<{
        id: string;
        sender_id: string;
        content: string;
        timestamp: string;
        reactions: string[];
      }>;
    }>(`/api/v1/chat/messages/${matchId}?limit=${limit}`);
  }

  // Ice Breakers
  async getIceBreaker(matchId: string, gameType?: string) {
    const params = gameType ? `?game_type=${gameType}` : '';
    return this.request<{
      game_type: string;
      prompt: string;
      options?: string[];
      category: string;
    }>(`/api/v1/icebreakers/prompt/${matchId}${params}`);
  }

  async getIceBreakerSequence(matchId: string, count = 5) {
    return this.request<
      Array<{
        game_type: string;
        prompt: string;
        options?: string[];
        category: string;
      }>
    >(`/api/v1/icebreakers/sequence/${matchId}?count=${count}`);
  }

  // Video
  async startVideoSession(matchId: string, anonymousId: string) {
    return this.request('/api/v1/video/start/' + matchId, {
      method: 'POST',
      body: JSON.stringify({ anonymous_id: anonymousId }),
    });
  }

  async toggleBlur(matchId: string, anonymousId: string, blurOn: boolean) {
    return this.request(`/api/v1/video/toggle-blur/${matchId}?blur_on=${blurOn}&anonymous_id=${anonymousId}`, {
      method: 'POST',
    });
  }

  async endVideoSession(matchId: string, anonymousId: string) {
    return this.request(`/api/v1/video/end/${matchId}?anonymous_id=${anonymousId}`, {
      method: 'POST',
    });
  }

  // Analytics
  async getInsights(anonymousId: string) {
    return this.request<{
      matches_this_week: number;
      avg_conversation_length: number;
      top_shared_interests: string[];
      best_match_times: string[];
    }>(`/api/v1/analytics/insights/${anonymousId}`);
  }
}

// Singleton instance
export const api = new ApiClient(API_BASE_URL);

// WebSocket connections
export function createChatWebSocket(matchId: string, anonymousId: string) {
  const wsUrl = `${API_BASE_URL.replace('http', 'ws')}/api/v1/chat/ws/${matchId}?anonymous_id=${anonymousId}`;
  return new WebSocket(wsUrl);
}

export function createVideoWebSocket(anonymousId: string) {
  const wsUrl = `${API_BASE_URL.replace('http', 'ws')}/api/v1/video/signal/${anonymousId}`;
  return new WebSocket(wsUrl);
}
