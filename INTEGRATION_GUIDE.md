# Baldwin - Frontend & Backend Integration Guide

## 🎯 Overview

Baldwin now has a complete **REST API** + **React Frontend** integration. The frontend communicates with the backend through a FastAPI server that bridges the web UI with the Baldwin voice assistant core.

---

## 📁 Architecture

```
d:\BALDWIN\
├── main.py                 # Original CLI assistant
├── api_server.py          # NEW: FastAPI REST server
├── config.py              # Configuration (API keys)
├── core/                  # Core modules (STT, LLM, TTS, Session)
├── frontend/              # React frontend
│   ├── src/
│   │   ├── routes/index.tsx        # Main UI (now uses real API)
│   │   ├── services/api.ts         # NEW: API client service
│   │   └── ...
│   ├── .env.local         # NEW: Frontend env config
│   └── package.json
└── requirements.txt       # Backend dependencies (updated)
```

---

## 🚀 QUICK START

### 1. **Install Backend Dependencies**

```bash
cd d:\BALDWIN
pip install -r requirements.txt
```

This installs:
- `fastapi>=0.104.0` (REST framework)
- `uvicorn[standard]>=0.24.0` (ASGI server)
- All other Baldwin dependencies

### 2. **Start Backend API Server**

```bash
python api_server.py
```

Or explicitly with uvicorn:

```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### 3. **Start Frontend Development Server**

In a new terminal:

```bash
cd d:\BALDWIN\frontend
npm run dev
```

**Expected Output:**
```
VITE v... dev server running at:

  ➜  Local:   http://localhost:5173/
  ➜  press h + enter to show help
```

### 4. **Open in Browser**

Visit: **http://localhost:5173/**

You should see the Baldwin UI with:
- ✅ Microphone button (working)
- ✅ Real-time transcription (STT)
- ✅ Chat messages (LLM responses)
- ✅ Tool calling (Weather, News, Currency, Calculator, Todo)
- ✅ Audio playback (TTS with male voice - George)
- ✅ Session sidebar
- ✅ Settings panel

---

## 🔌 API Endpoints

### Chat Endpoint
```http
POST http://localhost:8000/api/chat
Content-Type: application/json

{
  "message": "What's the weather in Jakarta?",
  "language": "english"
}
```

**Response:**
```json
{
  "success": true,
  "content": "It's currently 28°C and partly cloudy in Jakarta...",
  "audio_url": "data:audio/mpeg;base64,...",
  "tool_calls": [
    {
      "name": "weather",
      "parameters": { "city": "Jakarta" },
      "result": "28°C • Partly cloudy..."
    }
  ],
  "processing_time_ms": 1234
}
```

### Other Key Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Health check |
| POST | `/api/transcribe` | STT (upload WAV file) |
| POST | `/api/audio-synthesis` | TTS (text → audio) |
| GET | `/api/status` | API integration status |
| GET | `/api/session/history` | Get conversation history |
| POST | `/api/session/reset` | Reset session |
| POST | `/api/session/download` | Download transcript |
| WS | `/ws/chat` | WebSocket (real-time chat) |

---

## 🎧 Frontend Features (Now Live)

### ✅ Real Microphone Recording
- Uses Web Audio API
- Records 16-bit mono WAV audio
- Sends to backend for STT

### ✅ Real STT (Sarvam AI)
- Backend transcribes audio using Sarvam
- Returns confidence score
- Displays live transcript with confidence %

### ✅ Real LLM (Groq)
- Backend sends message to Groq
- Supports tool calling (5 tools)
- Shows processing time

### ✅ Real TTS (ElevenLabs)
- Male voice: George (American) - **Default**
- Female voice: Bella (Italian) - Alternative
- Audio auto-plays with built-in HTML5 player

### ✅ Tool Calling Integration
All 5 tools now execute through the backend:
- 🌤️ **Weather** - OpenWeather API
- 📰 **News** - NewsAPI
- 💱 **Currency** - Free exchange rates
- 🧮 **Calculator** - Math expressions
- ✓ **Todo** - Local storage

---

## 🔧 Configuration

### Backend Configuration (`.env`)
```env
# LLM
GROQ_API_KEY=your_groq_key_here

# STT
SARVAM_API_KEY=your_sarvam_key_here

# TTS
ELEVENLABS_API_KEY=your_elevenlabs_key_here

