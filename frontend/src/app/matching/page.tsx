"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { userStore, matchesStore } from "@/lib/store";
import { api } from "@/lib/api";

export default function MatchingPage() {
  const router = useRouter();
  const [status, setStatus] = useState<"searching" | "found" | "connecting">("searching");
  const [matchData, setMatchData] = useState<{
    matchId: string;
    name: string;
    compatibility: number;
    interests: string[];
    style: string;
  } | null>(null);
  const [searchTime, setSearchTime] = useState(0);
  const [user, setUser] = useState<{ anonymousId: string } | null>(null);

  useEffect(() => {
    const stored = userStore.getUser();
    if (!stored) {
      router.push("/onboarding");
      return;
    }
    setUser({ anonymousId: stored.anonymousId });
  }, [router]);

  // Define findMatch outside to be reusable
  const findMatch = async (currentUserId: string) => {
    try {
      const result = await api.findMatch(currentUserId);

      if (result.data?.status === "match_found" && result.data.match_id && result.data.partner) {
        const match = {
          matchId: result.data.match_id,
          name: result.data.partner.display_name,
          compatibility: result.data.partner.compatibility,
          interests: result.data.partner.interests,
          style: "Playful", // Would come from API
        };

        setMatchData(match);
        setStatus("found");

        // Save to local store
        matchesStore.addMatch({
          matchId: match.matchId,
          partnerName: match.name,
          partnerInterests: match.interests,
          compatibility: match.compatibility,
          unreadCount: 0,
          createdAt: new Date().toISOString(),
        });
      } else {
        // Still searching/queued - retry after delay
        setTimeout(() => findMatch(currentUserId), 3000);
      }
    } catch (error) {
      console.error("Error finding match:", error);
      // Retry on error too
      setTimeout(() => findMatch(currentUserId), 3000);
    }
  };

  useEffect(() => {
    if (!user) return;

    // Search timer
    const timer = setInterval(() => {
      setSearchTime((prev) => prev + 1);
    }, 1000);

    // Initial search
    findMatch(user.anonymousId);

    return () => {
      clearInterval(timer);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  const handleAccept = () => {
    setStatus("connecting");
    setTimeout(() => {
      if (matchData) {
        router.push(`/chat/${matchData.matchId}`);
      }
    }, 1500);
  };

  const handleSkip = () => {
    if (!user) return;
    
    setStatus("searching");
    setMatchData(null);
    setSearchTime(0);

    // Give a short delay before restarting search to reset UI
    setTimeout(() => {
      findMatch(user.anonymousId);
    }, 500);
  };

  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-6 py-12 relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-gradient-to-b from-purple-900/20 to-transparent" />
        {status === "searching" && (
          <>
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 rounded-full border border-purple-500/20 animate-ping" style={{ animationDuration: '3s' }} />
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 rounded-full border border-purple-500/30 animate-ping" style={{ animationDuration: '2s' }} />
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-32 h-32 rounded-full border border-purple-500/40 animate-ping" style={{ animationDuration: '1s' }} />
          </>
        )}
        {status === "found" && (
          <div className="absolute inset-0 bg-gradient-to-b from-green-900/10 to-transparent" />
        )}
      </div>

      {/* Searching State */}
      {status === "searching" && (
        <div className="relative z-10 text-center animate-fade-in">
          <div className="w-24 h-24 rounded-full bg-gradient-to-br from-purple-500 to-cyan-500 mx-auto mb-8 animate-pulse-glow flex items-center justify-center">
            <svg className="w-12 h-12 text-white animate-spin" style={{ animationDuration: '3s' }} fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold mb-2">Finding your match...</h1>
          <p className="text-gray-400 mb-6">Looking for someone who shares your interests</p>
          <div className="text-sm text-purple-400">
            Searching for {searchTime}s
          </div>
          <button
            onClick={() => router.push("/home")}
            className="mt-8 text-sm text-gray-400 hover:text-white transition"
          >
            Cancel
          </button>
        </div>
      )}

      {/* Match Found State */}
      {status === "found" && matchData && (
        <div className="relative z-10 text-center animate-fade-in">
          <div className="mb-4 text-green-400 text-sm font-semibold flex items-center justify-center gap-2">
            <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            Match Found!
          </div>

          <div className="glass rounded-3xl p-8 max-w-sm mx-auto mb-8">
            {/* Avatar */}
            <div className="relative mb-6">
              <div className="w-24 h-24 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 mx-auto flex items-center justify-center text-4xl animate-float">
                {matchData.name.charAt(0)}
              </div>
              <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-green-500 text-white text-sm font-bold">
                {matchData.compatibility}% Match
              </div>
            </div>

            {/* Name */}
            <h2 className="text-2xl font-bold mb-2">{matchData.name}</h2>
            <p className="text-gray-400 text-sm mb-4">{matchData.style} vibe</p>

            {/* Interests */}
            <div className="flex flex-wrap justify-center gap-2 mb-6">
              {matchData.interests.map((interest) => (
                <span key={interest} className="chip">{interest}</span>
              ))}
            </div>

            {/* Compatibility Breakdown */}
            <div className="space-y-2 text-sm">
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Interests</span>
                <div className="flex items-center gap-2">
                  <div className="w-24 h-2 bg-gray-700 rounded-full overflow-hidden">
                    <div className="h-full bg-purple-500 rounded-full" style={{ width: '95%' }} />
                  </div>
                  <span className="text-purple-400">95%</span>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Vibe</span>
                <div className="flex items-center gap-2">
                  <div className="w-24 h-2 bg-gray-700 rounded-full overflow-hidden">
                    <div className="h-full bg-cyan-500 rounded-full" style={{ width: '88%' }} />
                  </div>
                  <span className="text-cyan-400">88%</span>
                </div>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-4 justify-center">
            <button
              onClick={handleSkip}
              className="btn-secondary px-8"
            >
              Skip
            </button>
            <button
              onClick={handleAccept}
              className="btn-primary px-8"
            >
              Start Chatting 💬
            </button>
          </div>
        </div>
      )}

      {/* Connecting State */}
      {status === "connecting" && (
        <div className="relative z-10 text-center animate-fade-in">
          <div className="w-20 h-20 rounded-full bg-gradient-to-br from-green-400 to-cyan-500 mx-auto mb-6 flex items-center justify-center animate-pulse">
            <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold mb-2">Connecting...</h1>
          <p className="text-gray-400">Starting your conversation</p>
        </div>
      )}
    </main>
  );
}
