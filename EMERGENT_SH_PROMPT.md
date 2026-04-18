## BALDWIN VOICE ASSISTANT - UI BUILD PROMPT for emergent.sh

### PROJECT OVERVIEW
Build a modern, interactive web UI for Baldwin - a personal voice assistant with real-time speech-to-text, AI responses, and text-to-speech features using ElevenLabs (male voice).

---

### CORE FEATURES

#### 1. RECORDING & TRANSCRIPTION PANEL
- **Microphone Button**
  - Large, centered circular button (on/off toggle)
  - Visual feedback: pulsing animation when recording
  - Display: "Listening..." status
  - Duration timer (shows seconds elapsed)
  - Waveform visualization during recording

- **Transcription Display**
  - Real-time text display as audio is being processed
  - Show confidence score (0-100%)
  - "Transcribing..." loading state
  - Display final transcription result

#### 2. CHAT CONVERSATION PANEL
- **Message History**
  - User messages aligned left (light background)
  - Baldwin responses aligned right (darker, accent color background)
  - Timestamps for each message
  - Differentiate tool calls with badge: [TOOL: currency_conversion]
  - Show response time: "⏱ 1.2s"

- **Message Features**
  - Avatar icons (user and Baldwin)
  - Markdown support for bold/italic text
  - Copy-to-clipboard button on each message
  - Auto-scroll to latest message

#### 3. AUDIO PLAYBACK
- **Response Audio Player**
  - Embedded audio player below Baldwin's response
  - Play/Pause button (prominent)
  - Progress bar showing playback progress
  - Volume control slider
  - Playback speed selector (0.75x, 1x, 1.5x, 2x)
  - Download MP3 button

#### 4. TOOL CALLING INDICATOR
- **Tool Execution Status**
  - Show when tools are called: "Fetching currency rates..."
  - Progress indicator (spinner/skeleton loading)
  - Tool result preview (before sending to LLM)
  - Tools displayed:
    - 🌤️ Weather (temperature, conditions)
    - 📰 News (headline preview)
    - 🧮 Calculator (equation → result)
    - 💱 Currency (exchange rates)
    - ✓ Todo (task management)

#### 5. SESSION SIDEBAR
- **Session Info Panel** (right side)
  - Session duration: "2 min 34 sec"
  - Total interactions: "7 messages"
  - Session ID/timestamp
  - Download session transcript button
  - Clear session button
  - Model info: "Groq llama-3.3-70b, ElevenLabs George"

#### 6. SETTINGS PANEL
- **Voice Settings**
  - Current voice: "George (Male, American)"
  - Change voice dropdown: [George | Bella]
  - Language selector: [English | Indonesian | Mixed]

- **STT Settings**
  - Language: [en-IN | hi-IN | auto-detect]
  - Confidence threshold: slider (0-100%)

- **API Status**
  - Green/Red indicator for Groq, Sarvam, ElevenLabs
  - Rate limit status: "Groq: 89,234/100,000 tokens"
  - Last sync: "Just now"

- **Recording Settings**
  - Mic device selector
  - Recording quality (Low/Normal/High)
  - Voice activity detection toggle

#### 7. HEADER/NAVIGATION
- **Top Bar**
  - Baldwin logo + name
  - Connected status indicator
  - Help/Documentation button (?)
  - Settings gear icon
  - Minimize/Fullscreen toggle

---

### DESIGN SPECIFICATIONS

#### Color Scheme
```
Primary (Baldwin): #2563eb (Blue)
Accent (George Voice): #1e40af (Dark Blue)
User Message: #f3f4f6 (Light Gray)
Baldwin Response: #dbeafe (Light Blue)
Success: #10b981 (Green)
Warning: #f59e0b (Amber)
Error: #ef4444 (Red)
Background: #ffffff (White)
Dark Background: #f9fafb (Very Light Gray)
```

#### Typography
- **Font Family**: "Inter", "Segoe UI", sans-serif
- **Headings**: Bold, 18-24px
- **Body**: Regular, 14-16px
- **Mono (Timestamps, IDs)**: "Courier New", monospace

#### Spacing & Layout
- **Max Width**: 1200px (responsive)
- **Gap**: 16px standard spacing
- **Padding**: 20px containers
- **Border Radius**: 8px (slightly rounded)

#### Animations
- Microphone button: Pulse effect when recording
- Messages: Fade-in (200ms)
- Loading states: Skeleton loaders
- Transitions: 300ms ease-in-out

---

### LAYOUT STRUCTURE

```
┌─────────────────────────────────────────────────────┐
│  Header: Baldwin Logo | Status | Settings          │
├──────────────────────┬────────────────────────────┤
│                      │                            │
│  Chat Messages       │  Session Sidebar          │
│  (scrollable)        │  - Duration              │
│                      │  - Total messages        │
│                      │  - Settings              │
│                      │                            │
├──────────────────────┴────────────────────────────┤
│  Recording Section                                 │
│  ┌─────────────────────────────────────────────┐  │
│  │  [Mic Button] "Listening..." [Timer]        │  │
│  │  Waveform Visualization                      │  │
│  │  Transcription: "Hello Baldwin..."           │  │
│  │  Audio Player [▶️ ▮▮▮▮▯▯▯ 2.3s 🔊]          │  │
│  └─────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────┘
```

