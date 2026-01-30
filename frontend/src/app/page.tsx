"use client";

import Link from "next/link";
import { useState, useEffect } from "react";

const INTERESTS = [
  "Gaming 🎮", "Music 🎵", "Movies 🎬", "Sports ⚽", "Travel ✈️",
  "Food 🍕", "Art 🎨", "Tech 💻", "Books 📚", "Photography 📷"
];

export default function LandingPage() {
  const [currentInterest, setCurrentInterest] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentInterest((prev) => (prev + 1) % INTERESTS.length);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <main className="min-h-screen relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 -left-20 w-96 h-96 bg-purple-600/20 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 -right-20 w-96 h-96 bg-cyan-500/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-purple-500/10 rounded-full blur-3xl" />
      </div>

      {/* Navigation */}
      <nav className="relative z-10 flex items-center justify-between px-8 py-6 max-w-7xl mx-auto">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-cyan-400 flex items-center justify-center">
            <span className="text-white text-xl font-bold">M</span>
          </div>
          <span className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">
            Mingle
          </span>
        </div>
        <div className="flex items-center gap-4">
          <Link href="/onboarding" className="btn-primary text-sm">
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative z-10 flex flex-col items-center justify-center text-center px-6 pt-20 pb-32 max-w-5xl mx-auto">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-purple-500/10 border border-purple-500/20 mb-8 animate-fade-in">
          <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
          <span className="text-sm text-purple-300">500+ people matching right now</span>
        </div>

        <h1 className="text-5xl md:text-7xl font-bold mb-6 animate-fade-in" style={{ animationDelay: '0.1s' }}>
          Connect through{" "}
          <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400 bg-clip-text text-transparent">
            interests
          </span>
          <br />not appearances
        </h1>

        <p className="text-xl text-gray-400 max-w-2xl mb-8 animate-fade-in" style={{ animationDelay: '0.2s' }}>
          Match with people who love{" "}
          <span className="text-purple-400 font-semibold transition-all duration-500">
            {INTERESTS[currentInterest]}
          </span>{" "}
          just like you. No photos, no judgment—just real conversations.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 mb-16 animate-fade-in" style={{ animationDelay: '0.3s' }}>
          <Link 
            href="/onboarding" 
            className="btn-primary text-lg px-8 py-4 animate-pulse-glow"
          >
            Start Matching Free
          </Link>
          <Link href="#how-it-works" className="btn-secondary text-lg px-8 py-4">
            How It Works
          </Link>
        </div>

        {/* Preview Cards */}
        <div className="flex gap-4 flex-wrap justify-center animate-fade-in" style={{ animationDelay: '0.4s' }}>
          <PreviewCard
            compatibility={87}
            interests={["Gaming", "Anime"]}
            style="Playful"
            delay={0}
          />
          <PreviewCard
            compatibility={92}
            interests={["Music", "Travel"]}
            style="Chill"
            delay={0.2}
          />
          <PreviewCard
            compatibility={78}
            interests={["Tech", "Movies"]}
            style="Deep"
            delay={0.4}
          />
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="relative z-10 py-24 px-6 max-w-6xl mx-auto">
        <h2 className="text-4xl font-bold text-center mb-4">
          How <span className="text-purple-400">Mingle</span> Works
        </h2>
        <p className="text-gray-400 text-center mb-16 max-w-xl mx-auto">
          Three simple steps to meaningful connections
        </p>

        <div className="grid md:grid-cols-3 gap-8">
          <StepCard
            number={1}
            title="Share Your Interests"
            description="Pick topics you love, choose your vibe, and set your comfort level. No photos required."
            icon="🎯"
          />
          <StepCard
            number={2}
            title="Get Matched"
            description="Our algorithm finds people who share your passions and conversation style."
            icon="🔗"
          />
          <StepCard
            number={3}
            title="Chat & Connect"
            description="Break the ice with games, chat anonymously, and reveal yourself when you're ready."
            icon="💬"
          />
        </div>
      </section>

      {/* Features */}
      <section className="relative z-10 py-24 px-6 max-w-6xl mx-auto">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <h2 className="text-4xl font-bold mb-6">
              Privacy-first, <br />
              <span className="text-cyan-400">always.</span>
            </h2>
            <ul className="space-y-4">
              <FeatureItem icon="🔒" text="Anonymous profiles—share only what you want" />
              <FeatureItem icon="🎭" text="Camera blur until you're comfortable" />
              <FeatureItem icon="⏱️" text="Ephemeral messages that disappear" />
              <FeatureItem icon="🛡️" text="AI moderation blocks toxic behavior" />
            </ul>
          </div>
          <div className="glass rounded-2xl p-8 animate-float">
            <div className="flex items-center gap-4 mb-6">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-2xl">
                🎮
              </div>
              <div>
                <p className="text-sm text-gray-400">Matched with</p>
                <p className="font-semibold">NightOwlGamer</p>
                <p className="text-sm text-purple-400">92% Compatible</p>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex gap-2">
                <span className="chip text-xs">Gaming</span>
                <span className="chip text-xs">Anime</span>
                <span className="chip text-xs">Music</span>
              </div>
              <p className="text-sm text-gray-400 mt-4">
                💬 "Hey! Would you rather play a new game nobody's heard of or replay your all-time favorite?"
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="relative z-10 py-24 px-6 text-center">
        <div className="glass max-w-3xl mx-auto rounded-3xl p-12">
          <h2 className="text-4xl font-bold mb-4">Ready to find your people?</h2>
          <p className="text-gray-400 mb-8">
            Join thousands connecting through shared passions every day.
          </p>
          <Link href="/onboarding" className="btn-primary text-lg px-10 py-4">
            Get Started — It&apos;s Free
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-white/5 py-8 px-6">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-cyan-400 flex items-center justify-center">
              <span className="text-white text-sm font-bold">M</span>
            </div>
            <span className="font-semibold">Mingle</span>
          </div>
          <div className="flex gap-6 text-sm text-gray-400">
            <Link href="/privacy" className="hover:text-purple-400 transition">Privacy</Link>
            <Link href="/terms" className="hover:text-purple-400 transition">Terms</Link>
            <Link href="/support" className="hover:text-purple-400 transition">Support</Link>
          </div>
          <p className="text-sm text-gray-500">© 2025 Mingle. Made with 💜</p>
        </div>
      </footer>
    </main>
  );
}

