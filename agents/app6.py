from pydantic import BaseModel, Field
from google import genai
import os
from pathlib import Path
from langchain_community.tools import DuckDuckGoSearchRun

ddg_search = DuckDuckGoSearchRun()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\Kavtech AI Engineer\Downloads\Projects\CAMMI\image\service-account.json"

client = genai.Client(
    vertexai=True,
    project="lyrical-marker-474614-s5",
    location="us-central1",
)


class MarketingInput(BaseModel):
    company_description: str = Field(..., description="What do you do? Company/Product description")
    campaign_goal: str = Field(..., description="What's the goal? Awareness / Leads / Demo")
    campaign_theme: str = Field(..., description="What should we talk about? Topic or campaign theme")

def generate_marketing_context(user_input: MarketingInput) -> str:
    search_query = f"{user_input.campaign_theme} {user_input.company_description}"
    research_context = ddg_search.run(search_query)
    agent_prompt = f"""
Role:
You are a senior Trend Research Analyst specializing in B2B SaaS marketing platforms.

Primary Constraint (MANDATORY):
You must base your analysis ONLY on the DuckDuckGo search results provided below. Do NOT use prior knowledge, assumptions, or external information.

Search Source (Single Source of Truth):
The following content is the complete and only research input derived from a DuckDuckGo search
using the user's campaign theme and company description:
{research_context}

User Inputs (Contextual Metadata ONLY — do not research beyond this):
• Company / Product Description: {user_input.company_description}
• Campaign Goal: {user_input.campaign_goal}
• Campaign Theme: {user_input.campaign_theme}

Objective:
Extract and synthesize observable trend signals present in the provided search results.
Focus on what is being discussed, emphasized, or repeated — not opinions, strategies, or recommendations.

Analysis Tasks:
- Identify recurring topics, themes, and discussion patterns
- Classify each trend signal by visibility level:
  • Dominant Signal (appears repeatedly across multiple sources)
  • Recurring Signal (appears consistently but not universally)
  • Emerging Signal (appears infrequently or in early-stage discussions)

Language Constraints (MANDATORY):
- Describe observations only; do not evaluate or recommend
- Avoid outcome-oriented, promotional, or strategic language
- Use descriptive phrasing such as:
  “frequently mentioned as…”
  “commonly discussed in relation to…”
  “often framed as…”

Output Requirements:
- Return a flat, structured output
- Use clear section headings only
- Be concise.
- Do NOT generate posts, blogs, strategies, or promotional content
- Do NOT speculate beyond what is visible in the search data

Output Structure (STRICT):
Trend Signals & Hot Topics
- Dominant Signals
- Recurring Signals
- Emerging Signals

Quality Bar:
The output must be in the form of trend signals.
"""

    response = client.models.generate_content(
        model="publishers/google/models/gemini-2.5-flash-lite",
        contents=agent_prompt,
    )

    return response.text or ""

if __name__ == "__main__":
    test_input = MarketingInput(
        company_description="We provide AI marketing automation for SMBs.",
        campaign_goal="awareness",
        campaign_theme="AI-driven marketing efficiency"
    )
    context = generate_marketing_context(test_input)
    print(context)
