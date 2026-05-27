from openai import AsyncOpenAI
import os

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def optimize_cost(input_data, cost_data):

    prompt = f"""
You are a construction cost optimization expert.

User Input:
{input_data}

Cost:
{cost_data}

Return ONLY JSON:

{{
  "summary": "...",
  "optimizations": [
    {{
      "action": "...",
      "estimated_savings": "₹X"
    }}
  ],
  "recommended_changes": [
    {{
      "change": "...",
      "impact": "..."
    }}
  ]
}}
"""

    res = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6
    )

    return res.choices[0].message.content