// Components
function PreviewCard({ 
  compatibility, 
  interests, 
  style, 
  delay 
}: { 
  compatibility: number; 
  interests: string[]; 
  style: string;
  delay: number;
}) {
  return (
    <div 
      className="glass rounded-2xl p-6 w-64 text-left animate-fade-in"
      style={{ animationDelay: `${delay}s` }}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-600 to-cyan-500 opacity-60" />
        <span className="text-2xl font-bold text-purple-400">{compatibility}%</span>
      </div>
      <div className="flex gap-2 mb-3">
        {interests.map((i) => (
          <span key={i} className="chip text-xs">{i}</span>
        ))}
      </div>
      <p className="text-sm text-gray-400">
        <span className="text-gray-300">Vibe:</span> {style}
      </p>
    </div>
  );
}

function StepCard({ 
  number, 
  title, 
  description, 
  icon 
}: { 
  number: number; 
  title: string; 
  description: string; 
  icon: string;
}) {
  return (
    <div className="card text-center group hover:border-purple-500/50 transition-all duration-300">
      <div className="w-16 h-16 rounded-2xl bg-purple-500/10 flex items-center justify-center text-3xl mx-auto mb-4 group-hover:scale-110 transition">
        {icon}
      </div>
      <div className="text-sm text-purple-400 font-mono mb-2">STEP {number}</div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-gray-400 text-sm">{description}</p>
    </div>
  );
}

function FeatureItem({ icon, text }: { icon: string; text: string }) {
  return (
    <li className="flex items-center gap-3">
      <span className="text-xl">{icon}</span>
      <span className="text-gray-300">{text}</span>
    </li>
  );
}
