# AI Ad Generator

A minimal full-stack AI agent demo for Crowd Wisdom Trading. The backend uses FastAPI and simulated CrewAI-style Python agents. The frontend is a simple React app built with Vite.

## Architecture

```text
React frontend
   |
   | POST /generate-ad
   v
backend/ FastAPI app
   |
   | Apify adapter or backend/data/mock_successful_ads.json
   v
SuccessfulAdSearchAgent
   |
   | saves backend/data/working_ads.json
   v
MarketingInsightAgent
   |
   | pain points + marketing angles + concepts
   v
GDriveDataAgent
   |
   | Google Drive JSON or backend/data/unique_product_data.json
   v
AdScriptAgent
   |
   | 60-second ad script
   v
VideoCreativeAgent
   |
   | Remotion-ready plan + voice text + subtitles
   v
JSON Response -> React UI
```

## Project Structure

```text
.
├── backend/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── ad_search.py
│   │   ├── gdrive_data.py
│   │   ├── insight_extractor.py
│   │   ├── pipeline.py
│   │   ├── script_writer.py
│   │   └── video_creator.py
│   ├── data/
│   │   ├── mock_successful_ads.json
│   │   └── unique_product_data.json
│   ├── __init__.py
│   └── main.py
├── frontend/
│   ├── src/
│   │   ├── main.jsx
│   │   ├── styles.css
│   │   └── remotion/
│   │       ├── AdVideo.jsx
│   │       └── index.jsx
│   └── index.html
├── Procfile
├── README.md
└── requirements.txt
```

## Run Locally

1. Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the backend:

```bash
uvicorn backend.main:app --reload
```

4. Start the React frontend in a second terminal:

```bash
cd frontend
npm install
npm run dev
```

5. Open the app:

```text
http://127.0.0.1:5173
```

The backend runs at `http://127.0.0.1:8000`.

## API

### POST `/generate-ad`

Runs the full agent flow and returns:

```json
{
  "pain_points": ["..."],
  "marketing_angles": ["..."],
  "concepts": ["..."],
  "ad_script": "...",
  "video_plan": {}
}
```

## Optional Integrations

The demo works without keys by using local mock data. Add these environment variables when you are ready to connect live services:

```text
APIFY_TOKEN=your_apify_token
APIFY_META_ADS_ACTOR_ID=your_meta_ads_actor_id
GDRIVE_DATA_URL=public_json_url_from_google_drive
GOOGLE_DRIVE_FILE_ID=public_google_drive_file_id
ELEVENLABS_API_KEY=your_elevenlabs_key
ELEVENLABS_VOICE_ID=your_voice_id
```

Current behavior:

```text
Apify missing        -> uses backend/data/mock_successful_ads.json
Google Drive missing -> uses backend/data/unique_product_data.json
ElevenLabs missing   -> saves backend/media/voiceover.txt
Image generation     -> returns a Pollinations image URL prompt
Remotion             -> saves backend/media/remotion_input.json and provides npm run render:ad
```

## Deploy On Render

1. Push this project to a GitHub repository.
2. Create a new Web Service on Render.
3. Connect the repository.
4. Use these settings:

```text
Build Command: pip install -r requirements.txt
Start Command: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

Render can also use the included `Procfile`. For the React frontend, either deploy `frontend` as a separate static site or build it before deployment and serve the generated `frontend/dist` from FastAPI.

## Deploy On Railway

1. Push this project to GitHub.
2. Create a new Railway project from the repository.
3. Railway will install dependencies from `requirements.txt`.
4. Use this start command if needed:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

## Render The Video Later

After running the agent flow and installing frontend dependencies:

```bash
cd frontend
npm run render:ad
```

This uses `backend/media/remotion_input.json` as the Remotion props file.
