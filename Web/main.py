import os, json
from dotenv import load_dotenv
from hyperbrowser import Hyperbrowser
from hyperbrowser.models import StartScrapeJobParams, ScrapeOptions
from groq import Groq

load_dotenv(dotenv_path=r"C:\Users\Kavtech AI Engineer\Documents\CAMMI\.env")
client_llm = Groq(api_key=os.getenv("GROQ_API_KEY"))
client_scraper = Hyperbrowser(api_key=os.getenv("HYPERBROWSER_API_KEY"))
website = input("Enter the website url: ").strip()


def scrape_website(url):
    result = client_scraper.scrape.start_and_wait(
        StartScrapeJobParams(
            url=url,
            scrape_options=ScrapeOptions(formats=["markdown"])
        )
    )
    return result

system_prompt_1 = (
    "Read the entire unstructured scraped detail of the webpage and understand the information and convert it to the structured information"
)

markdown_data = scrape_website(website)

messages1 = [
    {"role": "system", "content": system_prompt_1},
    {"role": "user", "content": str(markdown_data)}
]

response_text1 = ""
print("\n Generating structured data...\n")

completion1 = client_llm.chat.completions.create(
    model="deepseek-r1-distill-llama-70b",
    messages=messages1,
    temperature=0.9,
    max_tokens=2048,
    top_p=1.0,
    stream=True
)

for chunk1 in completion1:
    if chunk1.choices[0].delta.content:
        response_text1 += chunk1.choices[0].delta.content
        print(chunk1.choices[0].delta.content, end="", flush=True)

# Save intermediate structured result
with open("structured_output.md", "w", encoding="utf-8") as f:
    f.write(response_text1)

# Step 2: Feed structured result into brand strategy prompt
prompt = (
    "You are a brand and marketing strategist. Based on the structured information below, analyze the company's brand. "
    "Start with a brief overview covering its mission, vision, and values. Identify the target audience, including demographics, "
    "psychographics, and industry. Define the Ideal Customer Profile (ICP) — their industry, company size, pain points, and goals. "
    "Describe the brand's voice and tone, highlighting how it communicates and the emotional feel of its messaging. Summarize the "
    "Unique Value Proposition (UVP) — what makes the brand stand out. Conclude with a high-level marketing strategy tailored to the ICP "
    "and UVP, suggesting channels, content types, and campaign ideas and do not provide the output in double quotations."
)

messages2 = [
    {"role": "system", "content": prompt},
    {"role": "user", "content": str(response_text1)}
]

response_text2 = ""
print("\n\n Generating marketing insights...\n")

completion2 = client_llm.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=messages2,
    temperature=0.9,
    max_tokens=2048,
    top_p=1.0,
    stream=True
)

for chunk2 in completion2:
    if chunk2.choices[0].delta.content:
        response_text2 += chunk2.choices[0].delta.content
        print(chunk2.choices[0].delta.content, end="", flush=True)

# Save final output
with open("final_output.md", "w", encoding="utf-8") as f:
    f.write(response_text2)

print("\n\n All results saved to MD files.")