# AI Ad Generator

A full-stack AI agent demo for Crowd Wisdom Trading. The backend uses FastAPI and Python agent classes. The frontend is a simple React app built with Vite.

The app can run fully offline with mock ads. When Apify environment variables are set, the ad-search agent calls Apify to fetch recent Meta-style ads, normalizes the dataset items, ranks the best working ads, and saves the results to JSON.

## Architecture

```text
React UI
   |
   | POST /generate-ad
   v
FastAPI backend
   |
   | Apify Actor/Task or mock fallback
   v
SuccessfulAdSearchAgent
   |
   | saves working_ads.json and apify_raw_ads.json
   v
MarketingInsightAgent
   |
   | extracts pain points, angles, concepts
   v
GDriveDataAgent
   |
   | Google Drive JSON or local product data
   v
AdScriptAgent
   |
   | writes 60-second ad script
   v
VideoCreativeAgent
   |
   | creates image prompt, voice asset, subtitles, Remotion props
   v
JSON response -> React UI
```

## Project Structure

```text
.
|-- backend/
|   |-- agents/
|   |   |-- ad_search.py
|   |   |-- apify_fetch.py
|   |   |-- gdrive_data.py
|   |   |-- insight_extractor.py
|   |   |-- pipeline.py
|   |   |-- script_writer.py
|   |   |-- video_creator.py
|   |   `-- __init__.py
|   |-- data/
|   |   |-- mock_successful_ads.json
|   |   `-- unique_product_data.json
|   |-- __init__.py
|   `-- main.py
|-- frontend/
|   |-- src/
|   |   |-- main.jsx
|   |   |-- styles.css
|   |   `-- remotion/
|   |       |-- AdVideo.jsx
|   |       `-- index.jsx
|   |-- index.html
|   |-- package.json
|   |-- remotion.config.js
|   `-- vite.config.js
|-- .env.example
|-- Procfile
|-- README.md
`-- requirements.txt
```

## Apify Integration

The backend uses `backend/agents/apify_fetch.py`.

It supports either:

```text
APIFY_META_ADS_ACTOR_ID=owner~actor-name
```

or:

```text
APIFY_META_ADS_TASK_ID=your-task-id
```

If a task ID is set, it takes priority over actor ID. This is useful when you have a saved Apify task already configured for Meta Ads Library scraping. Actor mode sends the product URL and niche as run input. Task mode uses the saved Apify task input, because Apify's synchronous task dataset endpoint is a GET endpoint.

Create a `.env` in the project root or set environment variables based on `.env.example`:

```text
APIFY_TOKEN=your_apify_token
APIFY_META_ADS_ACTOR_ID=your_meta_ads_actor_id
APIFY_META_ADS_TASK_ID=
APIFY_TIMEOUT_SECONDS=120
APIFY_MAX_ITEMS=25
```

The app calls Apify's synchronous dataset-items endpoint and sends product/niche search input. Returned items are normalized into:

```json
{
  "brand": "...",
  "hook": "...",
  "ad_text": "...",
  "cta": "...",
  "started_at": "YYYY-MM-DD",
  "spend": 0,
  "engagement": 0,
  "impressions": 0,
  "platform": "Meta Ads",
  "url": "...",
  "apify_ad_id": "..."
}
```

Saved files:

```text
backend/data/apify_raw_ads.json
backend/data/working_ads.json
backend/data/generated_campaign.json
```

Without Apify credentials, the pipeline automatically uses `backend/data/mock_successful_ads.json`.

## Run Locally

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

Install backend dependencies:

```bash
pip install -r requirements.txt
```

Install frontend dependencies:

```bash
cd frontend
npm install
```

Build the React UI:

```bash
npm run build
cd ..
```

Run the full app from the project root:

```bash
uvicorn backend.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

For React dev mode:

```bash
cd frontend
npm run dev
```

Set this if the frontend runs separately:

```text
VITE_API_URL=http://127.0.0.1:8000
```

## API

### GET `/apify-status`

Returns whether Apify is configured and which target type is being used.

### POST `/generate-ad`

Request:

```json
{
  "product_url": "https://crowdwisdomtrading.com",
  "niche": "trading research and market signals",
  "days": 30,
  "limit": 5,
  "force_mock": false
}
```

Response includes:

```json
{
  "ad_source": "apify",
  "apify": {},
  "used_mock_fallback": false,
  "selected_ads": [],
  "pain_points": [],
  "marketing_angles": [],
  "concepts": [],
  "ad_script": "...",
  "video_plan": {},
  "saved_files": {}
}
```

## Other Integrations

```text
GDRIVE_DATA_URL=public_json_url_from_google_drive
GOOGLE_DRIVE_FILE_ID=public_google_drive_file_id
ELEVENLABS_API_KEY=your_elevenlabs_key
ELEVENLABS_VOICE_ID=your_voice_id
```

Current fallback behavior:

```text
Apify missing        -> uses backend/data/mock_successful_ads.json
Google Drive missing -> uses backend/data/unique_product_data.json
ElevenLabs missing   -> saves backend/media/voiceover.txt
Image generation     -> returns a Pollinations image URL prompt
Remotion             -> saves backend/media/remotion_input.json
```

## Deploy On Render

Use one web service if you want FastAPI to serve the built React UI.

```text
Build Command: pip install -r requirements.txt && cd frontend && npm install && npm run build
Start Command: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

Add the Apify and other API keys in Render environment variables.

## Deploy On Railway

Use the same start command:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

Build the frontend before deployment or deploy `frontend` as a separate static app.

## Render The Video Later

After running the agent flow:

```bash
cd frontend
npm run render:ad
```

This uses `backend/media/remotion_input.json` as the Remotion props file.
