from hyperbrowser import Hyperbrowser
from hyperbrowser.models import StartScrapeJobParams, ScrapeOptions
from huggingface_hub import InferenceClient

client_scraper = Hyperbrowser(api_key="")

client = InferenceClient(
    provider="fireworks-ai",
    api_key=""
)

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
    page_content = scrape_page_content(link)
    all_content += f"\n\n--- Page: {link} ---\n{page_content}"

str(all_content)
def llm_calling(prompt):
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role":"user","content":str(prompt)}
        ]
    )
    return response.choices[0].message.content.strip()

prompt_structuring = (
    f"""You are an expert information architect. 
    Convert the unstructure data {str(all_content)} into structured information dont remove any information just present it in a structured format.
    """)
structured_info = llm_calling(prompt_structuring)

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
relevant_info = llm_calling(prompt_relevancy)
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
finalized_output = llm_calling(prompt_finalized)
print(finalized_output)