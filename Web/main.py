import os
from dotenv import load_dotenv
from hyperbrowser import Hyperbrowser
from hyperbrowser.models import StartScrapeJobParams, ScrapeOptions
from groq import Groq

load_dotenv(r"C:\Users\Kavtech AI Engineer\Documents\CAMMI\.env")
client_llm = Groq(api_key=os.getenv("GROQ_API_KEY"))
client_scraper = Hyperbrowser(api_key=os.getenv("HYPERBROWSER_API_KEY"))

website = input("Enter the website url: ").strip()

def scrape_links(url):
    result = client_scraper.scrape.start_and_wait(
        StartScrapeJobParams(
            url=url,
            scrape_options=ScrapeOptions(formats=['links'], only_main_content=True)
        )
    )
    return result.data.links

links = scrape_links(website)

links = [link for link in links if link.startswith(website)]

def scrape_page_content(url):
    result = client_scraper.scrape.start_and_wait(
        StartScrapeJobParams(
            url=url,
            scrape_options=ScrapeOptions(formats=['markdown'], only_main_content=True)
        )
    )
    return result.data.markdown or ""

all_content = ""
for idx, link in enumerate(links, start=1):
    # print(f"[{idx}/{len(links)}] Scraping: {link}")
    page_content = scrape_page_content(link)
    all_content += f"\n\n--- Page: {link} ---\n{page_content}"

str(all_content)

def call_llm(model_name, prompt, tokens):
    response = client_llm.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content" : str(prompt)}],
        temperature=1,
        max_completion_tokens=tokens
    )
    return response.choices[0].message.content.strip()

prompt_structuring = (
    f"""You are an expert information architect. 
    Convert the unstructure data {str(all_content)} into structured information dont remove any information just present it in a structured format.
    """)
token1 = 32768
structured_info = call_llm("llama-3.3-70b-versatile", prompt_structuring, token1)

prompt_relevancy = (
    f"""You are an expert business and marketing analyst specializing in B2B strategy.
    Review the following structured company information: {str(all_content)} 
    Your Task: 
    Extract only the information that is highly relevant for developing a B2B marketing strategy.
    Discard all irrelevant or redundant details.
    Return the answer in the exact format below, using the same headings exactly as written:
        Objective:
        Mission:
        Vision:
        Business Concept:
        Target Market:
        Value Proposition:
        Business Name:
        Products or Services they offer:
        Who they currently sell to:
        Top Business Goals:
        Challenges:
    Note:
    - Keep responses concise and fact-based.
    - Do not add new headings or commentary.
    - Do not include extra text outside this format.
    """)
token2 = 131072
relevant_info = call_llm("deepseek-r1-distill-llama-70b", prompt_relevancy, token2)

token3 = 8000

prompt_finalized = (
    f"""
    You are a professional business document formatter.
    Task:
    Take the following input data: {str(relevant_info)}
    Remove any content between <think> and </think>
    Present the information in a clean, professional document format.
    Required headings (exactly as written, in this order):
    Objective:
    Mission:
    Vision:
    Business Concept:
    Target Market:
    Value Proposition:
    Business Name:
    Products or Services they offer:
    Who they currently sell to:
    Top Business Goals:
    Challenges:

    Notes:
    Include only these headings and their corresponding information.
    f no information is available for a heading, write "Not specified".
    Do not use symbols like #, **, or bullet points.
    Do not add any extra commentary or text outside the headings and their content.
    Maintain proper spacing and readability.
    """)

finalized_output = call_llm("llama-3.1-8b-instant", prompt_finalized, token3)
print(finalized_output)