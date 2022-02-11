from scrape_linkedin import ProfileScraper
from scrape_linkedin.utils import HEADLESS_OPTIONS
import json

LI_AT_COOKIE = "AQEDATnt7VcAtzJ-AAABfulgXNAAAAF_DWzg0E4AvgHCFPvrkW3A85XXQnIu7x7y0Exd62R5ctRsBki0riYVYJuFVx8ERl1s1OPtRY7BA7kayLwpnZLEM8_uD8KYkVdT_wPbO_XFpRCwcHon2Rrvw3Iz"

options = HEADLESS_OPTIONS
# options = dict()

user = 'austinoboyle'
with ProfileScraper(cookie=LI_AT_COOKIE, driver_options=options) as scraper:
    profile = scraper.scrape(user=user)

print(json.dumps(profile.to_dict()))

with open(f'data/output/{user}-profile.json', 'w', encoding='utf-8') as f:
    json.dump(profile.to_dict(), f, ensure_ascii=False, indent=2)