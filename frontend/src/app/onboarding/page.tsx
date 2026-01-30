"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { userStore } from "@/lib/store";

const INTEREST_CATEGORIES = {
  "Gaming 🎮": ["Valorant", "League of Legends", "Minecraft", "Fortnite", "Chess", "Board Games"],
  "Music 🎵": ["Pop", "Hip Hop", "Rock", "Electronic", "K-Pop", "Indie"],
  "Entertainment 🎬": ["Movies", "Anime", "Netflix", "K-Drama", "Reality TV", "Documentaries"],
  "Sports ⚽": ["Football", "Basketball", "Tennis", "Gym", "Yoga", "Running"],
  "Lifestyle 📸": ["Travel", "Food", "Photography", "Fashion", "Pets", "Coffee"],
  "Tech 💻": ["Programming", "AI", "Startups", "Gadgets", "Crypto", "Science"],
};

const CONVERSATION_STYLES = [
  { id: "playful", label: "Playful 😄", desc: "Fun, jokes, memes" },
  { id: "casual", label: "Casual 💬", desc: "Easy-going chat" },
  { id: "deep", label: "Deep 🧠", desc: "Meaningful convos" },
  { id: "chill", label: "Chill 😌", desc: "Relaxed vibes" },
];

const ENERGY_LEVELS = [
  { id: "early_bird", label: "Early Bird 🌅", desc: "Morning person" },
  { id: "night_owl", label: "Night Owl 🦉", desc: "Late night vibes" },
  { id: "flexible", label: "Flexible 🕐", desc: "Anytime works" },
];

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [selectedInterests, setSelectedInterests] = useState<string[]>([]);
  const [conversationStyle, setConversationStyle] = useState("");
  const [energyLevel, setEnergyLevel] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const toggleInterest = (interest: string) => {
    setSelectedInterests((prev) =>
      prev.includes(interest)
        ? prev.filter((i) => i !== interest)
        : prev.length < 10
        ? [...prev, interest]
        : prev
    );
  };

  const canProceed = () => {
    if (step === 1) return selectedInterests.length >= 3;
    if (step === 2) return conversationStyle && energyLevel;
    if (step === 3) return displayName.length >= 2;
    return false;
  };

  const handleNext = async () => {
    if (step < 3) {
      setStep(step + 1);
    } else {
      // Submit to backend
      setIsSubmitting(true);
      setError(null);

      try {
        const result = await api.createProfile({
          interests: selectedInterests,
          conversation_style: conversationStyle,
          energy_level: energyLevel,
          languages: ["en"],
        });

        if (result.data) {
          // Save to local store
          userStore.setUser({
            anonymousId: result.data.anonymous_id,
            displayName,
            interests: selectedInterests,
            conversationStyle,
            energyLevel,
            reputationScore: 50,
          });
          router.push("/home");
        } else {
          setError(result.error || "Failed to create profile");
        }
      } catch (err) {
        setError("Network error. Please try again.");
      }

      setIsSubmitting(false);
    }
  };

  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-6 py-12 relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 -left-20 w-72 h-72 bg-purple-600/20 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 -right-20 w-72 h-72 bg-cyan-500/20 rounded-full blur-3xl" />
      </div>

      {/* Progress Bar */}
      <div className="absolute top-0 left-0 right-0 h-1 bg-gray-800">
        <div 
          className="h-full bg-gradient-to-r from-purple-500 to-cyan-500 transition-all duration-500"
          style={{ width: `${(step / 3) * 100}%` }}
        />
      </div>

      {/* Content */}
      <div className="relative z-10 w-full max-w-2xl">
        {/* Error Banner */}
        {error && (
          <div className="mb-6 p-4 rounded-xl bg-red-500/20 border border-red-500/50 text-red-300 text-sm animate-fade-in">
            {error}
          </div>
        )}

        {/* Step 1: Interests */}
        {step === 1 && (
          <div className="animate-fade-in">
            <div className="text-center mb-8">
              <span className="text-purple-400 text-sm font-mono">STEP 1 OF 3</span>
              <h1 className="text-3xl font-bold mt-2">What are you into?</h1>
              <p className="text-gray-400 mt-2">
                Pick 3-10 interests. This helps us find your matches.
              </p>
            </div>

            <div className="space-y-6">
              {Object.entries(INTEREST_CATEGORIES).map(([category, interests]) => (
                <div key={category}>
                  <h3 className="text-sm text-gray-400 mb-3">{category}</h3>
                  <div className="flex flex-wrap gap-2">
                    {interests.map((interest) => (
                      <button
                        key={interest}
                        onClick={() => toggleInterest(interest)}
                        className={`chip ${
                          selectedInterests.includes(interest) ? "selected" : ""
                        }`}
                      >
                        {interest}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 text-center text-sm text-gray-400">
              Selected: {selectedInterests.length}/10
            </div>
          </div>
        )}

        {/* Step 2: Vibe */}
        {step === 2 && (
          <div className="animate-fade-in">
            <div className="text-center mb-8">
              <span className="text-purple-400 text-sm font-mono">STEP 2 OF 3</span>
              <h1 className="text-3xl font-bold mt-2">What&apos;s your vibe?</h1>
              <p className="text-gray-400 mt-2">
                Help us match you with people who chat like you.
              </p>
            </div>

            <div className="space-y-8">
              <div>
                <h3 className="text-sm text-gray-400 mb-4">Conversation Style</h3>
                <div className="grid grid-cols-2 gap-4">
                  {CONVERSATION_STYLES.map((style) => (
                    <button
                      key={style.id}
                      onClick={() => setConversationStyle(style.id)}
                      className={`card text-left transition-all ${
                        conversationStyle === style.id
                          ? "border-purple-500 bg-purple-500/10"
                          : "hover:border-purple-500/50"
                      }`}
                    >
                      <span className="text-lg font-semibold">{style.label}</span>
                      <p className="text-sm text-gray-400 mt-1">{style.desc}</p>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="text-sm text-gray-400 mb-4">Energy Level</h3>
                <div className="grid grid-cols-3 gap-4">
                  {ENERGY_LEVELS.map((level) => (
                    <button
                      key={level.id}
                      onClick={() => setEnergyLevel(level.id)}
                      className={`card text-center transition-all ${
                        energyLevel === level.id
                          ? "border-cyan-500 bg-cyan-500/10"
                          : "hover:border-cyan-500/50"
                      }`}
                    >
                      <span className="text-lg font-semibold">{level.label}</span>
                      <p className="text-sm text-gray-400 mt-1">{level.desc}</p>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Step 3: Display Name */}
        {step === 3 && (
          <div className="animate-fade-in">
            <div className="text-center mb-8">
              <span className="text-purple-400 text-sm font-mono">STEP 3 OF 3</span>
              <h1 className="text-3xl font-bold mt-2">Choose a display name</h1>
              <p className="text-gray-400 mt-2">
                This is how others will see you. Keep it fun!
              </p>
            </div>

            <div className="max-w-sm mx-auto">
              <input
                type="text"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                placeholder="e.g., NightOwlGamer"
                maxLength={20}
                className="w-full px-6 py-4 rounded-xl bg-[var(--surface)] border border-purple-500/20 focus:border-purple-500 focus:outline-none text-center text-lg transition-all"
              />
              <p className="text-center text-sm text-gray-400 mt-2">
                {displayName.length}/20 characters
              </p>
            </div>

            <div className="mt-12 text-center">
              <div className="glass inline-block rounded-2xl p-6">
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 rounded-full bg-gradient-to-br from-purple-500 to-cyan-500 flex items-center justify-center text-2xl">
                    {displayName.charAt(0).toUpperCase() || "?"}
                  </div>
                  <div className="text-left">
                    <p className="font-semibold">{displayName || "Your Name"}</p>
                    <p className="text-sm text-gray-400">
                      {selectedInterests.slice(0, 3).join(", ")}
                    </p>
                    <p className="text-sm text-purple-400">
                      {CONVERSATION_STYLES.find((s) => s.id === conversationStyle)?.label || ""}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Navigation */}
        <div className="flex justify-between mt-12">
          {step > 1 && (
            <button
              onClick={() => setStep(step - 1)}
              className="btn-secondary"
              disabled={isSubmitting}
            >
              Back
            </button>
          )}
          <button
            onClick={handleNext}
            disabled={!canProceed() || isSubmitting}
            className={`btn-primary ml-auto ${
              !canProceed() || isSubmitting ? "opacity-50 cursor-not-allowed" : ""
            }`}
          >
            {isSubmitting ? (
              <span className="flex items-center gap-2">
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Creating...
              </span>
            ) : step === 3 ? (
              "Start Matching"
            ) : (
              "Continue"
            )}
          </button>
        </div>
      </div>
    </main>
  );
}
