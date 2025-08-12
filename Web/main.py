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

# Optional: Filter only same-domain links
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
    print(f"[{idx}/{len(links)}] Scraping: {link}")
    page_content = scrape_page_content(link)
    all_content += f"\n\n--- Page: {link} ---\n{page_content}"

print("\n Data scraping completed.")

print(all_content)
