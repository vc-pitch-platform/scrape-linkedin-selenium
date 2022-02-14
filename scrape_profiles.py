from scrape_linkedin import ProfileScraper
from scrape_linkedin.utils import HEADLESS_OPTIONS
import argparse
import json
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='''Scrapes linked profiles and stores information in json files''')
    parser.add_argument('--profiles_file', type=str, help='File containing one Linkedin profile username or url per line. Should be put in the data/input/ directory!')
    args = parser.parse_args()


    LI_AT_COOKIE = os.getenv('LI_AT_COOKIE')
    HEADLESS = False

    if not LI_AT_COOKIE:
        raise Exception("Please define the environment variable LI_AT_COOKIE containing the LI_AT cookie value of the linkedin user used for scraping") 

    options = HEADLESS_OPTIONS if HEADLESS else dict() 

    with open(Path('data/input', args.profiles_file), 'r') as fp:
        profile_names_or_urls = fp.read().splitlines()

    output_dir = Path('data/output', Path(args.profiles_file).stem)
    output_dir.mkdir(parents=True, exist_ok=True)

    for i, p in enumerate(profile_names_or_urls): 
        print(f'Scraping {i+1}/{len(profile_names_or_urls)}: {p}')
        with ProfileScraper(cookie=LI_AT_COOKIE, driver_options=options, scroll_increment=250) as scraper:
            profile = scraper.scrape(user_or_url=p)

        with open(Path(output_dir, f'{i}-profile.json'), 'w', encoding='utf-8') as f:
            json.dump(profile.to_dict(), f, ensure_ascii=False, indent=2)