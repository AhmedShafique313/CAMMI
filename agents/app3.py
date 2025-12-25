from pydantic import BaseModel, Field
from google import genai
import os
from pathlib import Path

def load_markdown_file(file_path: str) -> str:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Markdown file not found: {file_path}")
    return path.read_text(encoding="utf-8")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\Kavtech AI Engineer\Downloads\Projects\CAMMI\image\service-account.json"

client = genai.Client(
    vertexai=True,
    project="lyrical-marker-474614-s5",
    location="us-central1",
)

class MarketingInput(BaseModel):
    output: str = Field(..., description="Generated campaign document output")

def generate_marketing_context(user_input: MarketingInput) -> str:
    agent_prompt = f"""
Role:
You are an expert B2B content strategist and ideation specialist for SaaS and SMB marketing platforms.

Goal:
From the provided campaign document, generate high-intent, search-optimized content ideas suitable for blogs, social posts, and landing pages.

Agent Backstory:
You specialize in converting marketing strategy and campaign briefs into actionable content ideas. Each idea must have a clear, concise, brand-aligned description that captures the target persona and search intent (Informational, Commercial, Transactional).

Task:
1. Analyze the campaign document below.
2. Generate up to 5 content ideas.
3. Each idea should include:
   - Heading (engaging, clear, ≤10 words)
   - Concise description** (2-4 sentences, precise, aligned with brand voice and tone)
4. Ensure all content ideas are actionable and suitable for cross-channel usage (blogs, social media, landing pages).

Document:
{user_input.output}

Return output in a clean, structured list.
"""

    response = client.models.generate_content(
        model="publishers/google/models/gemini-2.5-flash-lite",
        contents=agent_prompt,
    )

    return response.text or ""

if __name__ == "__main__":
    md_file_path = r"C:\Users\Kavtech AI Engineer\Downloads\Projects\CAMMI\agents\document.md"
    loaded_document = load_markdown_file(md_file_path)
    test_input = MarketingInput(
        output=loaded_document
    )
    context = generate_marketing_context(test_input)
    print(context)
