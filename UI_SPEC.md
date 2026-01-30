# Mingle UI Specifications

## Overview

Mingle is a **privacy-first social matching platform** that connects users based on interests, not identities. The UI should feel modern, playful, and trustworthy.

---

## Design Principles

1. **Privacy First** - No photos by default, blur controls, anonymous profiles
2. **Playful & Modern** - Glassmorphism, gradients, micro-animations
3. **Dark Mode Default** - Easy on the eyes for night owls
4. **Mobile First** - Responsive, touch-friendly

---

## Color Palette

| Color | Hex | Use |
|-------|-----|-----|
| Primary | `#8B5CF6` | Buttons, accents |
| Secondary | `#06B6D4` | Highlights |
| Background | `#0F0F23` | Dark mode base |
| Surface | `#1A1A2E` | Cards, modals |
| Success | `#10B981` | Match found |
| Warning | `#F59E0B` | Alerts |
| Danger | `#EF4444` | Block, report |

---

## Pages

### 1. Landing Page (`/`)
- Hero with tagline: "Connect through interests, not appearances"
- How it works (3 steps)
- CTA: "Get Started"
- Footer with links

### 2. Onboarding (`/onboarding`)
**Step 1: Interests**
- Select 3-10 interests from categories (Gaming, Music, Sports, etc.)
- Search/filter interests

**Step 2: Vibe**
- Conversation style: Playful / Casual / Deep / Chill
- Energy level: Early Bird / Night Owl / Flexible

**Step 3: Preferences**
- Topics to avoid (optional)
- Languages spoken

### 3. Home/Dashboard (`/home`)
- Current mood selector (emoji buttons)
- "Find a Match" button (prominent)
- Active matches list
- Quick stats (conversations today, reputation)

### 4. Matching Queue (`/matching`)
- Animated searching state
- Compatibility percentage on match found
- Ice breaker prompt display
- Accept/Skip buttons

### 5. Chat (`/chat/:matchId`)
- Message bubbles (user vs partner)
- Typing indicator
- Reaction picker (emoji)
- Ice breaker button
- Video call button
- Report/Block menu
- Unmatch option

### 6. Video Chat (`/video/:matchId`)
- Main video (partner with optional blur)
- Self video (corner PiP)
- Blur toggle button
- Mute button
- End call button
- Chat overlay (optional)

### 7. Ice Breakers (`/icebreakers/:matchId`)
- Card-based UI for prompts
- Would You Rather with two buttons
- This or That with swipe
- Answer reveal animation

### 8. Profile Settings (`/settings`)
- Edit interests
- Change conversation style
- Blocked users list
- Account actions

### 9. Stats/Insights (`/insights`)
- Matches this week
- Best conversation times
- Top shared interests
- Reputation score

---

## Components

| Component | Description |
|-----------|-------------|
| `InterestChip` | Selectable tag with icon |
| `MoodSelector` | Row of emoji buttons |
| `MatchCard` | Shows compatibility %, shared interests |
| `ChatBubble` | Message with reactions |
| `VideoTile` | Video with blur overlay |
| `IceBreakerCard` | Game prompt with options |
| `CompatibilityMeter` | Animated percentage ring |

---

## User Flows

### Flow 1: First Match
```
Landing → Onboarding → Home → Find Match → 
Searching... → Match Found! → Chat → Ice Breaker → Video
```

### Flow 2: Returning User
```
Home → Active Matches → Continue Chat → Video Call
```

### Flow 3: Report User
```
Chat → Menu → Report → Select Reason → Submit → Confirmation
```

---

## States

### Matching States
- `idle` - Ready to find match
- `searching` - Looking for partner
- `found` - Match found, showing preview
- `chatting` - In active conversation
- `video` - Video call active

### Message States
- `sending` - Optimistic render
- `sent` - Delivered
- `moderated` - Flagged by system (blur + warning)

---

## Animations

1. **Match Found** - Confetti + pulse effect
2. **Compatibility Meter** - Count-up animation
3. **Typing Indicator** - Bouncing dots
4. **Video Blur** - Smooth gaussian transition
5. **Ice Breaker** - Card flip reveal

---

## Accessibility

- Keyboard navigation
- Screen reader labels
- High contrast mode option
- Reduced motion preference

---

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS + CSS Modules
- **State**: Zustand
- **WebSocket**: Socket.IO client
- **Video**: WebRTC native API
