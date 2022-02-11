import logging
from typing import List

from .ProfileResultsObject import ProfileResultsObject
from .utils import *

logger = logging.getLogger(__name__)


class Profile(ProfileResultsObject):
    """Linkedin User Profile Object"""

    attributes = ['personal_info', 'experiences',
                  'skills', 'accomplishments', 'interests', 'recommendations']

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
        logger.info("Trying to determine the 'experiences' property")
        from collections import defaultdict
        experiences_dict = defaultdict(list)
        
        # dict.fromkeys(
        #     ['job_titles', 'employers', 'job_descriptions', 'employment_type', 'time_periods'], [])
        try:
            # TODO: better crawl this link: https://www.linkedin.com/in/nkaenzig/details/experience/ - should be much easier
            pvs_header_text = all_or_default(self.main_profile_soup, '.pvs-header__title')[2].span.text

            experience_list = self.experience_soup.select("div.pvs-entity.pvs-entity--padded.pvs-list__item--no-padding-when-nested")

            for exp in experience_list:
                exp_items = exp.select('div.display-flex.flex-column.full-width.align-self-center')

                if len(exp_items) == 1:
                    job_title = exp_items[0].select_one("div div span[class='t-bold mr1 '] span").get_text()
                    experiences_dict['job_titles'].append(job_title)

                    job_description = exp_items[0].select_one("div.pvs-list__outer-container span")
                    job_description = job_description.get_text() if job_description else None
                    experiences_dict['job_descriptions'].append(job_description)

                    employer = exp_items[0].select_one("span[class='t-14 t-normal'] span").get_text()
                    tmp = employer.split(' · ')
                    employment_type = None
                    if len(tmp) > 1:
                        employer = tmp[0]
                        employment_type = tmp[1]
                    experiences_dict['employers'].append(employer)
                    experiences_dict['job_descriptions'].append(employment_type)

                    time_period = exp_items[0].select_one("span[class='t-14 t-normal t-black--light'] span").get_text()
                    experiences_dict['time_periods'].append(time_period)
                else:
                    # TODO: handle companies with multiple positions`
                    pass

        except Exception as e:
            logger.exception(
                "Failed while determining experiences. Results may be missing/incorrect: %s", e)
        finally:
            return experiences_dict

    @property
    def skills(self):
        """
        Returns:
            list of skills {name: str, endorsements: int} in decreasing order of
            endorsement quantity.
        """
        logger.info("Trying to determine the 'skills' property")
        skills = self.main_profile_soup.select('.pv-skill-category-entity__skill-wrapper')
        skills = list(map(get_skill_info, skills))

        # Sort skills based on endorsements.  If the person has no endorsements
        def sort_skills(x): return int(
            x['endorsements'].replace('+', '')) if x['endorsements'] else 0
        return sorted(skills, key=sort_skills, reverse=True)

    @property
    def accomplishments(self):
        """
        Returns:
            dict of professional accomplishments including:
                - publications
                - cerfifications
                - patents
                - courses
                - projects
                - honors
                - test scores
                - languages
                - organizations
        """
        logger.info("Trying to determine the 'accomplishments' property")
        accomplishments = dict.fromkeys([
            'publications', 'certifications', 'patents',
            'courses', 'projects', 'honors',
            'test_scores', 'languages', 'organizations'
        ])
        try:
            container = one_or_default(
                self.main_profile_soup, '.pv-accomplishments-section')
            for key in accomplishments:
                accs = all_or_default(
                    container, 'section.' + key + ' ul > li')
                accs = map(lambda acc: acc.get_text() if acc else None, accs)
                accomplishments[key] = list(accs)
        except Exception as e:
            logger.exception(
                "Failed to get accomplishments, results may be incomplete/missing/wrong: %s", e)
        finally:
            return accomplishments

    @property
    def interests(self):
        """
        Returns:
            list of person's interests
        """
        logger.info("Trying to determine the 'interests' property")
        interests = []
        try:
            container = one_or_default(self.main_profile_soup, '.pv-interests-section')
            interests = all_or_default(container, 'ul > li')
            interests = list(map(lambda i: text_or_default(
                i, '.pv-entity__summary-title'), interests))
        except Exception as e:
            logger.exception("Failed to get interests: %s", e)
        finally:
            return interests

    @property
    def recommendations(self):
        logger.info("Trying to determine the 'recommendations' property")
        recs = dict.fromkeys(['received', 'given'], [])
        try:
            rec_block = one_or_default(
                self.main_profile_soup, 'section.pv-recommendations-section')
            received, given = all_or_default(
                rec_block, 'div.artdeco-tabpanel')
            for rec_received in all_or_default(received, "li.pv-recommendation-entity"):
                recs["received"].append(
                    get_recommendation_details(rec_received))

            for rec_given in all_or_default(given, "li.pv-recommendation-entity"):
                recs["given"].append(get_recommendation_details(rec_given))
        except Exception as e:
            logger.exception("Failed to get recommendations: %s", e)
        finally:
            return recs

    def to_dict(self):
        logger.info(
            "Attempting to turn return a dictionary for the Profile object.")
        return super(Profile, self).to_dict()