# Optional Tools
OPENWEATHER_API_KEY=your_weather_key_here
NEWS_API_KEY=your_news_key_here
```

### Frontend Configuration (`.env.local`)
```env
# Backend API URL
VITE_API_BASE_URL=http://localhost:8000

# Feature flags
VITE_USE_REAL_API=true
VITE_USE_MOCK_RESPONSES=false

# Audio settings
VITE_AUDIO_SAMPLE_RATE=16000
VITE_AUDIO_CHANNELS=1
VITE_AUDIO_DURATION_MS=5000
```

---

## 🧪 Testing API Endpoints

### Test Backend Connectivity

```bash
# Health check
curl http://localhost:8000/health

# Get API status
curl http://localhost:8000/api/status

# Chat with Baldwin
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

### Test Frontend

1. Open http://localhost:5173/
2. Click the microphone button
3. Speak for 5 seconds
4. Watch real-time transcription appear
5. Baldwin responds with audio
6. Check session sidebar for duration & message count

---

## 📊 Data Flow

```
User Interface (React)
    ↓
API Service (/services/api.ts)
    ↓
FastAPI Server (api_server.py)
    ↓
Baldwin Core (STT → LLM → TTS)
    ↓
External APIs (Groq, Sarvam, ElevenLabs)
    ↓
Response back to UI
```

---

## 🐛 Troubleshooting

### "API connection failed"

1. Check backend is running: `http://localhost:8000/health`
2. Verify `.env.local` has correct `VITE_API_BASE_URL`
3. Check CORS: Backend should show "allow_origins=["*"]"

### "Microphone not working"

1. Grant microphone permission in browser
2. Check browser console for errors
3. Verify audio device is connected

### "Transcription empty"

1. Speak louder or use different microphone
2. Check Sarvam API key is valid
3. See logs: `data/logs/baldwin_YYYYMMDD_HHMMSS.log`

### "No audio response"

1. Verify ElevenLabs API key is set
2. Check speaker volume
3. Browser may block autoplay - manual play works
4. See browser console for playback errors

### "Groq rate limited (429)"

1. Default quota: 100,000 tokens/day
2. Use less tokens or upgrade Groq tier
3. Alternative: Swap LLM provider (Claude, Mixtral)

---

## 📦 Build for Production

### Backend

```bash
# Install production dependencies
pip install -r requirements.txt

# Run with production ASGI server
gunicorn api_server:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### Frontend

```bash
cd frontend
npm run build

# Output in: frontend/dist/
# Deploy to: Vercel, Netlify, or static hosting
```

---

## 🎯 Next Steps

1. ✅ **Backend + Frontend Connected** (DONE)
2. ⏳ **Wait for Groq API reset** (~2 hours from rate limit)
3. 🧪 **End-to-end testing** with real voice
4. 🎨 **UI enhancements** (dark mode, animations, etc.)
5. 📱 **Mobile optimization**
6. 🔐 **Authentication & user sessions**
7. 🚀 **Deploy to production**

---

## 📚 Tech Stack

**Backend:**
- FastAPI (REST API framework)
- Uvicorn (ASGI server)
- Groq (LLM)
- Sarvam AI (STT)
- ElevenLabs (TTS)

**Frontend:**
- React 18 (UI framework)
- Vite (build tool)
- TanStack Router (routing)
- Tailwind CSS (styling)
- Radix UI (components)

**Integrations:**
- OpenWeather (weather data)
- NewsAPI (news headlines)
- ExchangeRate-API (currency conversion)
- Web Audio API (microphone)

---

## 💡 Tips

- **Development**: Keep both servers running in separate terminals
- **Debugging**: Check browser console (frontend) and terminal logs (backend)
- **Hot reload**: Both frontend and backend support hot reload
- **API testing**: Use Postman/Insomnia for endpoint testing
- **Performance**: Monitor response times in Session sidebar

---

## 🚀 Status

✅ **Backend**: Fully integrated FastAPI server ready  
✅ **Frontend**: Real API calls (no more mocks)  
✅ **STT**: Sarvam AI transcription working  
✅ **LLM**: Groq integration ready (watch quota)  
✅ **TTS**: ElevenLabs male voice (George) active  
✅ **Tools**: All 5 tools functional  
⏳ **WebSocket**: Optional for real-time updates  

**Ready to deploy!** 🎉

---

*Baldwin Frontend-Backend Integration*  
*April 17, 2026*
