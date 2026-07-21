import os
import json
import base64
from typing import Dict, Any
from groq import Groq

def parse_timetable_image(image_bytes: bytes, mime_type: str) -> Dict[str, Any]:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set")

    client = Groq(api_key=api_key)

    # Encode image to base64 for the API
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    prompt = """You are an AI that extracts timetable information from images and outputs structured JSON.
Analyze the provided timetable image and extract the following information.
Format your response STRICTLY as a JSON object matching this schema, without any markdown formatting (like ```json), just raw JSON:

{
  "department": "Name of the department if present",
  "section": "Section name (e.g. CSE-D)",
  "semester": "Semester/Year text (e.g. III B.Tech-I Semester)",
  "periods": [
    { "number": 1, "time": "9:30-10:30" }
  ],
  "subjects": [
    { "code": "CS501PC", "name": "Design and Analysis of Algorithms", "short": "DAA", "faculty": "Dr. K Raghupathi", "credits": 4 }
  ],
  "schedule": {
    "MONDAY": [
      { "period": 1, "subject_code": "DAA" },
      { "period": 4, "break": true }
    ],
    "TUESDAY": []
  }
}

Notes:
- If a period is a break/lunch, set "break": true and omit "subject_code".
- For subjects, try to match the short code (e.g. DAA) from the table grid to the full subject details list.
- Day names in schedule must be UPPERCASE (MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY).
- Only include days that appear in the timetable.
- Return ONLY the raw JSON, no explanation, no markdown."""

    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{image_b64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ],
        temperature=0,
        max_tokens=4096
    )

    try:
        text = response.choices[0].message.content.strip()
        # Clean up any potential markdown code blocks
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

        data = json.loads(text.strip())
        return data
    except Exception as e:
        print(f"Failed to parse Groq response: {e}")
        print(f"Raw response: {response.choices[0].message.content}")
        raise ValueError(f"Failed to extract timetable structure from the image: {e}")
