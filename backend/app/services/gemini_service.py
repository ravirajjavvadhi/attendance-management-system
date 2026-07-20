import os
import json
import google.generativeai as genai
from typing import Dict, Any

def parse_timetable_image(image_bytes: bytes, mime_type: str) -> Dict[str, Any]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    
    genai.configure(api_key=api_key)
    
    # We use gemini-1.5-flash as it's the recommended model for multimodal tasks
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = """
    You are an AI that extracts timetable information from images and outputs structured JSON.
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
          { "period": 1, "subject_code": "CN" },
          { "period": 4, "break": true }
        ],
        "TUESDAY": [ ... ]
      }
    }
    
    Notes:
    - If a period is a break/lunch, set "break": true and omit "subject_code".
    - For subjects, try to match the short code (e.g. DAA) from the table grid to the full subject details list.
    - Day names in schedule must be UPPERCASE (MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY).
    """
    
    image_part = {
        "mime_type": mime_type,
        "data": image_bytes
    }
    
    response = model.generate_content([prompt, image_part])
    
    try:
        text = response.text
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
        print(f"Failed to parse Gemini response: {e}")
        print(f"Raw response: {response.text}")
        raise ValueError("Failed to extract timetable structure from the image")
