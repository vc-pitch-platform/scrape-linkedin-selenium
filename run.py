from scrape_linkedin import ProfileScraper
from scrape_linkedin.utils import HEADLESS_OPTIONS

LI_AT_COOKIE = "AQEDATnt7VcDMTGTAAABfuSkgSwAAAF_CLEFLE0AJjClBx7Ja8SuUxJvscJWTGrxTYtifohSttPBrH1dblNuj-xxIMycpXkeGq9YRq0COrNCvVqs-npAMIpjSn5JgQRZ94HbfEBqfdYtG18D-cV7iZko"

options = HEADLESS_OPTIONS
# options = dict()

with ProfileScraper(cookie=LI_AT_COOKIE, driver_options=options) as scraper:
    profile = scraper.scrape(user='austinoboyle')
print(profile.to_dict())