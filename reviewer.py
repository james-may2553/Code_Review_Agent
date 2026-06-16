from dotenv import load_dotenv
import json
import os
from .prompts import REVIEW_PROMPT

load_dotenv()

def review_file(file_name: str, diff_chunk: str):
    mock = os.getenv("MOCK_REVIEW", "false")
    print(f"MOCK_REVIEW value: {mock}")  # 👈 ADD THIS

    if mock.lower() == "true":
        print("USING MOCK REVIEW")  # 👈 ADD THIS
        return [
            {
                "file": file_name,
                "line": 1,
                "severity": "medium",
                "issue": "Mock review issue for local testing.",
                "suggestion": "This confirms the pipeline works without calling the API."
            }
        ]

    prompt = REVIEW_PROMPT.format(code=diff_chunk)

    from openai import OpenAI
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-5",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content

    try:
        parsed = json.loads(content)
        for c in parsed["comments"]:
            c["file"] = file_name
        return parsed["comments"]
    except:
        return []