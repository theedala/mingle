"use client";

import { useState, useEffect, useCallback } from "react";
import { api } from "./api";
import { userStore, matchesStore, UserProfile, ActiveMatch } from "./store";

/**
 * Hook for managing user profile
 */
export function useUser() {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = userStore.getUser();
    setUser(stored);
    setLoading(false);
  }, []);

  const createProfile = useCallback(
    async (profile: {
      displayName: string;
      interests: string[];
      conversationStyle: string;
      energyLevel: string;
    }) => {
      const result = await api.createProfile({
        interests: profile.interests,
        conversation_style: profile.conversationStyle,
        energy_level: profile.energyLevel,
        languages: ["en"],
      });

      if (result.data) {
        const newUser: UserProfile = {
          anonymousId: result.data.anonymous_id,
          displayName: profile.displayName,
          interests: profile.interests,
          conversationStyle: profile.conversationStyle,
          energyLevel: profile.energyLevel,
          reputationScore: 50,
        };
        userStore.setUser(newUser);
        setUser(newUser);
        return { success: true };
      }

      return { success: false, error: result.error };
    },
    []
  );

  const updateMood = useCallback(
    async (mood: string) => {
      if (!user) return;
      await api.updateMood(user.anonymousId, mood);
      userStore.updateUser({ currentMood: mood });
      setUser((prev) => (prev ? { ...prev, currentMood: mood } : prev));
    },
    [user]
  );

  const logout = useCallback(() => {
    userStore.clearUser();
    matchesStore.clearMatches();
    setUser(null);
  }, []);

  return {
    user,
    loading,
    isLoggedIn: !!user,
    createProfile,
    updateMood,
    logout,
  };
}

/**
 * Hook for matching
 */
export function useMatching() {
  const [searching, setSearching] = useState(false);
  const [matchFound, setMatchFound] = useState<{
    matchId: string;
    partner: {
      displayName: string;
      interests: string[];
      compatibility: number;
    };
  } | null>(null);

  const findMatch = useCallback(async (anonymousId: string) => {
    setSearching(true);
    setMatchFound(null);

    const result = await api.findMatch(anonymousId);

    if (result.data?.status === "match_found" && result.data.match_id && result.data.partner) {
      const match = {
        matchId: result.data.match_id,
        partner: {
          displayName: result.data.partner.display_name,
          interests: result.data.partner.interests,
          compatibility: result.data.partner.compatibility,
        },
      };
      setMatchFound(match);

      // Save to matches store
      matchesStore.addMatch({
        matchId: match.matchId,
        partnerName: match.partner.displayName,
        partnerInterests: match.partner.interests,
        compatibility: match.partner.compatibility,
        unreadCount: 0,
        createdAt: new Date().toISOString(),
      });
    }

    setSearching(false);
    return result;
  }, []);

  const cancelSearch = useCallback(() => {
    setSearching(false);
  }, []);

  const unmatch = useCallback(async (matchId: string, anonymousId: string, reason?: string) => {
    const result = await api.unmatch(matchId, anonymousId, reason);
    if (result.data) {
      matchesStore.removeMatch(matchId);
    }
    return result;
  }, []);

  return {
    searching,
    matchFound,
    findMatch,
    cancelSearch,
    unmatch,
  };
}

/**
 * Hook for active matches
 */
export function useActiveMatches() {
  const [matches, setMatches] = useState<ActiveMatch[]>([]);

  useEffect(() => {
    setMatches(matchesStore.getMatches());
  }, []);

  const refreshMatches = useCallback(() => {
    setMatches(matchesStore.getMatches());
  }, []);

  return { matches, refreshMatches };
}

/**
 * Hook for chat messages
 */
export function useChat(matchId: string, anonymousId: string) {
  const [messages, setMessages] = useState<
    Array<{
      id: string;
      sender: "me" | "partner";
      text: string;
      timestamp: Date;
      reactions: string[];
    }>
  >([]);
  const [connected, setConnected] = useState(false);
  const [partnerTyping, setPartnerTyping] = useState(false);

  useEffect(() => {
    let ws: WebSocket | null = null;

    const connect = () => {
      const wsUrl = `ws://localhost:8000/api/v1/chat/ws/${matchId}?anonymous_id=${anonymousId}`;
      ws = new WebSocket(wsUrl);

      ws.onopen = () => setConnected(true);
      ws.onclose = () => setConnected(false);

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === "message") {
          setMessages((prev) => [
            ...prev,
            {
              id: data.message_id || Date.now().toString(),
              sender: data.sender_id === anonymousId ? "me" : "partner",
              text: data.content,
              timestamp: new Date(data.timestamp || Date.now()),
              reactions: [],
            },
          ]);
        } else if (data.type === "typing") {
          setPartnerTyping(true);
          setTimeout(() => setPartnerTyping(false), 3000);
        }
      };
    };

    connect();

    return () => {
      ws?.close();
    };
  }, [matchId, anonymousId]);

  const sendMessage = useCallback(
    (text: string) => {
      // For now, add optimistically - WebSocket will handle actual send
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          sender: "me",
          text,
          timestamp: new Date(),
          reactions: [],
        },
      ]);
    },
    []
  );

  return {
    messages,
    connected,
    partnerTyping,
    sendMessage,
  };
}

/**
 * Hook for ice breakers
 */
export function useIceBreakers(matchId: string) {
  const [currentPrompt, setCurrentPrompt] = useState<{
    gameType: string;
    prompt: string;
    options?: string[];
  } | null>(null);
  const [loading, setLoading] = useState(false);

  const getNextPrompt = useCallback(
    async (gameType?: string) => {
      setLoading(true);
      const result = await api.getIceBreaker(matchId, gameType);
      if (result.data) {
        setCurrentPrompt({
          gameType: result.data.game_type,
          prompt: result.data.prompt,
          options: result.data.options,
        });
      }
      setLoading(false);
    },
    [matchId]
  );

  return {
    currentPrompt,
    loading,
    getNextPrompt,
  };
}