---

### RESPONSIVE DESIGN
- **Desktop (>1024px)**: Full layout with sidebar
- **Tablet (768-1023px)**: Sidebar becomes modal/overlay
- **Mobile (<768px)**: Single column, collapsible sections

---

### TECHNICAL STACK RECOMMENDATIONS
- **Framework**: React.js (Next.js recommended for production)
- **Styling**: Tailwind CSS or CSS Modules
- **Audio**: Web Audio API + HTML5 Audio Element
- **Real-time Updates**: WebSocket or Server-Sent Events (SSE)
- **State Management**: React Context or Zustand
- **HTTP Client**: Axios or fetch API

---

### API INTEGRATION ENDPOINTS

#### Backend API URLs
```
POST /api/transcribe        - Send audio bytes, get transcription
POST /api/chat              - Send message, get LLM response
POST /api/audio-synthesis   - Send text, get MP3 audio
GET  /api/session           - Get current session info
GET  /api/status            - Get API status (Groq, Sarvam, ElevenLabs)
GET  /api/tools/{tool_name} - Get tool results
```

#### Expected Response Format
```json
{
  "success": true,
  "data": {
    "content": "Baldwin's response text",
    "audio_url": "data:audio/mpeg;base64,...",
    "tool_calls": [
      {
        "name": "convert_currency",
        "parameters": {"amount": 1, "from": "USD", "to": "IDR"},
        "result": "17,148.12 IDR"
      }
    ],
    "processing_time_ms": 1234
  }
}
```

---

### FEATURES TO IMPLEMENT

#### Phase 1: MVP (Essential)
- ✅ Microphone recording button
- ✅ Display transcription in real-time
- ✅ Show chat messages (user + Baldwin)
- ✅ Play audio responses
- ✅ Display session info
- ✅ Basic settings panel

#### Phase 2: Enhancement
- ✅ Tool calling visualization (weather, news, etc.)
- ✅ Download conversation transcript
- ✅ Multiple voice selection
- ✅ Waveform visualization
- ✅ API status indicator

#### Phase 3: Advanced
- ✅ Dark mode toggle
- ✅ Keyboard shortcuts (Start recording: Space)
- ✅ Audio file upload (instead of microphone)
- ✅ Conversation history/search
- ✅ User authentication (optional)

---

### USER INTERACTIONS

#### Main Flow
1. User opens UI → Sees empty chat with mic button
2. User clicks mic button → "Listening..." state
3. User speaks for ~5 seconds
4. Recording stops → Shows "Transcribing..." + spinner
5. Transcription appears → "You: Hello Baldwin..."
6. Show "Baldwin is thinking..." while LLM processes
7. Tool calls (if any) show as badges: "[TOOL: weather]"
8. Baldwin response appears → "Baldwin: I can help..."
9. Audio player appears below response
10. User can click play → Audio plays with visualization

#### Keyboard Shortcuts
- `Space` - Hold to record, release to stop
- `Ctrl+Enter` - Send text message (if text input)
- `Ctrl+K` - Open command palette (future)
- `Esc` - Close settings/modals

---

### ACCESSIBILITY REQUIREMENTS
- WCAG 2.1 AA compliance
- Keyboard navigation throughout
- Screen reader friendly labels
- High contrast mode support
- Focus indicators on interactive elements
- Alt text for icons
- ARIA labels for dynamic regions

---

### PERFORMANCE TARGETS
- Initial load: <2 seconds
- First message send: <3 seconds
- Message display: <100ms
- Audio playback: Immediate (<200ms)
- Responsive interactions: <16ms (60fps)

---

### MOBILE CONSIDERATIONS
- Touch-friendly button sizes (min 44x44px)
- No hover-only interactions
- Optimize microphone access on mobile
- Handle audio permissions gracefully
- Save bandwidth (compress audio if needed)

---

### ERROR HANDLING
- Network error recovery
- Missing audio device handling
- API rate limit warning
- Microphone permission denied flow
- Browser compatibility warnings
- Display user-friendly error messages

---

### LOGGING & ANALYTICS (Optional)
- Track session duration
- Count tool usage
- Monitor API response times
- Log errors and exceptions
- User interaction events

---

### DEPLOYMENT
- Build optimization (minimize bundle size)
- CDN for static assets
- Environment variables for API endpoints
- HTTPS required
- CORS configuration for API

---

### NOTES FOR EMERGENT.SH
1. This is a voice assistant UI - focus on audio interaction
2. Baldwin uses ElevenLabs for natural male voice (George)
3. Real-time transcription is critical
4. Tool calling (weather, currency, etc.) must show progress
5. Keep UI minimal and focused on conversation
6. Mobile responsiveness is important
7. Use modern web standards (HTML5 Audio API)

---

### REFERENCE INFORMATION
**Baldwin Backend Details:**
- STT: Sarvam AI (16kHz mono WAV, en-IN/hi-IN)
- LLM: Groq (llama-3.3-70b-versatile, tool calling enabled)
- TTS: ElevenLabs (George = male voice, Bella = female voice optional)
- Tools: Weather, News, Calculator, Currency Exchange, Todo List
- Language: Indonesian (id-ID) with English fallback

---

**Ready to build? Start with the chat interface and recording button, then add features incrementally!**
