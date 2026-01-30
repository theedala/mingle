"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { userStore, matchesStore, ActiveMatch } from "@/lib/store";
import { api } from "@/lib/api";

const MOODS = [
  { emoji: "😊", label: "Happy" },
  { emoji: "😌", label: "Relaxed" },
  { emoji: "🤔", label: "Thoughtful" },
  { emoji: "🎉", label: "Excited" },
  { emoji: "😴", label: "Tired" },
  { emoji: "🔥", label: "Energetic" },
];

export default function HomePage() {
  const router = useRouter();
  const [user, setUser] = useState<{
    anonymousId: string;
    displayName: string;
    currentMood?: string;
    reputationScore: number;
  } | null>(null);
  const [activeMatches, setActiveMatches] = useState<ActiveMatch[]>([]);
  const [selectedMood, setSelectedMood] = useState<string | null>(null);
  const [isSearching, setIsSearching] = useState(false);

  useEffect(() => {
    const stored = userStore.getUser();
    if (!stored) {
      router.push("/onboarding");
      return;
    }
    setUser({
      anonymousId: stored.anonymousId,
      displayName: stored.displayName,
      currentMood: stored.currentMood,
      reputationScore: stored.reputationScore,
    });
    setSelectedMood(stored.currentMood || null);
    setActiveMatches(matchesStore.getMatches());
  }, [router]);

  const handleMoodSelect = async (mood: string) => {
    setSelectedMood(mood);
    if (user) {
      await api.updateMood(user.anonymousId, mood);
      userStore.updateUser({ currentMood: mood });
    }
  };

  const handleFindMatch = () => {
    setIsSearching(true);
    setTimeout(() => {
      router.push("/matching");
    }, 1000);
  };

  if (!user) {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full" />
      </main>
    );
  }

  return (
    <main className="min-h-screen relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 right-0 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl" />
      </div>

      {/* Header */}
      <header className="relative z-10 flex items-center justify-between px-6 py-4 border-b border-white/5">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-cyan-400 flex items-center justify-center">
            <span className="text-white text-sm font-bold">M</span>
          </div>
          <span className="text-lg font-bold">Mingle</span>
        </div>
        <Link href="/settings" className="p-2 rounded-full hover:bg-white/5 transition">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </Link>
      </header>

      <div className="relative z-10 max-w-4xl mx-auto px-6 py-8">
        {/* Greeting */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">
            Hey, <span className="text-purple-400">{user.displayName}</span> 👋
          </h1>
          <p className="text-gray-400">Ready to find someone new today?</p>
        </div>

        {/* Mood Selector */}
        <div className="glass rounded-2xl p-6 mb-8">
          <h2 className="text-sm text-gray-400 mb-4">How are you feeling today?</h2>
          <div className="flex flex-wrap gap-3">
            {MOODS.map((mood) => (
              <button
                key={mood.label}
                onClick={() => handleMoodSelect(mood.label)}
                className={`flex items-center gap-2 px-4 py-2 rounded-full transition-all ${
                  selectedMood === mood.label
                    ? "bg-purple-500 text-white"
                    : "bg-[var(--surface-light)] hover:bg-[var(--surface-light)]/80"
                }`}
              >
                <span className="text-xl">{mood.emoji}</span>
                <span className="text-sm">{mood.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Find Match Button */}
        <div className="text-center mb-12">
          <button
            onClick={handleFindMatch}
            disabled={isSearching}
            className={`btn-primary text-xl px-12 py-5 ${
              isSearching ? "animate-pulse-glow" : ""
            }`}
          >
            {isSearching ? (
              <span className="flex items-center gap-3">
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Finding your match...
              </span>
            ) : (
              "🔗 Find a Match"
            )}
          </button>
          <p className="text-sm text-gray-400 mt-3">
            {selectedMood 
              ? `Looking for ${selectedMood.toLowerCase()} vibes`
              : "Select your mood for better matches"
            }
          </p>
        </div>

        {/* Active Matches */}
        {activeMatches.length > 0 && (
          <div>
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              Active Conversations
            </h2>
            <div className="space-y-3">
              {activeMatches.map((match) => (
                <Link
                  key={match.matchId}
                  href={`/chat/${match.matchId}`}
                  className="card flex items-center gap-4 hover:border-purple-500/50 transition-all"
                >
                  <div className="w-14 h-14 rounded-full bg-gradient-to-br from-purple-500 to-cyan-500 flex items-center justify-center text-xl">
                    {match.partnerName.charAt(0)}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold">{match.partnerName}</span>
                      <span className="text-sm text-purple-400">{match.compatibility}%</span>
                    </div>
                    {match.lastMessage && (
                      <p className="text-sm text-gray-400 truncate">{match.lastMessage}</p>
                    )}
                    <div className="flex gap-2 mt-1">
                      {match.partnerInterests.slice(0, 3).map((i) => (
                        <span key={i} className="text-xs text-cyan-400">{i}</span>
                      ))}
                    </div>
                  </div>
                  {match.unreadCount > 0 && (
                    <span className="w-6 h-6 rounded-full bg-purple-500 text-xs flex items-center justify-center">
                      {match.unreadCount}
                    </span>
                  )}
                  <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {activeMatches.length === 0 && (
          <div className="card text-center py-12">
            <span className="text-5xl mb-4 block">🔍</span>
            <h3 className="text-lg font-semibold mb-2">No active conversations</h3>
            <p className="text-gray-400 text-sm">
              Hit that Find a Match button to start chatting!
            </p>
          </div>
        )}

        {/* Quick Stats */}
        <div className="grid grid-cols-3 gap-4 mt-8">
          <div className="card text-center">
            <span className="text-2xl font-bold text-purple-400">{activeMatches.length}</span>
            <p className="text-xs text-gray-400 mt-1">Active Matches</p>
          </div>
          <div className="card text-center">
            <span className="text-2xl font-bold text-cyan-400">{user.reputationScore}</span>
            <p className="text-xs text-gray-400 mt-1">Rep Score</p>
          </div>
          <div className="card text-center">
            <span className="text-2xl font-bold text-green-400">100%</span>
            <p className="text-xs text-gray-400 mt-1">Response Rate</p>
          </div>
        </div>
      </div>
    </main>
  );
}
