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

def analyzing_context(user_idea: str, user_input: MarketingInput) -> str:
    agent_prompt = f"""
Role:
You are a Senior SEO & Content Quality Auditor for B2B SaaS and SMB marketing platforms.

Objective:
Evaluate how well the provided content is optimized using the given SEO keywords and hashtags.
You MUST analyze only. Do NOT rewrite, improve, or suggest changes.

Analyze across:
- Keyword and hashtag relevance
- Search intent alignment (Informational / Commercial / Transactional)
- Semantic coverage and topical depth
- Keyword placement and natural usage
- Content clarity (heading + description)
- SEO hygiene (over-optimization, gaps)

Inputs:
SEO Keywords & Hashtags:
{user_input.output}

User Content:
{user_idea}

Scoring Instructions:
- Calculate one overall optimization percentage (0–100)
- Use weighted judgment:
  30% keyword coverage
  25% intent match
  20% semantic depth
  15% structure clarity
  10% SEO hygiene

Output Rules (IMPORTANT):
- Do NOT use headings
- Do NOT label sections
- Do NOT explain methodology
- Output must be clean, minimal, and flat

Return output in this exact order and style:

<overall_percentage>%

keyword coverage: <score>/100  
search intent match: <score>/100  
semantic depth: <score>/100  
content structure: <score>/100  
seo hygiene: <score>/100  

findings:
- <short insight>
- <short insight>

gaps:
- <gap or missing element>
- <gap or missing element>
"""
    response = client.models.generate_content(
        model="publishers/google/models/gemini-2.5-flash-lite",
        contents=agent_prompt,
    )
    return response.text or ""

    
def optimized_context(previous_model_output: str, user_idea: str) -> str:
    agent_prompt = f"""
Role:
You are a Senior SEO Content Optimization Strategist for B2B SaaS and SMB brands.

Objective:
Improve SEO and content effectiveness using ONLY the analysis provided.
Do NOT analyze again and do NOT generate final content.

Inputs:
Analysis Output:
{previous_model_output}

Original User Content:
{user_idea}

Output Rules (STRICT):
- Be concise
- No explanations
- No headings
- No scoring
- Suggestions only
- Include original content verbatim

Return output in this exact format:

original content:
"{user_idea}"

suggestions:
- <short actionable suggestion>
- <short actionable suggestion>
- <short actionable suggestion>
- <short actionable suggestion>

Focus on:
- keyword usage improvements
- intent alignment
- semantic/entity expansion
- on-page SEO clarity
"""
    response = client.models.generate_content(
        model="publishers/google/models/gemini-2.5-flash-lite",
        contents=agent_prompt,
    )
    return response.text or ""


if __name__ == "__main__":
    md_file_path = r"C:\Users\Kavtech AI Engineer\Downloads\Projects\CAMMI\agents\seo.md"
    user_idea = input("Enter heading + description:\n")
    loaded_document = load_markdown_file(md_file_path)
    test_input = MarketingInput(output=loaded_document)
    context = analyzing_context(user_idea, test_input)
    opt = optimized_context(context, user_idea)
    print("=== ANALYSIS OUTPUT ===")
    print(context)
    print("\n=== OPTIMIZATION PROMPTS ===")
    print(opt)

