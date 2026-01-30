"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";

interface PeerConnection {
  pc: RTCPeerConnection | null;
  stream: MediaStream | null;
}

export default function VideoPage() {
  const router = useRouter();
  const params = useParams();
  const matchId = params.id as string;
  
  const [localStream, setLocalStream] = useState<MediaStream | null>(null);
  const [remoteStream, setRemoteStream] = useState<MediaStream | null>(null);
  const [blurEnabled, setBlurEnabled] = useState(true);
  const [isMuted, setIsMuted] = useState(false);
  const [isVideoOff, setIsVideoOff] = useState(false);
  const [connectionState, setConnectionState] = useState<"connecting" | "connected" | "failed">("connecting");
  const [partnerBlurred, setPartnerBlurred] = useState(true);
  
  const localVideoRef = useRef<HTMLVideoElement>(null);
  const remoteVideoRef = useRef<HTMLVideoElement>(null);
  const peerConnectionRef = useRef<RTCPeerConnection | null>(null);

  const partnerName = "NightOwlGamer";

  // Initialize local media
  useEffect(() => {
    const initMedia = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: true,
        });
        setLocalStream(stream);
        if (localVideoRef.current) {
          localVideoRef.current.srcObject = stream;
        }
        
        // Simulate connection after getting media
        setTimeout(() => {
          setConnectionState("connected");
          // Simulate remote stream (in real app, this comes from WebRTC)
          setRemoteStream(stream); // Using same stream for demo
        }, 2000);
      } catch (err) {
        console.error("Failed to get media:", err);
        setConnectionState("failed");
      }
    };

    initMedia();

    return () => {
      localStream?.getTracks().forEach((track) => track.stop());
      peerConnectionRef.current?.close();
    };
  }, []);

  // Update remote video when stream changes
  useEffect(() => {
    if (remoteVideoRef.current && remoteStream) {
      remoteVideoRef.current.srcObject = remoteStream;
    }
  }, [remoteStream]);

  const toggleMute = () => {
    if (localStream) {
      localStream.getAudioTracks().forEach((track) => {
        track.enabled = !track.enabled;
      });
      setIsMuted(!isMuted);
    }
  };

  const toggleVideo = () => {
    if (localStream) {
      localStream.getVideoTracks().forEach((track) => {
        track.enabled = !track.enabled;
      });
      setIsVideoOff(!isVideoOff);
    }
  };

  const toggleBlur = () => {
    setBlurEnabled(!blurEnabled);
    // In real app, send blur state to partner via WebSocket
  };

  const endCall = () => {
    localStream?.getTracks().forEach((track) => track.stop());
    peerConnectionRef.current?.close();
    router.push(`/chat/${matchId}`);
  };

  return (
    <main className="h-screen bg-black flex flex-col">
      {/* Main Video (Partner) */}
      <div className="flex-1 relative overflow-hidden">
        {connectionState === "connecting" && (
          <div className="absolute inset-0 flex items-center justify-center bg-[var(--background)]">
            <div className="text-center">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-purple-500 to-cyan-500 mx-auto mb-4 animate-pulse flex items-center justify-center text-3xl">
                {partnerName.charAt(0)}
              </div>
              <p className="text-white mb-2">Connecting with {partnerName}...</p>
              <div className="flex justify-center gap-1">
                <span className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}

        {connectionState === "failed" && (
          <div className="absolute inset-0 flex items-center justify-center bg-[var(--background)]">
            <div className="text-center">
              <div className="text-6xl mb-4">📵</div>
              <p className="text-red-400 mb-4">Failed to connect video</p>
              <button onClick={() => router.back()} className="btn-secondary">
                Go Back
              </button>
            </div>
          </div>
        )}

        {connectionState === "connected" && (
          <>
            <video
              ref={remoteVideoRef}
              autoPlay
              playsInline
              className={`w-full h-full object-cover ${partnerBlurred ? 'blur-xl' : ''} transition-all duration-500`}
            />

            {/* Partner Blur Indicator */}
            {partnerBlurred && (
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                <div className="text-center">
                  <div className="w-24 h-24 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 mx-auto mb-4 flex items-center justify-center text-4xl">
                    {partnerName.charAt(0)}
                  </div>
                  <p className="text-white text-lg font-semibold">{partnerName}</p>
                  <p className="text-gray-400 text-sm">Camera is blurred</p>
                </div>
              </div>
            )}

            {/* Partner Name Badge */}
            <div className="absolute top-4 left-4 glass rounded-full px-4 py-2 flex items-center gap-2">
              <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              <span className="text-sm font-medium">{partnerName}</span>
            </div>
          </>
        )}

        {/* Local Video (Self) */}
        <div className="absolute bottom-24 right-4 w-32 md:w-48 aspect-video rounded-xl overflow-hidden shadow-2xl border-2 border-purple-500/50">
          <video
            ref={localVideoRef}
            autoPlay
            playsInline
            muted
            className={`w-full h-full object-cover ${blurEnabled ? 'blur-lg' : ''} transition-all duration-500`}
          />
          {blurEnabled && (
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-2xl">🙈</span>
            </div>
          )}
          {isVideoOff && (
            <div className="absolute inset-0 bg-gray-900 flex items-center justify-center">
              <span className="text-2xl">📷</span>
            </div>
          )}
        </div>
      </div>

      {/* Controls */}
      <div className="bg-[var(--surface)] px-6 py-4">
        <div className="flex items-center justify-center gap-4">
          {/* Mute */}
          <button
            onClick={toggleMute}
            className={`p-4 rounded-full transition-all ${
              isMuted
                ? "bg-red-500 hover:bg-red-600"
                : "bg-[var(--surface-light)] hover:bg-gray-700"
            }`}
          >
            {isMuted ? (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2" />
              </svg>
            ) : (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
            )}
          </button>

          {/* Video Toggle */}
          <button
            onClick={toggleVideo}
            className={`p-4 rounded-full transition-all ${
              isVideoOff
                ? "bg-red-500 hover:bg-red-600"
                : "bg-[var(--surface-light)] hover:bg-gray-700"
            }`}
          >
            {isVideoOff ? (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3l18 18" />
              </svg>
            ) : (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            )}
          </button>

          {/* Blur Toggle */}
          <button
            onClick={toggleBlur}
            className={`p-4 rounded-full transition-all ${
              blurEnabled
                ? "bg-purple-500 hover:bg-purple-600"
                : "bg-[var(--surface-light)] hover:bg-gray-700"
            }`}
            title={blurEnabled ? "Reveal yourself" : "Enable blur"}
          >
            <span className="text-xl">{blurEnabled ? "🙈" : "😊"}</span>
          </button>

          {/* End Call */}
          <button
            onClick={endCall}
            className="p-4 rounded-full bg-red-500 hover:bg-red-600 transition-all"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 8l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2M5 3a2 2 0 00-2 2v1c0 8.284 6.716 15 15 15h1a2 2 0 002-2v-3.28a1 1 0 00-.684-.948l-4.493-1.498a1 1 0 00-1.21.502l-1.13 2.257a11.042 11.042 0 01-5.516-5.517l2.257-1.128a1 1 0 00.502-1.21L9.228 3.683A1 1 0 008.28 3H5z" />
            </svg>
          </button>

          {/* Chat Link */}
          <Link
            href={`/chat/${matchId}`}
            className="p-4 rounded-full bg-[var(--surface-light)] hover:bg-gray-700 transition-all"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </Link>
        </div>

        {/* Blur Status */}
        <div className="text-center mt-3">
          <p className="text-sm text-gray-400">
            {blurEnabled
              ? "Your camera is blurred • Click 😊 to reveal"
              : "You're visible • Click 🙈 to blur"}
          </p>
        </div>
      </div>
    </main>
  );
}
