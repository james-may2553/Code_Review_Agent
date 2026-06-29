REVIEW_PROMPT = """
You are a senior software engineer performing a code review.

Analyze the following code diff and identify:
- Bugs
- Security issues
- Performance problems
- Code quality issues
- Missing edge cases

Return ONLY valid JSON in this format:
{{
  "comments": [
    {{
      "file": "...",
      "line": 0,
      "severity": "low|medium|high",
      "issue": "...",
      "suggestion": "..."
    }}
  ]
}}

Code:
{code}
"""