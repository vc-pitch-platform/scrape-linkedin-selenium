import logging
from typing import List

from .ProfileResultsObject import ProfileResultsObject
from .Experience import Experience
from .utils import *

logger = logging.getLogger(__name__)


class Profile(ProfileResultsObject):
    """Linkedin User Profile Object"""

    attributes = ['personal_info', 'experiences',
                  'skills']

    @property
    def personal_info(self):
        logger.info("Trying to determine the 'personal_info' property")
        """Return dict of personal info about the user"""
        personal_info = dict.fromkeys(['name', 'headline', 'company', 'school', 'location',
                                      'summary', 'image', 'followers', 'email', 'phone', 'connected', 'websites'])
        try:
            top_card = one_or_default(self.main_profile_soup, '.pv-top-card')
            contact_info = one_or_default(self.main_profile_soup, '.pv-contact-info')

            # Note that some of these selectors may have multiple selections, but
            # get_info takes the first match
            personal_info = {**personal_info, **get_info(top_card, {
                'name': 'h1',
                'headline': '.text-body-medium.break-words',
                'company': 'div[aria-label="Current company"]',
                'school': 'div[aria-label="Education"]',
                'location': '.text-body-small.inline.break-words',
            })}

            summary = text_or_default(
                self.main_profile_soup, '.pv-about-section', '').replace('... see more', '')

            personal_info['summary'] = re.sub(
                r"^About", "", summary, flags=re.IGNORECASE).strip()

            image_url = ''
            # If this is not None, you were scraping your own profile.
            image_element = one_or_default(
                top_card, 'img.profile-photo-edit__preview')

            if not image_element:
                image_element = one_or_default(
                    top_card, 'img.pv-top-card__photo')

            # Set image url to the src of the image html tag, if it exists
            try:
                image_url = image_element['src']
            except:
                pass

            personal_info['image'] = image_url

            activity_section = one_or_default(self.main_profile_soup,
                                              '.pv-recent-activity-section-v2')

            followers_text = ''
            if activity_section:
                logger.info(
                    "Found the Activity section, trying to determine follower count.")

                # Search for numbers of the form xx(,xxx,xxx...)
                follower_count_search = re.search(
                    r"[^,\d](\d+(?:,\d{3})*) followers", activity_section.text, re.IGNORECASE)

                if follower_count_search:
                    followers_text = follower_count_search.group(1)

                else:
                    logger.debug("Did not find follower count")
            else:
                logger.info(
                    "Could not find the Activity section. Continuing anyways.")

            personal_info['followers'] = followers_text
            personal_info.update(get_info(contact_info, {
                'email': '.ci-email .pv-contact-info__ci-container',
                'phone': '.ci-phone .pv-contact-info__ci-container',
                'connected': '.ci-connected .pv-contact-info__ci-container'
            }))

            personal_info['websites'] = []
            if contact_info:
                websites = contact_info.select('.ci-websites li a')
                websites = list(map(lambda x: x['href'], websites))
                personal_info['websites'] = websites
        except Exception as e:
            logger.exception(
                "Encountered error while fetching personal_info. Details may be incomplete/missing/wrong: %s", e)
        finally:
            return personal_info

    @property
    def experiences(self):
        """
        Returns:
            dict of person's professional experiences.  These include:
                - Jobs
                - Education
                - Volunteer Experiences
        """
        def extract_experience_properties(exp_item: bs4.element.Tag):
            job_title = exp_item.select_one("span.t-bold.mr1 span").get_text()
            job_description = exp_item.select_one("div.pvs-list__outer-container span")
            job_description = job_description.get_text() if job_description else None
            employment_period = exp_item.select_one("span[class='t-14 t-normal t-black--light'] span").get_text()
            tmp = exp_item.select("span[class='t-14 t-normal t-black--light']")
            if len(tmp) > 1:
                employment_period = tmp[0].span.get_text()
                location = tmp[1].span.get_text()
            else:
                employment_period = tmp[0].span.get_text()
                location = ''

            return Experience(employer=None, employment_type=None, job_title=job_title, job_description=job_description, employment_period=employment_period, location=location)

        logger.info("Trying to determine the 'experiences' property")

        experience_dicts = []
        
        try:
            experience_list = self.experience_soup.select("div.pvs-entity.pvs-entity--padded.pvs-list__item--no-padding-when-nested")

            for exp in experience_list:
                exp_items = exp.select('div.display-flex.flex-column.full-width.align-self-center')
                employment_type = None
                start_idx = 0

                if len(exp_items) == 1:
                    employer = exp_items[0].select_one("span[class='t-14 t-normal'] span").get_text()
                else:
                    employer = exp_items[0].select_one("span.t-bold.mr1 span").get_text()
                    start_idx = 1

                tmp = employer.split(' · ')
                if len(tmp) > 1:
                    employer = tmp[0]
                    employment_type = tmp[1]

                for i in range(start_idx, len(exp_items)):
                    experience_obj = extract_experience_properties(exp_items[i])
                    experience_obj.employer = employer
                    experience_obj.employment_type = employment_type
                    experience_dicts.append(experience_obj.__dict__)

        except Exception as e:
            logger.exception(
                "Failed while determining experiences. Results may be missing/incorrect: %s", e)
        finally:
            return experience_dicts

    @property
    def skills(self):
        """
        Returns:
            list of skills {name: str, endorsements: int} in decreasing order of
            endorsement quantity.
        """
        # TODO: hit show more results button
        return []


    def to_dict(self):
        logger.info(
            "Attempting to turn return a dictionary for the Profile object.")
        return super(Profile, self).to_dict()
