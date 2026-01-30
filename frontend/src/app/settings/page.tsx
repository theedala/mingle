"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { userStore, matchesStore } from "@/lib/store";
import { api } from "@/lib/api";

interface BlockedUser {
  anonymousId: string;
  blockedAt: string;
}

export default function SettingsPage() {
  const router = useRouter();
  const [user, setUser] = useState<{
    displayName: string;
    interests: string[];
    conversationStyle: string;
    energyLevel: string;
  } | null>(null);
  const [blockedUsers, setBlockedUsers] = useState<BlockedUser[]>([]);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [activeTab, setActiveTab] = useState<"profile" | "blocked" | "account">("profile");

  useEffect(() => {
    const stored = userStore.getUser();
    if (stored) {
      setUser({
        displayName: stored.displayName,
        interests: stored.interests,
        conversationStyle: stored.conversationStyle,
        energyLevel: stored.energyLevel,
      });
    }
  }, []);

  const handleLogout = () => {
    userStore.clearUser();
    matchesStore.clearMatches();
    router.push("/");
  };

  const handleDeleteAccount = () => {
    // In real app, call API to delete account
    userStore.clearUser();
    matchesStore.clearMatches();
    router.push("/");
  };

  const handleUnblock = async (blockedId: string) => {
    const stored = userStore.getUser();
    if (stored) {
      await api.unblockUser(stored.anonymousId, blockedId);
      setBlockedUsers((prev) => prev.filter((u) => u.anonymousId !== blockedId));
    }
  };

  const STYLE_LABELS: Record<string, string> = {
    playful: "Playful 😄",
    casual: "Casual 💬",
    deep: "Deep 🧠",
    chill: "Chill 😌",
  };

  const ENERGY_LABELS: Record<string, string> = {
    early_bird: "Early Bird 🌅",
    night_owl: "Night Owl 🦉",
    flexible: "Flexible 🕐",
  };

  if (!user) {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-400 mb-4">Not logged in</p>
          <Link href="/" className="btn-primary">Go to Home</Link>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[var(--background)]">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-white/5 bg-[var(--surface)]">
        <div className="flex items-center gap-3">
          <Link href="/home" className="p-2 -ml-2 rounded-full hover:bg-white/5">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </Link>
          <h1 className="text-xl font-bold">Settings</h1>
        </div>
      </header>

      <div className="max-w-2xl mx-auto px-6 py-8">
        {/* Tabs */}
        <div className="flex gap-2 mb-8">
          {(["profile", "blocked", "account"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                activeTab === tab
                  ? "bg-purple-500 text-white"
                  : "bg-[var(--surface)] text-gray-400 hover:text-white"
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {/* Profile Tab */}
        {activeTab === "profile" && (
          <div className="space-y-6 animate-fade-in">
            {/* Profile Card */}
            <div className="card">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-20 h-20 rounded-full bg-gradient-to-br from-purple-500 to-cyan-500 flex items-center justify-center text-3xl">
                  {user.displayName.charAt(0).toUpperCase()}
                </div>
                <div>
                  <h2 className="text-xl font-bold">{user.displayName}</h2>
                  <p className="text-purple-400">{STYLE_LABELS[user.conversationStyle]}</p>
                  <p className="text-sm text-gray-400">{ENERGY_LABELS[user.energyLevel]}</p>
                </div>
              </div>

              <div>
                <h3 className="text-sm text-gray-400 mb-3">Your Interests</h3>
                <div className="flex flex-wrap gap-2">
                  {user.interests.map((interest) => (
                    <span key={interest} className="chip">{interest}</span>
                  ))}
                </div>
              </div>
            </div>

            {/* Edit Profile */}
            <div className="card">
              <h3 className="font-semibold mb-4">Edit Profile</h3>
              <p className="text-gray-400 text-sm mb-4">
                Want to update your interests or vibe? Re-do the onboarding!
              </p>
              <Link href="/onboarding" className="btn-secondary inline-block">
                Update Profile
              </Link>
            </div>
          </div>
        )}

        {/* Blocked Tab */}
        {activeTab === "blocked" && (
          <div className="space-y-4 animate-fade-in">
            <div className="card">
              <h3 className="font-semibold mb-4">Blocked Users</h3>
              
              {blockedUsers.length === 0 ? (
                <div className="text-center py-8">
                  <span className="text-4xl mb-4 block">🕊️</span>
                  <p className="text-gray-400">You haven&apos;t blocked anyone</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {blockedUsers.map((blocked) => (
                    <div
                      key={blocked.anonymousId}
                      className="flex items-center justify-between p-3 rounded-xl bg-[var(--surface-light)]"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-gray-700 flex items-center justify-center">
                          🚫
                        </div>
                        <div>
                          <p className="font-medium">User {blocked.anonymousId.slice(0, 8)}</p>
                          <p className="text-xs text-gray-400">
                            Blocked {new Date(blocked.blockedAt).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={() => handleUnblock(blocked.anonymousId)}
                        className="text-sm text-purple-400 hover:text-purple-300"
                      >
                        Unblock
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Account Tab */}
        {activeTab === "account" && (
          <div className="space-y-6 animate-fade-in">
            {/* Privacy Info */}
            <div className="card">
              <h3 className="font-semibold mb-4">🔒 Your Privacy</h3>
              <ul className="space-y-3 text-sm text-gray-300">
                <li className="flex items-start gap-3">
                  <span className="text-green-400">✓</span>
                  Your profile is anonymous—no email or phone required
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-green-400">✓</span>
                  Messages are ephemeral and auto-delete
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-green-400">✓</span>
                  Video starts blurred until you reveal
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-green-400">✓</span>
                  We never sell your data
                </li>
              </ul>
            </div>

            {/* Logout */}
            <div className="card">
              <h3 className="font-semibold mb-4">Session</h3>
              <button
                onClick={handleLogout}
                className="btn-secondary w-full"
              >
                Log Out
              </button>
            </div>

            {/* Delete Account */}
            <div className="card border-red-500/20">
              <h3 className="font-semibold text-red-400 mb-4">Danger Zone</h3>
              <p className="text-sm text-gray-400 mb-4">
                Delete your account and all associated data. This cannot be undone.
              </p>
              
              {!showDeleteConfirm ? (
                <button
                  onClick={() => setShowDeleteConfirm(true)}
                  className="text-sm text-red-400 hover:text-red-300"
                >
                  Delete my account
                </button>
              ) : (
                <div className="flex gap-3">
                  <button
                    onClick={handleDeleteAccount}
                    className="px-4 py-2 rounded-lg bg-red-500 hover:bg-red-600 text-white text-sm"
                  >
                    Yes, delete everything
                  </button>
                  <button
                    onClick={() => setShowDeleteConfirm(false)}
                    className="px-4 py-2 rounded-lg bg-gray-700 text-gray-300 text-sm"
                  >
                    Cancel
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
