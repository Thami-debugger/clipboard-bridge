# Clipboard Bridge

Free instant clipboard sync between devices using room codes.

## Features
- 🔒 Secure room-based system
- 🚀 Real-time WebSocket sync
- 📱 Works on any device with a browser
- 🆓 100% free, no login required
- ⏱️ Rooms expire after 24 hours

## How to Use
1. Open the app on your PC
2. Click "Create New Room" - you'll get a 6-character code
3. Open the app on your phone
4. Enter the same room code
5. Start copying text - it syncs instantly!

## Deploy Your Own (Free)

### Option 1: Railway
1. Fork this repo
2. Go to [railway.app](https://railway.app)
3. Click "New Project" → "Deploy from GitHub repo"
4. Select this repo
5. Done! Railway will auto-detect and deploy

### Option 2: Render
1. Fork this repo
2. Go to [render.com](https://render.com)
3. Click "New Web Service"
4. Connect your GitHub repo
5. Build command: `pip install -r requirements.txt`
6. Start command: `uvicorn server:app --host 0.0.0.0 --port $PORT`

### Option 3: Fly.io
```bash
fly launch
fly deploy
```

## Run Locally
```bash
pip install -r requirements.txt
uvicorn server:app --reload
```

Open http://localhost:8000

## Tech Stack
- **Backend**: FastAPI + WebSockets
- **Frontend**: Vanilla JavaScript
- **No database needed** - runs entirely in memory

## License
MIT - Feel free to use and modify!
