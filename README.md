# Social Media Content Generator API

FastAPI backend deployed on Vercel that generates 30 days of social media content using GPT-4o Mini and a sample image via DALL-E 3.

---

## Endpoints

### `GET /`
Health check — returns `{ "status": "ok" }`.

### `POST /generate`
**Request body:**
```json
{
  "brand_name": "Nike",
  "niche": "sportswear",
  "tone": "motivational",
  "platforms": ["Instagram", "Facebook", "LinkedIn"],
  "language": "English"
}
```

**Tone options:** `fun` | `professional` | `luxury` | `motivational`

**Response:**
```json
{
  "brand": "Nike",
  "posts": [
    {
      "day": 1,
      "platform": "Instagram",
      "caption": "...",
      "hashtags": ["#Nike", "#JustDoIt"],
      "reels_script": "Line 1\nLine 2\nLine 3",
      "image_prompt": "..."
    }
    // ... 30 items total
  ],
  "sample_image_url": "https://..."
}
```

---

## Local Development

```bash
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...
uvicorn api.index:app --reload
```

API will be live at `http://localhost:8000`

---

## Deploy to Vercel

### 1. Install Vercel CLI
```bash
npm i -g vercel
```

### 2. Add your OpenAI API key as a Vercel secret
```bash
vercel secrets add openai_api_key sk-your-key-here
```

### 3. Deploy
```bash
vercel --prod
```

### 4. Set environment variable in Vercel Dashboard
Go to **Project → Settings → Environment Variables** and add:
- Key: `OPENAI_API_KEY`
- Value: `sk-your-key-here`

> The `vercel.json` references `@openai_api_key` (a Vercel secret). You can also set it directly in the dashboard instead.

---

## Project Structure

```
.
├── api/
│   └── index.py       # FastAPI app (Vercel entry point)
├── requirements.txt   # Python dependencies
├── vercel.json        # Vercel config
└── README.md
```

---

## Notes

- GPT-4o Mini generates all 30 posts in one call for efficiency.
- DALL-E 3 generates **one** sample image using Day 1's image prompt.
- If image generation fails (quota, etc.), the error message is returned in `sample_image_url` instead of crashing the whole request.
- CORS is fully open (`allow_origins=["*"]`) so any frontend can call it.
