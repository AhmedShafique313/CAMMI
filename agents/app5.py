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

def generate_marketing_content(user_input: MarketingInput) -> str:
    agent_prompt = f"""
Role:
You are an Optimized Content Generator for B2B SaaS and SMB marketing platforms.

Purpose:
Generate complete, publish-ready marketing content using:
- User original content
- SEO keywords and hashtags
- Optimization suggestions

You are NOT brainstorming ideas.
You are producing final, usable content.

Inputs:
The document below contains:
- Original user content
- SEO keywords & hashtags
- Optimization suggestions

Document:
{user_input.output}

Your Task:
1. Generate ONE complete, optimized content set.
2. Content must be suitable for BOTH:
   - Blog post
   - Social media distribution

Each output MUST include:

- Title / Heading  
  Clear, compelling, SEO-aligned

- Description  
  2-5 sentences, intent-aligned, value-driven

- SEO Keywords  
  Primary and secondary keywords used naturally

- Hashtags  
  Relevant, non-stuffed, platform-appropriate

Guidelines:
- Follow the optimization suggestions strictly
- Maintain natural language (no keyword stuffing)
- Align with search intent (Informational, Commercial, or Transactional)
- Content must be execution-ready, not conceptual

Output Rules:
- No explanations
- No analysis
- No multiple options
- No headings like “Idea 1 / Idea 2”
- Return only the final content

Return output in this exact structure without headings:

<text>


<text>

- <keyword>
- <keyword>

- <hashtag>
- <hashtag>
"""

    response = client.models.generate_content(
        model="publishers/google/models/gemini-2.5-flash-lite",
        contents=agent_prompt,
    )

    return response.text or ""

if __name__ == "__main__":
    md_file_path = r"C:\Users\Kavtech AI Engineer\Downloads\Projects\CAMMI\agents\analyzed-suggestions.md"
    loaded_document = load_markdown_file(md_file_path)
    test_input = MarketingInput(
        output=loaded_document
    )
    context = generate_marketing_content(test_input)
    print(context)
