from scrape_linkedin import ProfileScraper
from scrape_linkedin.utils import HEADLESS_OPTIONS
import json
from dotenv import load_dotenv
import os

load_dotenv()

LI_AT_COOKIE = os.getenv('LI_AT_COOKIE')
HEADLESS = True

if not LI_AT_COOKIE:
    raise Exception("Please define the environment variable LI_AT_COOKIE containing the LI_AT cookie value of the linkedin user used for scraping") 

options = HEADLESS_OPTIONS if HEADLESS else dict() 

user = 'austinoboyle'
with ProfileScraper(cookie=LI_AT_COOKIE, driver_options=options) as scraper:
    profile = scraper.scrape(user_or_url=user)

print(json.dumps(profile.to_dict()))

with open(f'data/output/{user}-profile.json', 'w', encoding='utf-8') as f:
    json.dump(profile.to_dict(), f, ensure_ascii=False, indent=2)