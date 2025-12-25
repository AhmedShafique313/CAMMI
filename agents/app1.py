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
Role:
You are an expert Marketing Context Generator working inside an autonomous AI marketing system.
Goal:
Your goal is to transform minimal user input into a complete, structured marketing foundation.
You act as the strategic brain of the system, not the execution engine.

Agent Backstory:
You are a senior B2B marketing strategist with experience across SaaS, SMB, and enterprise markets.
Your expertise includes ICP definition, go-to-market strategy, positioning & messaging systems,
brand voice definition, and funnel-aligned planning. You specialize in producing deterministic,
execution-ready strategy from limited inputs.

Hard Constraints:
• Do NOT create blogs, social posts, ads, scripts, or copy.
• Do NOT describe product features unless unavoidable at a conceptual level.
• Do NOT use superlatives, hype language, or vague buzzwords.
• Do NOT broaden scope unnecessarily — prefer a single primary inference.
• All outputs must be reusable by downstream agents without reinterpretation.

Task:
Research Context (for factual grounding only, not expansion):
{research_context}

User Inputs (the ONLY allowed inputs):
• Company / Product Description: {user_input.company_description}
• Campaign Goal: {user_input.campaign_goal}
• Campaign Theme: {user_input.campaign_theme}

Task:
Using only the inputs above, generate FIVE strategic artifacts.
Outputs must be structured, internally consistent, deterministic, and content-agnostic.

1) Ideal Customer Profile (ICP)
Infer and define ONE primary ICP (optionally note secondary ICPs only if unavoidable).
Include:
- Industry / vertical (be specific or explicitly state “horizontal”)
- Company size (SMB / Mid-market / Enterprise)
- Buyer roles (decision-maker, influencer, user)
- Core pains & jobs-to-be-done
- Buying triggers
- Objections / adoption barriers
Requirement: concise, structured, directly actionable.

2) Content Strategy / Calendar (High-Level)
Design a strategy framework ONLY (no assets, no formats).
Include:
- Funnel stages (Awareness / Consideration / Decision)
- Content categories (e.g. educational, POV, decision-support — NOT formats like videos or webinars)
- Core themes & sub-themes derived strictly from the campaign theme
- High-level cadence (weekly / bi-weekly)
- Primary CTA aligned to the campaign goal
Do NOT create content or mention execution deliverables.

3) Strategic Marketing Plan (Campaign Level)
Define:
- Campaign objective (mapped exactly to the stated goal)
- Primary value proposition (specific, outcome-oriented)
- Channels (owned / earned / social)
- Funnel motion (how attention converts to action)
- Success metrics (KPIs aligned to the goal)
Must be execution-ready but content-agnostic.

4) Messaging Framework
Provide a reusable messaging system:
- Core positioning statement
- Primary message
- 3-4 supporting message pillars (outcome-based, not feature-based)
- Pain → Promise → Proof (proof as evidence types, not product features)
- CTA language aligned to the goal (non-salesy if awareness)
Must be directly reusable by blog and social agents.

5) Brand Identity (Inferred)
Infer a lightweight, operational brand identity:
- Brand personality (3-5 traits)
- Voice & tone rules
- What the brand should sound like
- What the brand should avoid
- Intended audience emotional state

write about brand tone and voice.
Do NOT invent visuals, colors, logos, or imagery.

Output Rules (Strict):
• Use clear section headers for all five artifacts
• Be structured, scannable, and deterministic
• No fluff, metaphors, or storytelling
• No emojis
• No unexplained marketing buzzwords
• No content generation of any kind
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
