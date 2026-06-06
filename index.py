import os
import json
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from openai import AsyncOpenAI

app = FastAPI(title="Social Media Content Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


class GenerateRequest(BaseModel):
    brand_name: str
    niche: str
    tone: str
    platforms: List[str]
    language: Optional[str] = "English"


@app.get("/")
async def root():
    return {"status": "ok", "message": "Social Media Content Generator API"}


@app.post("/generate")
async def generate(req: GenerateRequest):
    tone_map = {
        "fun": "playful, energetic, and witty with emojis",
        "professional": "formal, authoritative, and informative",
        "luxury": "elegant, exclusive, and aspirational",
        "motivational": "inspiring, uplifting, and empowering",
    }
    tone_desc = tone_map.get(req.tone.lower(), req.tone)
    platforms_str = ", ".join(req.platforms)
    num_platforms = len(req.platforms)
    posts_per_platform = max(1, 30 // num_platforms)

    system_prompt = (
        "You are an expert social media content strategist. "
        "You MUST respond with ONLY valid JSON — no markdown, no code fences, no extra text. "
        "The JSON must be parseable directly."
    )

    user_prompt = f"""Generate exactly 30 social media posts for the brand "{req.brand_name}" in the {req.niche} niche.
Tone: {tone_desc}
Platforms to rotate through: {platforms_str}
Language: {req.language}

Rules:
- Distribute the 30 posts evenly across platforms: {platforms_str}
- Each post must be tailored to its platform's best practices
- Day numbers go from 1 to 30 sequentially

Return ONLY this JSON structure (no markdown, no extra text):
{{
  "posts": [
    {{
      "day": 1,
      "platform": "Instagram",
      "caption": "engaging caption here",
      "hashtags": ["hashtag1", "hashtag2", "hashtag3"],
      "reels_script": "Line 1\\nLine 2\\nLine 3\\nLine 4\\nLine 5",
      "image_prompt": "detailed DALL-E image generation prompt"
    }}
  ]
}}

Generate all 30 posts now."""

    try:
        chat_response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.8,
            max_tokens=8000,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"OpenAI chat error: {str(e)}")

    raw = chat_response.choices[0].message.content.strip()

    # Strip markdown fences if present
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to parse GPT response as JSON: {str(e)}. Raw: {raw[:300]}",
        )

    posts = parsed.get("posts", [])
    if not posts:
        raise HTTPException(status_code=502, detail="No posts returned from GPT.")

    # Generate sample image from Day 1's image prompt
    day1_prompt = posts[0].get("image_prompt", f"Professional marketing image for {req.brand_name}")
    sample_image_url = None

    try:
        image_response = await client.images.generate(
            model="dall-e-3",
            prompt=day1_prompt,
            n=1,
            size="1024x1024",
            quality="standard",
        )
        sample_image_url = image_response.data[0].url
    except Exception as e:
        # Don't fail the whole request if image generation fails
        sample_image_url = f"Image generation failed: {str(e)}"

    return {
        "brand": req.brand_name,
        "posts": posts,
        "sample_image_url": sample_image_url,
    }
