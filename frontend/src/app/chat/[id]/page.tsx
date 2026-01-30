"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";

interface Message {
  id: string;
  sender: "me" | "partner";
  text: string;
  timestamp: Date;
  reactions?: string[];
}

const ICE_BREAKERS = [
  "Would you rather be able to fly or be invisible?",
  "What's the best trip you've ever taken?",
  "If you could learn any skill instantly, what would it be?",
  "What show are you currently binge-watching?",
];

export default function ChatPage() {
  const params = useParams();
  const matchId = params.id as string;
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      sender: "partner",
      text: "Hey! Your profile looks interesting 😊",
      timestamp: new Date(Date.now() - 60000),
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [showIceBreakers, setShowIceBreakers] = useState(false);
  const [showReactions, setShowReactions] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const partnerName = "NightOwlGamer";
  const compatibility = 92;

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Simulate partner typing
  useEffect(() => {
    if (messages.length === 1) {
      const timer = setTimeout(() => {
        setIsTyping(true);
        setTimeout(() => {
          setIsTyping(false);
          setMessages((prev) => [
            ...prev,
            {
              id: "2",
              sender: "partner",
              text: "What games are you into?",
              timestamp: new Date(),
            },
          ]);
        }, 2000);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [messages.length]);

  const sendMessage = () => {
    if (!inputValue.trim()) return;

    const newMessage: Message = {
      id: Date.now().toString(),
      sender: "me",
      text: inputValue,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, newMessage]);
    setInputValue("");

    // Simulate partner response
    setTimeout(() => {
      setIsTyping(true);
      setTimeout(() => {
        setIsTyping(false);
        setMessages((prev) => [
          ...prev,
          {
            id: (Date.now() + 1).toString(),
            sender: "partner",
            text: "That's awesome! I love that too 🎮",
            timestamp: new Date(),
          },
        ]);
      }, 1500 + Math.random() * 1500);
    }, 1000);
  };

  const sendIceBreaker = (prompt: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      sender: "me",
      text: `🎯 ${prompt}`,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, newMessage]);
    setShowIceBreakers(false);
  };

  const addReaction = (messageId: string, emoji: string) => {
    setMessages((prev) =>
      prev.map((m) =>
        m.id === messageId
          ? { ...m, reactions: [...(m.reactions || []), emoji] }
          : m
      )
    );
    setShowReactions(null);
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  return (
    <main className="min-h-screen flex flex-col bg-[var(--background)]">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-3 border-b border-white/5 bg-[var(--surface)]">
        <div className="flex items-center gap-3">
          <Link href="/home" className="p-2 -ml-2 rounded-full hover:bg-white/5">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </Link>
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-lg">
            {partnerName.charAt(0)}
          </div>
          <div>
            <h1 className="font-semibold">{partnerName}</h1>
            <p className="text-xs text-purple-400">{compatibility}% Match</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Link
            href={`/video/${matchId}`}
            className="p-2 rounded-full bg-purple-500/10 hover:bg-purple-500/20 transition"
          >
            <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          </Link>
          <button className="p-2 rounded-full hover:bg-white/5">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
            </svg>
          </button>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.sender === "me" ? "justify-end" : "justify-start"}`}
          >
            <div className="relative group max-w-[80%]">
              <div
                className={`px-4 py-2 rounded-2xl ${
                  message.sender === "me"
                    ? "bg-purple-500 text-white rounded-br-md"
                    : "bg-[var(--surface)] text-white rounded-bl-md"
                }`}
              >
                <p>{message.text}</p>
                <p className={`text-xs mt-1 ${
                  message.sender === "me" ? "text-purple-200" : "text-gray-400"
                }`}>
                  {formatTime(message.timestamp)}
                </p>
              </div>

              {/* Reactions */}
              {message.reactions && message.reactions.length > 0 && (
                <div className={`absolute -bottom-3 ${
                  message.sender === "me" ? "right-2" : "left-2"
                } bg-[var(--surface-light)] rounded-full px-2 py-0.5 text-sm flex gap-1`}>
                  {message.reactions.map((r, i) => (
                    <span key={i}>{r}</span>
                  ))}
                </div>
              )}

              {/* Reaction picker */}
              <button
                onClick={() => setShowReactions(showReactions === message.id ? null : message.id)}
                className={`absolute top-1/2 -translate-y-1/2 ${
                  message.sender === "me" ? "-left-8" : "-right-8"
                } opacity-0 group-hover:opacity-100 transition p-1 rounded-full hover:bg-white/10`}
              >
                😊
              </button>

              {showReactions === message.id && (
                <div className={`absolute top-0 ${
                  message.sender === "me" ? "-left-28" : "-right-28"
                } bg-[var(--surface)] rounded-full px-2 py-1 flex gap-1 shadow-lg`}>
                  {["❤️", "😂", "👍", "🔥", "😮"].map((emoji) => (
                    <button
                      key={emoji}
                      onClick={() => addReaction(message.id, emoji)}
                      className="hover:scale-125 transition"
                    >
                      {emoji}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Typing indicator */}
        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-[var(--surface)] px-4 py-3 rounded-2xl rounded-bl-md">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Ice Breakers Modal */}
      {showIceBreakers && (
        <div className="absolute bottom-24 left-4 right-4 glass rounded-2xl p-4 animate-fade-in">
          <h3 className="text-sm text-gray-400 mb-3">🎯 Ice Breakers</h3>
          <div className="space-y-2">
            {ICE_BREAKERS.map((prompt, i) => (
              <button
                key={i}
                onClick={() => sendIceBreaker(prompt)}
                className="w-full text-left p-3 rounded-xl bg-[var(--surface)] hover:bg-[var(--surface-light)] transition text-sm"
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="p-4 border-t border-white/5 bg-[var(--surface)]">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowIceBreakers(!showIceBreakers)}
            className={`p-3 rounded-full transition ${
              showIceBreakers
                ? "bg-purple-500 text-white"
                : "bg-[var(--surface-light)] hover:bg-purple-500/20"
            }`}
          >
            🎯
          </button>
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Type a message..."
            className="flex-1 px-4 py-3 rounded-full bg-[var(--surface-light)] focus:outline-none focus:ring-2 focus:ring-purple-500/50"
          />
          <button
            onClick={sendMessage}
            disabled={!inputValue.trim()}
            className={`p-3 rounded-full transition ${
              inputValue.trim()
                ? "bg-purple-500 hover:bg-purple-600"
                : "bg-gray-700 opacity-50"
            }`}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
      </div>
    </main>
  );
}
