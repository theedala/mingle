/**
 * User store - manages user state with localStorage persistence
 */

export interface UserProfile {
  anonymousId: string;
  displayName: string;
  interests: string[];
  conversationStyle: string;
  energyLevel: string;
  currentMood?: string;
  reputationScore: number;
}

const STORAGE_KEY = 'mingle_user';

export const userStore = {
  getUser(): UserProfile | null {
    if (typeof window === 'undefined') return null;
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : null;
  },

  setUser(user: UserProfile) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
  },

  updateUser(updates: Partial<UserProfile>) {
    const current = this.getUser();
    if (current) {
      this.setUser({ ...current, ...updates });
    }
  },

  clearUser() {
    localStorage.removeItem(STORAGE_KEY);
  },

  isLoggedIn(): boolean {
    return !!this.getUser();
  },
};

// Active matches store
export interface ActiveMatch {
  matchId: string;
  partnerName: string;
  partnerInterests: string[];
  compatibility: number;
  lastMessage?: string;
  unreadCount: number;
  createdAt: string;
}

const MATCHES_KEY = 'mingle_matches';

export const matchesStore = {
  getMatches(): ActiveMatch[] {
    if (typeof window === 'undefined') return [];
    const stored = localStorage.getItem(MATCHES_KEY);
    return stored ? JSON.parse(stored) : [];
  },

  addMatch(match: ActiveMatch) {
    const matches = this.getMatches();
    matches.unshift(match);
    localStorage.setItem(MATCHES_KEY, JSON.stringify(matches));
  },

  updateMatch(matchId: string, updates: Partial<ActiveMatch>) {
    const matches = this.getMatches();
    const index = matches.findIndex((m) => m.matchId === matchId);
    if (index !== -1) {
      matches[index] = { ...matches[index], ...updates };
      localStorage.setItem(MATCHES_KEY, JSON.stringify(matches));
    }
  },

  removeMatch(matchId: string) {
    const matches = this.getMatches().filter((m) => m.matchId !== matchId);
    localStorage.setItem(MATCHES_KEY, JSON.stringify(matches));
  },

  clearMatches() {
    localStorage.removeItem(MATCHES_KEY);
  },
};
