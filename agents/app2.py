from pydantic import BaseModel, Field
from google import genai
import os
from pathlib import Path

def load_markdown_file(file_path: str) -> str:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Markdown file not found: {file_path}")
    return path.read_text(encoding="utf-8")


# ---------- Set Google Cloud credentials ----------
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\Kavtech AI Engineer\Downloads\Projects\CAMMI\image\service-account.json"

# ---------- Initialize GenAI client ----------
client = genai.Client(
    vertexai=True,
    project="lyrical-marker-474614-s5",
    location="us-central1",
)


class MarketingInput(BaseModel):
    output: str = Field(..., description="Generated campaign document output")

# ---------- Function to generate marketing context ----------
def generate_marketing_context(user_input: MarketingInput) -> str:
    agent_prompt = f"""
Role:
You are an expert SEO strategist for B2B SaaS and SMB marketing platforms.
Goal:
Extract high-intent, search-optimized SEO keywords from the provided campaign document.

Agent Backstory:
You specialize in converting marketing strategy documents into
SEO-ready keyword sets aligned with search intent (Informational, Commercial, Transactional).

Task:
From the document below:
1. Generate (max 5 each):
   - Primary SEO keywords
   - Secondary keywords
   - Long-tail keywords
2. Group keywords by search intent (Informational, Commercial, Transactional), but return everything in a single flat list without headings or labels.
3. For each search intent, provide 5 relevant hashtags, also in the same flat list.
4. Ensure keywords are suitable for blogs, social content, and landing pages.

Document:
{user_input.output}

Return output in a clean, structured list.
"""

    response = client.models.generate_content(
        model="publishers/google/models/gemini-2.5-flash-lite",
        contents=agent_prompt,
    )

    return response.text or ""


# ---------- Example usage ----------
if __name__ == "__main__":
    md_file_path = r"C:\Users\Kavtech AI Engineer\Downloads\Projects\CAMMI\agents\document.md"
    loaded_document = load_markdown_file(md_file_path)
    test_input = MarketingInput(
        output=loaded_document
    )
    context = generate_marketing_context(test_input)
    print(context)
