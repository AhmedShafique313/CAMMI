from pydantic import BaseModel, Field
from google import genai
import os
from langchain_community.tools import DuckDuckGoSearchRun

ddg_search = DuckDuckGoSearchRun()

# ---------- Set Google Cloud credentials ----------
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\Kavtech AI Engineer\Downloads\Projects\CAMMI\image\service-account.json"

# ---------- Initialize GenAI client ----------
client = genai.Client(
    vertexai=True,
    project="lyrical-marker-474614-s5",
    location="us-central1",
)

class MarketingInput(BaseModel):
    company_description: str = Field(..., description="What do you do? Company/Product description")
    campaign_goal: str = Field(..., description="What's the goal? Awareness / Leads / Demo")
    campaign_theme: str = Field(..., description="What should we talk about? Topic or campaign theme")

# ---------- Function to generate marketing context ----------
def generate_marketing_context(user_input: MarketingInput) -> str:
    search_query = f"{user_input.campaign_theme} {user_input.company_description}"
    research_context = ddg_search.run(search_query)
    agent_prompt = f"""
You are an expert Marketing Context Generator working inside an autonomous AI marketing system.
Your role is to act like a senior B2B growth strategist who combines market research, SEO knowledge,
and competitive analysis to prepare high-quality context for downstream content creation agents.
You do not write final content — you prepare the intelligence that enables it.

Your primary goal is to generate accurate, relevant, and actionable marketing context that helps
teams create blogs and social media posts that perform well in search, resonate with the target
audience, and differentiate from competitors.

You have access to real-world research signals. Use them carefully to ground your recommendations
in current trends, terminology, and competitive positioning.

Real-world research context:
{research_context}

User-provided campaign inputs:
• Company / Product Description: {user_input.company_description}
• Campaign Goal: {user_input.campaign_goal}
• Campaign Theme: {user_input.campaign_theme}

Your task:
Analyze the inputs and research context, then generate a structured marketing context that includes:

1. 8-12 SEO keywords relevant to the campaign theme and audience
2. 5-8 long-tail keywords reflecting high-intent or niche queries
3. 5-10 relevant and discoverable hashtags
4. Sample UTM-ready links for LinkedIn, X, and Instagram
5. Suggested hot or emerging topics suitable for content creation
6. Competitor insights or identifiable content gaps in the market
7. Practical notes that can guide content briefs for blogs or social posts

Present the output clearly, logically, and in a well-structured, readable format.
Focus on clarity, usefulness, and strategic value over verbosity.
"""

    response = client.models.generate_content(
        model="publishers/google/models/gemini-2.5-flash-lite",
        contents=agent_prompt,
    )

    return response.text or ""


# ---------- Example usage ----------
if __name__ == "__main__":
    test_input = MarketingInput(
        company_description="We provide AI marketing automation for SMBs.",
        campaign_goal="awareness",
        campaign_theme="AI-driven marketing efficiency"
    )

    context = generate_marketing_context(test_input)

    print(context)
